///
/// @file
/// @brief  住所情報 Address の定義
/// @author 株式会社情報試作室
///
/// Copyright (c)2013, NII
///

#ifndef _ADDRESS_H
#define _ADDRESS_H

#include <string>
#include "picojsonExt.h"
#include "Geoword.h"

namespace geonlp
{
  class Address : public picojson::ext {
  private:

  public:
    /// コンストラクタ
    Address() { this->clear(); }

    Address(const picojson::value& v):picojson::ext(v) {}
    
    /// 初期化
    void clear() { this->initByJson("{}"); }

    /// JSON からオブジェクトを復元する
    static Address fromJson(const std::string& json_str);

    /// GeoJSON 形式のオブジェクト表現を得る
    picojson::ext getGeoObject() const;
    inline std::string getGeoJson() const { return this->getGeoObject().toJson(); }

    /// 必須項目が揃っていることを確認する
    bool isValid(const std::string& err) const;
    inline bool isValid(void) const { std::string err; return this->isValid(err); }
	
    // 定義済み項目についてはメソッドを用意し、型のチェックを行う

    // 経度・緯度
    inline void set_longitude(double v) { this->_set_double("longitude", v); }
    inline double get_longitude() const { return this->_get_double("longitude"); }
    inline void set_latitude(double v) { this->_set_double("latitude", v); }
    inline double get_latitude() const { return this->_get_double("latitude"); }

    // 住所表層形（住所要素に対応する表層形）
    inline void set_surface(const std::string& surface) { this->_set_string("surface", surface); }
    inline std::string get_surface() const { return this->_get_string("surface"); }

    // 住所正規形（住所要素の表記を結合して生成する）
    inline void set_standard_form(const std::string& v) { this->_set_string("standard_form", v); }
    inline std::string get_standard_form(void) const { return this->_get_string("standard_form"); }

    // コード（住所要素のコードを結合して生成する）
    inline picojson::value get_code(void) const { return this->get_value("code"); }

    // 住所要素
    inline void clear_address_element(void) { this->erase("address"); }
    void add_address_element(int level, const Geoword& geoword);
    void add_address_element(int level, const std::string& name, double latitude, double longitude);
    picojson::value get_address_element(void) const { return this->get_value("address"); }
  };
}

#endif
