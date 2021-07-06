#include <Python.h>
#include <string>
#include <vector>
#include <map>
#include <exception>
#include <cstring>
#include "picojson.h"

static bool debug_py2pico = false;

/**
 * Convert Python compound object to picojson
 */
picojson::value pyobject_to_picojson(PyObject *pyobj) {

  if (pyobj == Py_None) {
    // is None
    if (debug_py2pico) std::cerr << "is none." << std::endl;
    return picojson::value();
  }

  if (PyBool_Check(pyobj)) {
    // is a boolean value
    if (debug_py2pico) std::cerr << "is bool." << std::endl;
    return picojson::value((pyobj == Py_True));
  }

  if (PyLong_Check(pyobj)) {
    // is a long integer value
    if (debug_py2pico) std::cerr << "is long." << std::endl;
    return picojson::value(PyLong_AsLong(pyobj));
  }

  if (PyFloat_Check(pyobj)) {
    // is a floating point value
    if (debug_py2pico) std::cerr << "is float." << std::endl;
    return picojson::value(PyFloat_AsDouble(pyobj));
  }
  
  if (PyBytes_Check(pyobj)) {
    // is_a string object
    if (debug_py2pico) std::cerr << "is string." << std::endl;
    const std::string cstr(PyBytes_AsString(pyobj));
    return picojson::value(cstr);
  }

  if (PyUnicode_Check(pyobj)) {
    // is_a unicode object
    if (debug_py2pico) std::cerr << "is unicode." << std::endl;
    const std::string cstr = PyBytes_AsString(PyUnicode_AsUTF8String(pyobj));
    return picojson::value(cstr);
  }

  if (PyTuple_Check(pyobj)) {
    // is_a tuple object
    picojson::array pico_ary;
    PyObject *item;

    if (debug_py2pico) std::cerr << "is tupple." << std::endl;
    for (Py_ssize_t i = 0; i < PyTuple_Size(pyobj); i++) {
      item = PyTuple_GetItem(pyobj, i);
      pico_ary.push_back(pyobject_to_picojson(item));
    }

    return picojson::value(pico_ary);
  }

  if (PyList_Check(pyobj)) {
    // is_a list object
    picojson::array pico_ary;
    PyObject *item;

    if (debug_py2pico) std::cerr << "is list." << std::endl;
    for (Py_ssize_t i = 0; i < PyList_Size(pyobj); i++) {
      item = PyList_GetItem(pyobj, i);
      pico_ary.push_back(pyobject_to_picojson(item));
    }

    return picojson::value(pico_ary);
  }
  
  if (PyDict_Check(pyobj)) {
    // is_a dictionary object
    picojson::object pico_obj;
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    std::string key_str;
    
    if (debug_py2pico) std::cerr << "is dictionary." << std::endl;
    while (PyDict_Next(pyobj, &pos, &key, &value)) {
      if (PyBytes_Check(key)) {
	key_str = std::string(PyBytes_AsString(key));
      } else if (PyUnicode_Check(key)) {
	key_str = std::string(PyBytes_AsString(PyUnicode_AsUTF8String(key)));
      } else {
	PyErr_SetString(PyExc_RuntimeError, "The key-object of the dictionary object is neither bytes- nor unicode- object.");
	return picojson::value();
      }
      picojson::value value_pico = pyobject_to_picojson(value);
      pico_obj.insert(std::make_pair(key_str, value_pico));
    }

    return picojson::value(pico_obj);
  }

  if (debug_py2pico) {
    std::cerr << "is unknown. " << std::endl;
  }

  PyErr_SetString(PyExc_RuntimeError, "The object is not a supported type.");
  return picojson::value();
}

/**
 * Convert picojson object to Python compound object
 */

PyObject * picojson_to_pyobject(const picojson::value& pico_v) {

  if (pico_v.is<picojson::null>()) {
    // is null
    return Py_None;
  }

  if (pico_v.is<bool>()) {
    // is a boolean value
    if (pico_v.get<bool>()) {
      return Py_True;
    }
    return Py_False;
  }

  if (pico_v.is<long>()) {
    // is a long integer value
    return PyLong_FromLong(pico_v.get<long>());
  }

  if (pico_v.is<double>()) {
    // is a double floating point value
    return PyFloat_FromDouble(pico_v.get<double>());
  }

  if (pico_v.is<std::string>()) {
    // is a string value
    const char* str_ptr = pico_v.get<std::string>().c_str();
    return PyUnicode_DecodeUTF8(str_ptr, strlen(str_ptr), NULL);
  }

  if (pico_v.is<picojson::array>()) {
    // is an array value
    picojson::array pico_ary = pico_v.get<picojson::array>();
    Py_ssize_t len = pico_ary.size();
    PyObject *pylist = PyList_New(len);

    for (Py_ssize_t i = 0; i < len; i++) {
      PyList_SetItem(pylist, i, picojson_to_pyobject(pico_ary[i]));
    }
    
    return pylist;
  }

  if (pico_v.is<picojson::object>()) {
    // is an object value
    picojson::object pico_obj = pico_v.get<picojson::object>();
    PyObject *pydict = PyDict_New();

    picojson::object::const_iterator it;
    for (it = pico_obj.begin(); it != pico_obj.end(); ++it) {
      const char* str_ptr = it->first.c_str();
      PyObject *key = PyUnicode_DecodeUTF8(str_ptr, strlen(str_ptr), NULL);
      PyObject *val = picojson_to_pyobject(it->second);

      PyDict_SetItem(pydict, key, val);
    }

    return pydict;
  }
  
  PyErr_SetString(PyExc_RuntimeError, "The object is not a supported type.");
  return Py_None;
}
