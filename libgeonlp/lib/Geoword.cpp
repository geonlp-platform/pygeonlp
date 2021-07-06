///
/// @file
/// @brief 地名語クラスGeowordの実装。
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///
#include <sstream>
#include "config.h"
#include "Geoword.h"
#ifdef HAVE_LIBDAMS
#include <dams.h>
#endif /* HAVE_LIBDAMS */

namespace geonlp
{
  boost::regex Geoword::_sep = boost::regex("/");
  boost::regex Geoword::_pair_pat = boost::regex("(.+):(.+)", boost::regex_constants::egrep);

  /// geonlp_id を取得する
  const std::string Geoword::get_geonlp_id() const {
    std::string geonlp_id = this->_get_string("geonlp_id");
    if (geonlp_id.length() == 0) {
      geonlp_id = this->_get_string("geolod_id");
    }
    return geonlp_id;
  }

  /// JSON からオブジェクトを復元する
  Geoword Geoword::fromJson(const std::string& json_str) {
    Geoword in;
    in.initByJson(json_str);
    return in;
  }

  /// API 出力用の GeoJSON 表記を生成する
  picojson::ext Geoword::getGeoObject() const {
    ext geo, geometry, properties;

    // geo->geometry オブジェクトの作成
    std::vector<double> coordinates;
    coordinates.clear();
    double latitude, longitude;
    if (this->getCoordinates(latitude, longitude)) {
      coordinates.push_back(longitude);
      coordinates.push_back(latitude);
    } // 経緯度が空欄または範囲外の場合、 coordinates は空の配列とする
    geometry.set_value("coordinates", coordinates);
    geometry.set_value("type", "Point");

    // geo->peoperties オブジェクトの作成
    // name, kana が存在しない場合は追加する
    properties = (*this);
    if (properties._get_string("name") == "") properties.set_value("name", this->get_typical_name());
    if (properties._get_string("kana") == "") properties.set_value("kana", this->get_typical_kana());

    // geo オブジェクトの作成
    geo.set_value("type", "Feature");
    geo.set_value("geometry", geometry);
    geo.set_value("properties", properties);

    return geo;
  }

  /// 代表表記を生成する
  std::string Geoword::get_typical_name() const {
    std::string name = "";
    std::vector<std::string> prefix = this->get_prefix();
    std::vector<std::string> suffix = this->get_suffix();
    if (prefix.size() > 0) name += prefix[0];
    name += this->get_body();
    if (suffix.size() > 0) name += suffix[0];
    return name;
  }

  /// 代表カナを生成する
  std::string Geoword::get_typical_kana() const {
    std::string name = "";
    std::vector<std::string> prefix = this->get_prefix_kana();
    std::vector<std::string> suffix = this->get_suffix_kana();
    if (prefix.size() > 0) name += prefix[0];
    name += this->get_body_kana();
    if (suffix.size() > 0) name += suffix[0];
    return name;
  }

  // 必須項目が揃っていることを確認する
  bool Geoword::isValid(const std::string& err) const {
    if (this->get_geonlp_id().length() == 0) return false;
    if (this->get_dictionary_id() == 0) return false;
    if (this->get_body().length() == 0) return false;
    if (this->get_ne_class().length() == 0) return false;
    return true;
  }

  // 経緯度を実数値として取得する
  /// 正常な値であれば true, 空欄または範囲外の場合は false を返す
  bool Geoword::getCoordinates(double& lat, double& lon) const {
    if (this->get_latitude().length() == 0) return false;
    if (this->get_longitude().length() == 0) return false;
    std::stringstream ss_lat, ss_lon;
    ss_lat.str("");
    ss_lat << this->get_latitude();
    ss_lat >> lat;
    if (lat < -90.00 || lat > +90.00) return false;
    ss_lon.str("");
    ss_lon << this->get_longitude();
    ss_lon >> lon;
    if (lon < -180.00 || lon > +180.00) return false;
    return true;
  }

  /// 指定した表記に一致する接頭辞、接尾辞を得る
  /// prefix_no, suffix_no には何番目の接頭辞、接尾辞を利用するかが入る
  /// 一致しない場合 false, 一致する組み合わせがあれば true を返す
  bool Geoword::get_prefix_and_suffix_no(const std::string& surface, int& prefix_no, int& suffix_no) const {
    bool is_prefix_omitted = false;
    bool is_suffix_omitted = false;
    std::vector<std::string> prefix = this->get_prefix();
    std::vector<std::string> suffix = this->get_suffix();
    std::string body = this->get_body();
    std::string standardized = surface;
    if (prefix.size() == 0) {
      is_prefix_omitted = true;
      prefix.push_back("");
    }
    if (suffix.size() == 0) {
      is_suffix_omitted = true;
      suffix.push_back("");
    }
#ifdef HAVE_LIBDAMS
    standardized = damswrapper::get_standardized_string(surface);
#endif /* HAVE_LIBDAMS */
    for (prefix_no = 0; prefix_no < int(prefix.size()); prefix_no++) {
      std::string prefix_str = prefix[prefix_no];
      for (suffix_no = 0; suffix_no < int(suffix.size()); suffix_no++) {
	std::string suffix_str = suffix[suffix_no];
	std::string str = prefix_str + body + suffix_str;
#ifdef HAVE_LIBDAMS
	str = damswrapper::get_standardized_string(str);
#endif /* HAVE_LIBDAMS */
        if (str == standardized) {
	  if (is_prefix_omitted) prefix_no = -1;
	  if (is_suffix_omitted) suffix_no = -1;
	  return true;
	}
      }
    }
    return false;
  }

  /// 指定した表記に一致する接頭辞、接尾辞を得る
  /// prefix, suffix には対応する接頭辞、接尾辞が入る
  /// 一致しない場合 false, 一致する組み合わせがあれば true を返す
  bool Geoword::get_parts_for_surface(const std::string& surface, std::string& prefix, std::string& suffix) const {
    int prefix_no, suffix_no;
    prefix = "";
    suffix = "";
    bool r = get_prefix_and_suffix_no(surface, prefix_no, suffix_no);
    if (!r) return false;
    if (prefix_no >= 0) prefix = this->get_prefix()[prefix_no];
    if (suffix_no >= 0) suffix = this->get_suffix()[suffix_no];
    return true;
  }

  /// 指定した表記に一致するカナを得る
  /// prefix_kana, suffix_kana には対応するカナ接頭辞、カナ接尾辞が入る
  /// 一致しない場合 false, 一致する組み合わせがあれば true を返す
  bool Geoword::get_kana_parts_for_surface(const std::string& surface, std::string& prefix_kana, std::string& suffix_kana) const {
    int prefix_no, suffix_no;
    prefix_kana = "";
    suffix_kana = "";
    bool r = get_prefix_and_suffix_no(surface, prefix_no, suffix_no);
    if (!r) return false;
    if (prefix_no >= 0) {
      std::vector<std::string> prefixes = this->get_prefix_kana();
      if (prefix_no < int(prefixes.size())) prefix_kana = prefixes[prefix_no];
    }
    if (suffix_no >= 0) {
      std::vector<std::string> suffixes = this->get_suffix_kana();
      if (suffix_no < int(suffixes.size())) suffix_kana = suffixes[suffix_no];
    }
    return true;
  }

}

