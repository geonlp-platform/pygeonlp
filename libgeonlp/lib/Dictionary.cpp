///
/// @file
/// @brief 解析辞書クラスDictionaryの実装
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///
#include <sstream>
#include <boost/regex.hpp>
#include "Dictionary.h"

namespace geonlp
{

  /// JSON からオブジェクトを復元する
  Dictionary Dictionary::fromJson(const std::string& json_str) {
    Dictionary dic;
    dic.initByJson(json_str);
    return dic;
  }

  // 必須項目が揃っていることを確認する
  bool Dictionary::isValid(std::string& err) const {
    if (this->get_identifier().length() == 0) return false;
    if (this->get_name().length() == 0) return false;
    if (this->get_content_url().length() == 0) return false;
    return true;
  }

  bool Dictionary::isValid(void) const {
    std::string err("");
    return this->isValid(err);
  }

  // 辞書識別子
  // "identifier" が指す配列の中で "geonlp:" から始まるものを返す
  const std::string Dictionary::get_identifier(void) const {
    picojson::value v = this->get_value("identifier");
    if (!v.is<picojson::array>()) {
      throw std::runtime_error("The 'identifier' element must be an array.");
    }
    picojson::array id_list = v.get<picojson::array>();
    for (picojson::array::iterator it = id_list.begin(); it != id_list.end(); it++) {
      if (! (*it).is<std::string>()) {
	continue;
      }
      std::string id_str = (*it).get<std::string>();
      if (id_str.substr(0, 7) == "geonlp:") {
	return id_str;
      }
    }
    throw std::runtime_error("No element starting with 'geonlp:' found.");
  }

  // CSV の置かれている場所を指す URL を取得する
  // "/distribution[0]/contentUrl"
  const std::string Dictionary::get_content_url(void) const {
    picojson::value v = this->get_value("distribution");
    if (!v.is<picojson::array>()) {
      throw std::runtime_error("'distribution' element must be an array.");
    }
    picojson::array dist_list = v.get<picojson::array>();
    for (picojson::array::iterator it = dist_list.begin(); it != dist_list.end(); it++) {
      if (!(*it).is<picojson::object>()) continue;
      picojson::value v2 = (*it).get("contentUrl");
      if (v2.is<std::string>()) {
	return v2.get<std::string>();
      }      
    }
    throw std::runtime_error("'distribution' element found but not in the expected format.");
  }

}
