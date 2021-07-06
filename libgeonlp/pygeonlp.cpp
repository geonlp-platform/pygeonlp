#include <Python.h>
#include <cstdio>
#include "GeonlpMA.h"

/*
For creation of C-Exteion, refer;
- https://docs.python.org/3/extending/newtypes_tutorial.html

For the error handling and the built-in exceptions, see;
- https://docs.python.org/3.9/c-api/exceptions.html#standard-exceptions
- https://docs.python.org/3.9/c-api/exceptions.html#standard-exceptions
*/

picojson::value pyobject_to_picojson(PyObject *);
PyObject* picojson_to_pyobject(const picojson::value&);

/**
 * Define GeonlpMA Object
 */

typedef struct {
  PyObject_HEAD
  geonlp::MAPtr _ptrObj;
} GeonlpMA;

static void __alter_geonlpid_fieldname(geonlp::Geoword& geoword) {
  // Replace field name 'geonlp_id' with 'geolod_id' in the geoword
  geoword.set_value("geolod_id", geoword._get_string("geonlp_id"));
  geoword.erase("geonlp_id");
}

static int geonlp_ma_init(GeonlpMA *self, PyObject *args, PyObject *kwds)
// Initializetion function of GeoNLP Morphological Analyser object
{
  PyObject *pyobj;
  const char *dict_dir = NULL;

  PyArg_ParseTuple(args, "O", &pyobj);

  if (PyUnicode_Check(pyobj)) {
    dict_dir = PyUnicode_AsUTF8AndSize(pyobj, NULL);
    try {
      self->_ptrObj = geonlp::createMA(dict_dir);
    }
    catch (geonlp::ServiceCreateFailedException& e) {
      PyErr_SetString(PyExc_RuntimeError, e.what());
    }
    return 0;
  }
  
  if (!PyDict_Check(pyobj)) {
    PyErr_SetString(PyExc_RuntimeError, "The parameter must be a string (dict_dir) or a dict object (settings).");
    return 0;
  }

  picojson::value options = pyobject_to_picojson(pyobj);
  try {
    self->_ptrObj = geonlp::createMA(options);
  }
  catch (geonlp::ServiceCreateFailedException& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return 0;

  /*
  PyArg_ParseTuple(args, "s|s", &dict_dir, &profile);

  try {
    if (profile != NULL) {
      self->_ptrObj = geonlp::createMA(dict_dir, profile);
    }
    else {
      self->_ptrObj = geonlp::createMA(dict_dir);
    }
  }
  catch (geonlp::ServiceCreateFailedException& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  catch (std::runtime_error& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }

  return 0;
  */
}

static void geonlp_ma_dealloc(GeonlpMA *self)
// Destruct the object
{
  if (self->_ptrObj) {
    self->_ptrObj.reset();
  }
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject * geonlp_ma_parse(GeonlpMA *self, PyObject *args)
// Parse the sentence and return a formatted text
{
  char* str;

  PyArg_ParseTuple(args, "s", &str);
  std::string result = (self->_ptrObj)->parse(str);
  return Py_BuildValue("s", result.c_str(), 1);
}

static PyObject * geonlp_ma_parse_node(GeonlpMA *self, PyObject *args)
// Parse the sentence and return list of objects
{
  char* str;

  PyArg_ParseTuple(args, "s", &str);

  std::vector<geonlp::Node> ret;
  try {
    Py_ssize_t n = (Py_ssize_t) (self->_ptrObj)->parseNode(str, ret);
    PyObject *pylist = PyList_New(n);

    for (Py_ssize_t i = 0; i < n; i++) {
      picojson::object pico_obj = ret[i].toObject();
      picojson::value v(pico_obj);
      PyList_SetItem(pylist, i, picojson_to_pyobject(v));
    }

    return pylist;
  } catch (std::exception & e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

static PyObject * geonlp_ma_get_word_info(GeonlpMA *self, PyObject *args)
// Get attributes of geo-words from their geonlp_id list.
{
  char* str;

  PyArg_ParseTuple(args, "s", &str);
  try {
    picojson::ext json_obj;
    geonlp::Geoword geoword;
    if ((self->_ptrObj)->getGeowordEntry(str, geoword)) {
      __alter_geonlpid_fieldname(geoword);
      return picojson_to_pyobject(geoword);
    }
    return Py_None;
  } catch (geonlp::ServiceRequestFormatException &e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

static PyObject * geonlp_ma_search_word(GeonlpMA *self, PyObject *args)
// Search the dictionary by word spelling or reading.
{
  char* str;

  PyArg_ParseTuple(args, "s", &str);
  try {
    picojson::ext json_obj;
    std::map<std::string, geonlp::Geoword> results;
    (self->_ptrObj)->getGeowordEntries(str, results);
    for (std::map<std::string, geonlp::Geoword>::iterator it = results.begin();
	 it != results.end(); it++) {
      __alter_geonlpid_fieldname((*it).second);
      json_obj.set_value((*it).first, (*it).second);
    }
    return picojson_to_pyobject(json_obj);
  } catch (geonlp::ServiceRequestFormatException& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  } catch (geonlp::IndexNotExistsException& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

static PyObject * geonlp_ma_list_dictionary(GeonlpMA *self, PyObject *args)
// List installed dictionaries
{
  try {
    picojson::ext json_obj;
    std::map<int, geonlp::Dictionary> dicts;
    (self->_ptrObj)->getDictionaryList(dicts);
    for (std::map<int, geonlp::Dictionary>::iterator it = dicts.begin();
	 it != dicts.end(); it++) {
      std::stringstream ss;
      std::string dict_id;
      ss << (*it).first;
      ss >> dict_id;
      json_obj.set_value(dict_id, (*it).second);
    }
    return picojson_to_pyobject(json_obj);
  } catch (geonlp::ServiceRequestFormatException& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

static PyObject * geonlp_ma_get_dictionary_info(GeonlpMA *self, PyObject *args)
// Get attributes of dictionary specified by its ID
{
  PyObject *pyobj;

  PyArg_ParseTuple(args, "O", &pyobj);

  try {
    picojson::ext json_obj;
    geonlp::Dictionary dict;
    if (PyLong_Check(pyobj)) {
      long int dict_id = PyLong_AsLong(pyobj);
      if ((self->_ptrObj)->getDictionaryById(dict_id, dict)) {
	return picojson_to_pyobject(dict);
      }
      return Py_None;
    } else if (PyUnicode_Check(pyobj)) {
      const std::string cstr = PyBytes_AsString(PyUnicode_AsUTF8String(pyobj));
      if ((self->_ptrObj)->getDictionary(cstr, dict)) {
	return picojson_to_pyobject(dict);
      }
      return Py_None;
    }
    PyErr_SetString(PyExc_TypeError, "Param must be a int or str value.");
  } catch (geonlp::ServiceRequestFormatException& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

static PyObject * geonlp_ma_get_active_dictionaries(GeonlpMA *self, PyObject *args)
// Get active dictionaries as a list of dictionary id (int)
{
  picojson::ext json_obj;
  const std::map<int, geonlp::Dictionary>& dicts
    = (self->_ptrObj)->getActiveDictionaries();
  for (std::map<int, geonlp::Dictionary>::const_iterator it = dicts.begin();
       it != dicts.end(); it++) {
    std::stringstream ss;
    std::string dict_id;
    ss << (*it).first;
    ss >> dict_id;
    json_obj.set_value(dict_id, (*it).second);
  }
  return picojson_to_pyobject(json_obj);
}

static PyObject * geonlp_ma_set_active_dictionaries(GeonlpMA *self, PyObject *args)
// Set active dictionaries by a list of dictionary id (int)
{
  std::vector<int> dic_ids;
  PyObject *pyobj;
  if (!PyArg_ParseTuple(args, "O", &pyobj)) {
    PyErr_SetString(PyExc_TypeError, "Param must be a list of int.");
    return NULL;
  }
  if (!PyList_Check(pyobj)) {
    PyErr_SetString(PyExc_TypeError, "Param must be a list of int.");
    return NULL;
  }
  
  PyObject *iter = PyObject_GetIter(pyobj);
  if (!iter) {
    PyErr_SetString(PyExc_TypeError, "Param must be a list of int.");
    return NULL;
  }
  while (true) {
    PyObject *next = PyIter_Next(iter);
    if (!next) break;
    if (!PyLong_Check(next)) {
      PyErr_SetString(PyExc_TypeError, "Param must be a list of int values.");
      return NULL;
    }
    dic_ids.push_back(int(PyLong_AsLong(next)));
  }
  (self->_ptrObj)->setActiveDictionaries(dic_ids);
  return Py_None;
}

static PyObject * geonlp_ma_get_active_classes(GeonlpMA *self, PyObject *args)
// Get active classes as a list of class names
{
  const std::vector<std::string>& ne_classes
    = (self->_ptrObj)->getActiveClasses();
  Py_ssize_t len = ne_classes.size();

  PyObject *pylist = PyList_New(len);
  for (Py_ssize_t i = 0; i < len; i++) {
    PyList_SetItem(pylist, i, PyUnicode_DecodeUTF8(ne_classes[i].c_str(), ne_classes[i].length(), NULL));
  }
  return pylist;
}

static PyObject * geonlp_ma_set_active_classes(GeonlpMA *self, PyObject *args)
// Set active classes by a list of class names
{
  std::vector<std::string> ne_classes;
  PyObject *pyobj;
  if (!PyArg_ParseTuple(args, "O", &pyobj)) {
    PyErr_SetString(PyExc_TypeError, "Param must be a list of str.");
    return NULL;
  }

  PyObject *iter = PyObject_GetIter(pyobj);
  if (!iter) {
    PyErr_SetString(PyExc_TypeError, "Param must be a list of str.");
    return NULL;
  }
  while (true) {
    PyObject *next = PyIter_Next(iter);
    if (!next) break;
    if (PyBytes_Check(next)) {
      ne_classes.push_back(std::string(PyBytes_AsString(next)));
    } else if (PyUnicode_Check(next)) {
      ne_classes.push_back(std::string(PyUnicode_AsUTF8AndSize(next, NULL)));
    }
  }
  (self->_ptrObj)->setActiveClasses(ne_classes);
  return Py_None;
}

static PyObject * geonlp_ma_clear_database(GeonlpMA *self, PyObject *args)
{
  try {
    (self->_ptrObj)->clearDatabase();
    return Py_True;
  } catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

static PyObject * geonlp_ma_add_dictionary(GeonlpMA *self, PyObject *args)
{
  char* jsonfile = NULL;
  char* csvfile = NULL;

  PyArg_ParseTuple(args, "ss", &jsonfile, &csvfile);
  
  try {
    (self->_ptrObj)->addDictionary(jsonfile, csvfile);
    return Py_True;
  } catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

static PyObject * geonlp_ma_remove_dictionary(GeonlpMA *self, PyObject *args)
{
  char* identifier = NULL;

  PyArg_ParseTuple(args, "s", &identifier);
  
  try {
    (self->_ptrObj)->removeDictionary(identifier);
    return Py_True;
  } catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

static PyObject * geonlp_ma_update_index(GeonlpMA *self, PyObject *args)
{
  try {
    (self->_ptrObj)->updateIndex();
    return Py_True;
  } catch (std::exception &e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

static PyObject * geonlp_ma_get_dictionary_identifier_by_id(GeonlpMA *self, PyObject *args)
{
  long dic_id;
  PyArg_ParseTuple(args, "l", &dic_id);
  try {
    std::string identifier;
    identifier = (self->_ptrObj)->getDictionaryIdentifierById(dic_id);
    if (identifier.length() == 0) {
      PyErr_SetString(PyExc_RuntimeError, "No dictionary has the id.");
    }
    return PyUnicode_DecodeUTF8(identifier.c_str(), identifier.length(), NULL);
  } catch (std::runtime_error& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
  }
  return NULL;
}

// GeonlpMA object methods
static PyMethodDef GeonlpMAMethods[] = {
  {"parse", (PyCFunction)geonlp_ma_parse, METH_VARARGS, "Parse the sentence and return a formatted text."},
  {"parseNode", (PyCFunction)geonlp_ma_parse_node, METH_VARARGS, "Parse the sentece and return list of dict."},
  {"getWordInfo", (PyCFunction)geonlp_ma_get_word_info, METH_VARARGS, "Get word information."},
  {"searchWord", (PyCFunction)geonlp_ma_search_word, METH_VARARGS, "Search word by its spelling or reading."},
  {"getDictionaryList", (PyCFunction)geonlp_ma_list_dictionary, METH_NOARGS, "Get installed dictionary list."},
  {"getDictionaryInfo", (PyCFunction)geonlp_ma_get_dictionary_info, METH_VARARGS, "Get dictionary information."},
  {"getActiveDictionaries", (PyCFunction)geonlp_ma_get_active_dictionaries, METH_NOARGS, "Get active dictionaries."},
  {"setActiveDictionaries", (PyCFunction)geonlp_ma_set_active_dictionaries, METH_VARARGS, "Set active dictionaries."},
  {"getActiveClasses", (PyCFunction)geonlp_ma_get_active_classes, METH_NOARGS, "Get active NE classes."},
  {"setActiveClasses", (PyCFunction)geonlp_ma_set_active_classes, METH_VARARGS, "Set active NE classes."},
  {"clearDatabase", (PyCFunction)geonlp_ma_clear_database, METH_NOARGS, "Clear database."},
  {"addDictionary", (PyCFunction)geonlp_ma_add_dictionary, METH_VARARGS, "Add a dictionary to the database by importing files containing JSON metadata and CSV data."},
  {"removeDictionary", (PyCFunction)geonlp_ma_remove_dictionary, METH_VARARGS, "Remove the dictionary from the database specified by its identifier."},
  {"updateIndex", (PyCFunction)geonlp_ma_update_index, METH_NOARGS, "Update index of the database."},
  {"getDictionaryIdentifierById", (PyCFunction)geonlp_ma_get_dictionary_identifier_by_id, METH_VARARGS, "Get dictionary identifier from its internel id."},
  {NULL, NULL, 0, NULL} // Sentinel
};

/**
 * Define module
 */

static PyObject * geonlp_module_version(PyObject *self)
// Get the version string
{
  return Py_BuildValue("s", PACKAGE_VERSION, 1);
}

static PyMethodDef GeonlpModuleMethods[] = {
  {"version", (PyCFunction)geonlp_module_version, METH_NOARGS, "Show the version"},
  {NULL, NULL, 0, NULL} // Sentinel
};

static struct PyModuleDef GeonlpModule = {
  PyModuleDef_HEAD_INIT,
  "capi", // m_name
  NULL,     // m_doc
  -1,       // m_size
  GeonlpModuleMethods, // m_methods
  NULL,     // m_slots
  NULL,     // m_traverse
  NULL,     // m_clear
  NULL      // m_free
};

/**
 * Initialization
 */

PyMODINIT_FUNC
PyInit_capi (void)
// Create the module 'capi'
{

  // GeonlpMAType object
  static PyTypeObject GeonlpMAType = {
    PyVarObject_HEAD_INIT(NULL, 0)
  };
  GeonlpMAType.tp_name = "capi.ma";
  GeonlpMAType.tp_new = PyType_GenericNew;
  GeonlpMAType.tp_basicsize = sizeof(GeonlpMA);
  GeonlpMAType.tp_dealloc = (destructor) geonlp_ma_dealloc;
  GeonlpMAType.tp_flags = Py_TPFLAGS_DEFAULT;
  GeonlpMAType.tp_doc = "GeoNLP morphological analyzer objects";
  GeonlpMAType.tp_methods = GeonlpMAMethods;
  GeonlpMAType.tp_init = (initproc) geonlp_ma_init;

  if (PyType_Ready(&GeonlpMAType) < 0)
    return NULL;
  
  PyObject* m;  // the module object

  // Create module
  m = PyModule_Create(&GeonlpModule);
  if (m == NULL)
    return NULL;

  // Add GeonlpMA Object to the module
  Py_INCREF(&GeonlpMAType);
  PyModule_AddObject(m, "MA", (PyObject *)&GeonlpMAType);
  
  return m;
}
