///
/// @file
/// @brief 住所クラスAddressの実装。
/// @author 株式会社情報試作室
///
/// Copyright (c)2013, NII
///
#include <sstream>
#include "Address.h"

namespace geonlp
{
  /// JSON からオブジェクトを復元する
  Address Address::fromJson(const std::string& json_str) {
    Address in;
    in.initByJson(json_str);
    return in;
  }

  /// API 出力用の GeoJSON 表記を生成する
  picojson::ext Address::getGeoObject() const {
    ext geo, geometry, properties;
    std::stringstream ss_lon, ss_lat;

    // geo->geometry オブジェクトの作成
    std::vector<double> coordinates;
    double longitude, latitude;
    longitude = this->get_longitude();
    latitude = this->get_latitude();
    coordinates.push_back(longitude);
    coordinates.push_back(latitude);
    geometry.set_value("coordinates", coordinates);
    geometry.set_value("type", "Point");

    // geo->peoperties オブジェクトの作成
    properties.set_value("name", this->get_standard_form());
    properties.set_value("standard_form", this->get_standard_form());
    properties.set_value("address", this->get_address_element());
    properties.set_value("code", this->get_code());
    properties.set_value("longitude", longitude);
    properties.set_value("latitude", latitude);

    // geo オブジェクトの作成
    geo.set_value("type", "Feature");
    geo.set_value("geometry", geometry);
    geo.set_value("properties", properties);

    return geo;
  }

  // 必須項目が揃っていることを確認する
  bool Address::isValid(const std::string& err) const {
    if (this->get_standard_form().length() == 0) return false;
    return true;
  }

}

