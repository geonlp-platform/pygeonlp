///
/// @file
/// @brief PicoJSON 拡張クラス
/// @author 相良 毅 sagara@info-proto.com
///
/// Copyright (c)2013, InfoProto Co.,ltd.
///

#ifndef _PICOJSON_EXT_H_
#define _PICOJSON_EXT_H_

#include <exception>
#include <string>
#include <vector>
#include <map>
#include <boost/regex.hpp>
#include "picojson.h"

namespace picojson
{

  // 例外クラス
  class PicojsonException : public std::runtime_error {

  public:
    PicojsonException(const std::string& message): runtime_error(message) {}

    ~PicojsonException() throw() {}
  };

  /// PicoJSON に文字列、ハッシュ、整数などの直接入出力を拡張
  class ext {
  protected:
    picojson::value _v;

  protected:
    // picojson オブジェクトの指定したキーに null をセットする
    void _set_null(const std::string& key);
    // picojson オブジェクトの指定したキーに boolean 値をセットする
    void _set_bool(const std::string& key, bool b);
    // picojson オブジェクトの指定したキーに文字列をセットする
    void _set_string(const std::string& key, const std::string& vstring);
    // picojson オブジェクトの指定したキーに文字列の配列をセットする
    void _set_string_list(const std::string& key, const std::string& vstring, const boost::regex& separator);
    // picojson オブジェクトの指定したキーに文字列の配列をセットする
    void _set_string_list(const std::string& key, const std::vector<std::string>& vstrings);
    // picojson オブジェクトの指定したキーに文字列のハッシュをセットする
    void _set_string_map(const std::string& key, const std::string& vstrings, const boost::regex& item_separator, const boost::regex& pair_pattern);
    // picojson オブジェクトの指定したキーに文字列のハッシュをセットする
    void _set_string_map(const std::string& key, const std::map<std::string, std::string>& vstrings);
    // picojson オブジェクトの指定したキーに整数値をセットする
    void _set_int(const std::string& key, int vint);
    // picojson オブジェクトの指定したキーに整数値の配列をセットする
    void _set_int_list(const std::string& key, const std::vector<int>& values);
    // picojson オブジェクトの指定したキーに実数値をセットする
    void _set_double(const std::string& key, double vdouble);
    // picojson オブジェクトの指定したキーに実数値の配列をセットする
    void _set_double_list(const std::string& key, const std::vector<double>& values);

  public:
    // picojston オブジェクトの指定したキーが null かどうか判定する
    bool is_null(const std::string& key) const;
    // picojson オブジェクトの指定したキーの値を boolean 値として取得する
    bool _get_bool(const std::string& key) const ;
    // picojson オブジェクトの指定したキーの値を文字列として取得する
    std::string _get_string(const std::string& key) const ;
    // picojson オブジェクトの指定したキーの値を文字列の配列として取得する
    std::vector<std::string> _get_string_list(const std::string& key) const ;
    // picojson オブジェクトの指定したキーの値を文字列のハッシュとして取得する
    std::map<std::string, std::string> _get_string_map(const std::string& key) const ;
    // picojson オブジェクトの指定したキーの値を整数値として取得する
    int _get_int(const std::string& key) const ;
    // picojson オブジェクトの指定したキーの値を整数値の配列として取得する
    std::vector<int> _get_int_list(const std::string& key) const ;
    // picojson オブジェクトの指定したキーの値を実数値として取得する
    double _get_double(const std::string& key) const ;
    // picojson オブジェクトの指定したキーの値を実数値の配列として取得する
    std::vector<double> _get_double_list(const std::string& key) const ;

  public:
    /// constructor
    ext();
    ext(const picojson::value& v) { this->_v = v; }
    ext(const std::string& vstr) { this->initByJson(vstr); }

    /// cast operator
    operator picojson::value() { return this->_v; }

    // setter と getter
    void set_value(const std::string& key, const picojson::value& v);
    void set_value(const std::string& key, const ext& v);
    inline void set_value(const std::string& key, const picojson::null& n) { this->_set_null(key); }
    inline void set_value(const std::string& key, bool b) { this->_set_bool(key, b); }
    inline void set_value(const std::string& key, const char* v) { this->_set_string(key, std::string(v)); }
    inline void set_value(const std::string& key, const std::string& vstring) { this->_set_string(key, vstring); }
    inline void set_value(const std::string& key, const std::string& vstring, const boost::regex& separator) { this->_set_string_list(key, vstring, separator); }
    inline void set_value(const std::string& key, const std::vector<std::string>& vstrings) { this->_set_string_list(key, vstrings); }
    inline void set_value(const std::string& key, const std::map<std::string, std::string>& vmap) { this->_set_string_map(key, vmap); }
    inline void set_value(const std::string& key, int vint) { this->_set_int(key, vint); }
    inline void set_value(const std::string& key, const std::vector<int>& values) { this->_set_int_list(key, values); }
    inline void set_value(const std::string& key, double vdouble) { this->_set_double(key, vdouble); }
    inline void set_value(const std::string& key, const std::vector<double>& values) { this->_set_double_list(key, values); }

    // 要素のチェック
    inline bool has_key(const std::string& key) { int c = this->_v.get<picojson::object>().count(key); return c > 0; }

    // 要素を削除
    inline void erase(const std::string& key) { this->_v.get<picojson::object>().erase(key); }

    // オブジェクトのキー一覧を取得する
    std::vector<std::string> get_keys() const;
    picojson::value get_value(const std::string& key) const ;

    /// JSON テキストを得る。
    std::string toJson() const;

    /// JSON からオブジェクトを復元する
    static ext fromJson(const std::string& json_str) ;
	
    /// JSON 文字列で初期化する
    void initByJson(const std::string& json_str);
  };

}

#endif
