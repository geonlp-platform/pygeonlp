///
/// @file
/// @brief 地名語クラスGeowordの定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///

#ifndef _GEOWORD_H_
#define _GEOWORD_H_

#include <exception>
#include <string>
#include <vector>
#include <map>
#include "picojsonExt.h"

// 地名語の最大長（バイト）
#define MAX_GEOWORD_LENGTH  192

namespace geonlp
{

  /// 地名語エントリを表すクラス。
  /// 2013年6月 仕様変更, JSON オブジェクトのラッパー化
  class Geoword : public picojson::ext {
  private:
    static boost::regex _sep;
    static boost::regex _pair_pat;

  protected:
    /// 指定した表記に一致する接頭辞、接尾辞を得る
    /// prefix_no, suffix_no には何番目の接頭辞、接尾辞を利用するかが入る
    /// 一致しない場合 false, 一致する組み合わせがあれば true を返す
    bool get_prefix_and_suffix_no(const std::string& surface, int& prefix_no, int& suffix_no) const;

  public:
    /// コンストラクタ
    Geoword() { this->clear(); }

    Geoword(const picojson::value& v):picojson::ext(v) {}

    /// 初期化
    inline void clear() { this->initByJson("{}"); }

    /// JSON からオブジェクトを復元する
    static Geoword fromJson(const std::string& json_str);

    /// JSON テキストを得る
    inline std::string toJson() const { return this->isValid() ? ext::toJson() : "{}"; }

    /// GeoJSON 形式のオブジェクト表現を得る
    picojson::ext getGeoObject() const;
    inline std::string getGeoJson() const { return this->getGeoObject().toJson(); }

    /// 代表表記を生成する
    std::string get_typical_name() const;

    /// 代表読みを生成する
    std::string get_typical_kana() const;

    /// 指定した表記に一致する接頭辞、接尾辞を得る
    /// prefix, suffix には対応する接頭辞、接尾辞が入る
    /// 一致しない場合 false, 一致する組み合わせがあれば true を返す
    bool get_parts_for_surface(const std::string& surface, std::string& prefix, std::string& suffix) const;

    /// 指定した表記に一致するカナを得る
    /// prefix_kana, suffix_kana には対応するカナ接頭辞、カナ接尾辞が入る
    /// 一致しない場合 false, 一致する組み合わせがあれば true を返す
    bool get_kana_parts_for_surface(const std::string& surface, std::string& prefix_kana, std::string& suffix_kana) const;

    /// 必須項目が揃っていることを確認する
    bool isValid(const std::string& err) const;
    inline bool isValid(void) const { std::string err; return this->isValid(err); }

    /// 経緯度を実数値として取得する
    /// 正常な値であれば true, 空欄または範囲外の場合は false を返す
    bool getCoordinates(double& lat, double& lon) const;
	
    // 定義済み項目についてはメソッドを用意し、型のチェックを行う
    inline void set_geonlp_id(const std::string& v) { this->_set_string("geonlp_id", v); }
    const std::string get_geonlp_id() const;

    inline void set_entry_id(const std::string& v) { this->_set_string("entry_id", v); }
    inline std::string get_entry_id() const { return this->_get_string("entry_id"); }

    inline void set_dictionary_id(int v) { this->_set_int("dictionary_id", v); }
    inline int get_dictionary_id() const { return this->_get_int("dictionary_id"); }

    inline void set_body(const std::string& v) { this->_set_string("body", v); }
    inline std::string get_body() const { return this->_get_string("body"); }

    inline void set_prefix(const std::string& v) { this->_set_string_list("prefix", v, Geoword::_sep); }
    inline void set_prefix(const std::vector<std::string>& v) { this->_set_string_list("prefix", v); }
    inline std::vector<std::string> get_prefix() const { return this->_get_string_list("prefix"); }

    inline void set_suffix(const std::string& v) { this->_set_string_list("suffix", v, Geoword::_sep); }
    inline void set_suffix(const std::vector<std::string>& v) { this->_set_string_list("suffix", v); }
    inline std::vector<std::string> get_suffix() const { return this->_get_string_list("suffix"); }

    inline void set_body_kana(const std::string& v) { this->_set_string("body_kana", v); }
    inline std::string get_body_kana() const { return this->_get_string("body_kana"); }

    inline void set_prefix_kana(const std::string& v) { this->_set_string_list("prefix_kana", v, Geoword::_sep); }
    inline void set_prefix_kana(const std::vector<std::string>& v) { this->_set_string_list("prefix_kana", v); }
    inline std::vector<std::string> get_prefix_kana() const { return this->_get_string_list("prefix_kana"); }

    inline void set_suffix_kana(const std::string& v) { this->_set_string_list("suffix_kana", v, Geoword::_sep); }
    inline void set_suffix_kana(const std::vector<std::string>& v) { this->_set_string_list("suffix_kana", v); }
    inline std::vector<std::string> get_suffix_kana() const { return this->_get_string_list("suffix_kana"); }

    inline void set_ne_class(const std::string& v) { this->_set_string("ne_class", v); }
    inline std::string get_ne_class() const { return this->_get_string("ne_class"); }

    inline void set_hypernym(const std::string& v) { this->_set_string_list("hypernym", v, Geoword::_sep); }
    inline void set_hypernym(const std::vector<std::string>& v) { this->_set_string_list("hypernym", v); }
    inline std::vector<std::string> get_hypernym() const { return this->_get_string_list("hypernym"); }
    
    inline void set_priority_score(int v) { this->_set_int("priority_score", v); }
    inline int get_priority_score() const { return this->_get_int("priority_score"); }

    inline void set_latitude(const std::string& v) { this->_set_string("latitude", v); }
    inline std::string get_latitude() const { return this->_get_string("latitude"); }

    inline void set_longitude(const std::string& v) { this->_set_string("longitude", "v"); }
    inline std::string get_longitude() const { return this->_get_string("longitude"); }

    inline void set_address(const std::string& v) { this->_set_string("address", v); }
    inline std::string get_address() const { return this->_get_string("address"); }

    inline void set_code(const std::string& v) { this->_set_string_map("code", v, Geoword::_sep, Geoword::_pair_pat); }
    inline void set_code(const std::map<std::string, std::string>& v) { this->_set_string_map("code", v); }
    inline std::map<std::string, std::string> get_code() const { return this->_get_string_map("code"); }

    inline void set_valid_from(const std::string& v) { this->_set_string("valid_from", v); }
    inline std::string get_valid_from() const { return this->_get_string("valid_from"); }

    inline void set_valid_to(const std::string& v) { this->_set_string("valid_to", v); }
    inline std::string get_valid_to() const { return this->_get_string("valid_to"); }

  };

}

#endif
