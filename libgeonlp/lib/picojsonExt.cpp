///
/// @file
/// @brief PicoJSON 拡張クラスの実装
/// @author 相良 毅 sagara@info-proto.com
///
/// Copyright (c)2013, InfoProto Co.,Ltd.
///
#include <sstream>
#include "picojsonExt.h"

namespace picojson
{

  ext::ext() {
    initByJson("{}");
  }

  void ext::set_value(const std::string& key, const picojson::value& v) {
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, v));
  }
  
  void ext::set_value(const std::string& key, const ext& v) {
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, v._v));
  }

  void ext::_set_null(const std::string& key) {
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, picojson::value()));
  }
  
  void ext::_set_bool(const std::string& key, bool b) {
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, picojson::value(b)));
  }
  
  void ext::_set_string(const std::string& key, const std::string& vstring) {
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, picojson::value(vstring)));
  }

  void ext::_set_string_list(const std::string& key, const std::string& vstring, const boost::regex& separator) {
    boost::sregex_token_iterator it(vstring.begin(), vstring.end(), separator, -1);
    boost::sregex_token_iterator end_of_seq;
    picojson::array varray;
    boost::match_results<std::string::const_iterator> what;

    while (it != end_of_seq) {
      varray.push_back(picojson::value(*it));
      it++;
    }
    std::string tail = std::string(vstring.end() - 1, vstring.end());
    if (boost::regex_search(vstring.end() - 1, vstring.end(), what, separator, boost::match_default)) {
      varray.push_back(picojson::value(std::string("")));
    }
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, varray));
  }

  void ext::_set_string_list(const std::string& key, const std::vector<std::string>& vstrings) {
    picojson::array varray;
    for (std::vector<std::string>::const_iterator it = vstrings.begin(); it != vstrings.end(); it++) {
      varray.push_back(picojson::value(*it));
    }
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, varray));
  }

  void ext::_set_string_map(const std::string& key, const std::string& vstring, const boost::regex& item_separator, const boost::regex& pair_pattern) {
    boost::sregex_token_iterator it(vstring.begin(), vstring.end(), item_separator, -1);
    boost::sregex_token_iterator end_of_seq;
    picojson::object vobject;

    while (it != end_of_seq) {
      std::string pair_str = (*it);
      for (boost::sregex_iterator it2 = boost::make_regex_iterator(pair_str, pair_pattern); it2 != boost::sregex_iterator(); it2++) {
	vobject.insert(std::make_pair((*it2)[1], picojson::value((*it2)[2])));
      }
      it++;
    }
    
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, vobject));
  }

  void ext::_set_string_map(const std::string& key, const std::map<std::string, std::string>& vmap) {
    picojson::object vobject;
    for (std::map<std::string, std::string>::const_iterator it = vmap.begin(); it != vmap.end(); it++) {
      vobject.insert(std::make_pair((*it).first, picojson::value((*it).second)));
    }
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, vobject));
  }

  void ext::_set_int(const std::string& key, int vint) {
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, picojson::value((long)vint)));
  }
  
  void ext::_set_int_list(const std::string& key, const std::vector<int>& values) {
    picojson::array varray;
    for (std::vector<int>::const_iterator it = values.begin(); it != values.end(); it++) {
      varray.push_back(picojson::value((long)*it));
    }
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, varray));
  }

  void ext::_set_double(const std::string& key, double vdouble) {
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, picojson::value(vdouble)));
  }
  
  void ext::_set_double_list(const std::string& key, const std::vector<double>& values) {
    picojson::array varray;
    for (std::vector<double>::const_iterator it = values.begin(); it != values.end(); it++) {
      varray.push_back(picojson::value(*it));
    }
    this->_v.get<picojson::object>().erase(key);
    this->_v.get<picojson::object>().insert(std::make_pair(key, varray));
  }

  // picojson オブジェクトのキーリストを取得する
  std::vector<std::string> ext::get_keys() const {
    std::vector<std::string> keys;
    const picojson::object& o = this->_v.get<picojson::object>();
    for (picojson::object::const_iterator it = o.begin(); it != o.end(); it++) {
      keys.push_back((*it).first);
    }
    return keys;
  }

  // picojson オブジェクトから、指定したキーの値を picojson::value として取得する
  picojson::value ext::get_value(const std::string& key) const {
    picojson::object o = this->_v.get<picojson::object>();
    const picojson::value v = o[key];
    return v;
  }

  // picojson オブジェクトから、指定したキーの値を文字列として取得する
  // キーが存在しない場合は "" を返す
  // 値が object, array 型の場合は PicojsonException 例外を発生する
  std::string ext::_get_string(const std::string& key) const {
    const picojson::value v0 = this->get_value(key);
    if (!v0) return std::string("");
    if (v0.is<std::string>() || v0.is<long>() || v0.is<double>()) return v0.to_str();
    std::stringstream sstr;
    sstr << "'" << key << "' must be a string.";
    throw PicojsonException(sstr.str());
  }

  // picojson オブジェクトから、指定したキーの値を文字列の配列として取得する
  // キーが存在しない場合は [] を返す
  // 値が object, double 型の場合は PicojsonException 例外を発生する
  // 値が string 型の場合は要素数１の文字列配列を返す
  std::vector<std::string> ext::_get_string_list(const std::string& key) const {
    const picojson::value v0 = this->get_value(key);
    picojson::value v1;
    std::vector<std::string> varray;
    varray.clear();
    std::stringstream sstr;
    sstr << "'" << key << "' must be a list of string value.";

    if (v0.is<picojson::null>()) {
      return varray;
    } else if (v0.is<std::string>()) {
      varray.push_back(v0.to_str());
      return varray;
    } else if (v0.is<picojson::array>()) {
      picojson::array v = v0.get<picojson::array>();
      for (picojson::array::iterator it = v.begin(); it != v.end(); it++) {
	if ((*it).is<picojson::null>() || (*it).is<bool>()) {
	  varray.push_back("");
	} else if ((*it).is<std::string>()) {
	  varray.push_back((*it).to_str());
	} else {
	  throw PicojsonException(sstr.str());
	}
      }
      return varray;
    }
    throw PicojsonException(sstr.str());
  }

  // picojson オブジェクトから、指定したキーの値を文字列のハッシュとして取得する
  // キーが存在しない場合は [] を返す
  // 値が array, double, string 型の場合は PicojsonException 例外を発生する
  std::map<std::string, std::string> ext::_get_string_map(const std::string& key) const {
    const picojson::value v0 = this->get_value(key);
    picojson::value v1;
    std::map<std::string, std::string> varray;
    varray.clear();
    std::stringstream sstr;
    sstr << "'" << key << "' must be a map of string value.";

    if (v0.is<picojson::null>()) {
      return varray;
    } else if (v0.is<picojson::object>()) {
      picojson::object v = v0.get<picojson::object>();
      for (picojson::object::iterator it = v.begin(); it != v.end(); it++) {
	if ((*it).second.is<picojson::null>() || (*it).second.is<bool>()) {
	  varray.insert(std::make_pair((*it).first, std::string("")));
	} else if ((*it).second.is<std::string>()) {
	  varray.insert(std::make_pair((*it).first, (*it).second.to_str()));
	} else {
	  throw PicojsonException(sstr.str());
	}
      }
      return varray;
    }
    throw PicojsonException(sstr.str());
  }

  // picojson オブジェクトの指定したキーの値が null かどうか判定する
  // null の場合、およびキーが存在しない場合は true を返す
  // それ以外の場合は false を返す
  bool ext::is_null(const std::string& key) const {
    const picojson::value v0 = this->get_value(key);
    if (!v0 || v0.is<picojson::null>()) return true;
    return false;
  }

  // picojson オブジェクトから、指定したキーの値を bool 値として取得する
  // キーが存在しない場合は false を返す
  // 値が int, object, array, string 型の場合は PicojsonException 例外を発生する
  bool ext::_get_bool(const std::string& key) const {
    const picojson::value v0 = this->get_value(key);
    if (!v0) return false;
    if (v0.is<bool>()) return v0.get<bool>();
    std::stringstream sstr;
    sstr << "'" << key << "' must be a boolean value.";
    throw PicojsonException(sstr.str());
  }

  // picojson オブジェクトから、指定したキーの値を整数値として取得する
  // キーが存在しない場合は 0 を返す
  // 値が object, array, string 型の場合は PicojsonException 例外を発生する
  int ext::_get_int(const std::string& key) const {
    const picojson::value v0 = this->get_value(key);
    if (!v0) return 0;
    if (v0.is<long>()) return (int)(v0.get<long>());
    if (v0.is<double>()) return (int)(v0.get<double>());
    std::stringstream sstr;
    sstr << "'" << key << "' must be an integer value.";
    throw PicojsonException(sstr.str());
  }

  // picojson オブジェクトから、指定したキーの値を整数値の配列として取得する
  // キーが存在しない場合は [] を返す
  // 値が object, string 型の場合は PicojsonException 例外を発生する
  // 値が int 型の場合は要素数１の整数値配列を返す
  std::vector<int> ext::_get_int_list(const std::string& key) const {
    const picojson::value v0 = this->get_value(key);
    picojson::value v1;
    std::vector<int> varray;
    varray.clear();
    std::stringstream sstr;
    sstr << "'" << key << "' must be a list of int value.";

    if (v0.is<picojson::null>()) {
      return varray;
    } else if (v0.is<long>()) {
      varray.push_back((int)(v0.get<long>()));
      return varray;
    } else if (v0.is<double>()) {
      varray.push_back((int)(v0.get<double>()));
      return varray;
    } else if (v0.is<picojson::array>()) {
      picojson::array v = v0.get<picojson::array>();
      for (picojson::array::iterator it = v.begin(); it != v.end(); it++) {
	if ((*it).is<picojson::null>() || (*it).is<bool>()) {
	  varray.push_back(0);
	} else if ((*it).is<long>()) {
	  varray.push_back((int)((*it).get<long>()));
	} else if ((*it).is<double>()) {
	  varray.push_back((int)((*it).get<double>()));
	} else {
	  throw PicojsonException(sstr.str());
	}
      }
      return varray;
    }
    throw PicojsonException(sstr.str());
  }

  // picojson オブジェクトから、指定したキーの値を実数値として取得する
  // キーが存在しない場合は 0 を返す
  // 値が object, array, string 型の場合は PicojsonException 例外を発生する
  double ext::_get_double(const std::string& key) const {
    const picojson::value v0 = this->get_value(key);
    if (!v0) return 0.0;
    if (v0.is<long>()) return (double)(v0.get<long>());
    if (v0.is<double>()) return v0.get<double>();
    std::stringstream sstr;
    sstr << "'" << key << "' must be an double value.";
    throw PicojsonException(sstr.str());
  }

  // picojson オブジェクトから、指定したキーの値を実数値の配列として取得する
  // キーが存在しない場合は [] を返す
  // 値が object, string 型の場合は PicojsonException 例外を発生する
  // 値が double 型の場合は要素数１の実数値配列を返す
  std::vector<double> ext::_get_double_list(const std::string& key) const {
    const picojson::value v0 = this->get_value(key);
    picojson::value v1;
    std::vector<double> varray;
    varray.clear();
    std::stringstream sstr;
    sstr << "'" << key << "' must be a list of double value.";

    if (v0.is<picojson::null>()) {
      return varray;
    } else if (v0.is<long>()) {
      varray.push_back((double)(v0.get<long>()));
      return varray;
    } else if (v0.is<double>()) {
      varray.push_back(v0.get<double>());
      return varray;
    } else if (v0.is<picojson::array>()) {
      picojson::array v = v0.get<picojson::array>();
      for (picojson::array::iterator it = v.begin(); it != v.end(); it++) {
	if ((*it).is<picojson::null>() || (*it).is<bool>()) {
	  varray.push_back(0.0);
	} else if ((*it).is<long>()) {
	  varray.push_back((double)((*it).get<long>()));
	} else if ((*it).is<double>()) {
	  varray.push_back((*it).get<double>());
	} else {
	  throw PicojsonException(sstr.str());
	}
      }
      return varray;
    }
    throw PicojsonException(sstr.str());
  }

  // JSON 表現を得る
  std::string ext::toJson() const
  {
    return this->_v.serialize();
  }
	
  // JSON から復元する, static function
  ext ext::fromJson(const std::string& json_str) {
    ext e;
    e.initByJson(json_str);
    return e;
  }
	
  // 初期化する。
  void ext::initByJson(const std::string& json_str)
  {
    std::string err;
    picojson::parse(this->_v, json_str.c_str(), json_str.c_str() + json_str.length(), &err);
    if (!err.empty()) {
      throw PicojsonException(err);
    }
  }
}
