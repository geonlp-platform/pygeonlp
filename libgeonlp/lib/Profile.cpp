///
/// @file
/// @brief プロファイルクラスの実装。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///

#include "Profile.h"
#include <boost/property_tree/ini_parser.hpp>
#include <boost/algorithm/string.hpp>
#include <iostream>
#include "config.h"
#include "stdio.h"

static int is_file_exists(const std::string& filename) {
  FILE* fp = fopen((char*)filename.c_str(), "r");
  if (!fp) return 0;
  fclose(fp);
  return 1;
}

namespace geonlp {

  // プロファイルのパスを探す
  std::string Profile::searchProfile(const std::string& basename) {
    std::string filename(GEONLP_RESOURCE_FILENAME);
    std::string rcfilepath = "";

    // 指定されたパスを確認
    if (basename.length() > 0) {
      if (basename[basename.length() -1] == '/') {
	// ディレクトリを指定された場合はデフォルトファイル名を追加する
	rcfilepath = rcfilepath + filename;
      } else {
	rcfilepath = basename;
      }
    }
    if (is_file_exists(rcfilepath)) {
      return rcfilepath;
    }

    // 環境変数をチェック
    char* p = std::getenv("GEONLP_DIR");
    if (p) {
      rcfilepath = std::string(p);
      if (rcfilepath[rcfilepath.length() - 1] == '/') {
	rcfilepath = rcfilepath.substr(0, rcfilepath.length() - 1);
      }
      rcfilepath = rcfilepath + "/" + filename;
    }
    if (is_file_exists(rcfilepath)) {
      return rcfilepath;
    }

    // カレントディレクトリをチェック
    if (is_file_exists(filename)) {
      return filename;
    }
    
    // /etc, /usr/etc, /usr/local/etc の下をチェックする
    rcfilepath = std::string("/etc/") + filename;
    if (is_file_exists(std::string("/etc/") + filename)) {
      return std::string("/etc/") + filename;
    }
    if (is_file_exists(std::string("/usr/etc/") + filename)) {
      return std::string("/usr/etc/") + filename;
    }
    if (is_file_exists(std::string("/usr/local/etc/") + filename)) {
      return std::string("/usr/local/etc/") + filename;
    }

    throw std::runtime_error(std::string("No profile found with the given parameter ('") + basename + std::string("')"));
    return "";
  }

  // プロファイルを読み込む
  void Profile::load(const std::string& f) {
    filepath = f;
    try {
      boost::property_tree::ptree prop;
      read_ini(filepath, prop);
			
      formatter = prop.get<std::string>("formatter", "");

      // suffix
      suffix.clear();
      suffix_str = prop.get<std::string>("suffix", "");
      std::vector<std::string> suffix_data_strs;
      boost::split(suffix_data_strs, suffix_str, boost::is_any_of("|"));

      for (std::vector<std::string>::iterator it = suffix_data_strs.begin(); 
	   it != suffix_data_strs.end(); it++) {
	std::vector<std::string> v;
	boost::split(v, (*it), boost::is_any_of(","));
	if (v.size() == 3) {
	  Suffix s(v[0], v[1], v[2]);
	  suffix.push_back(s);
	}
      }
			
      // spatial
      spatial.clear();
      spatial_str = prop.get<std::string>("spatial", "");
      boost::split(spatial, spatial_str, boost::is_any_of("|"));

      // non_geoword
      non_geoword.clear();
      non_geoword_str = prop.get<std::string>("non_geoword", "");
      boost::split(non_geoword, non_geoword_str, boost::is_any_of("|"));

      // dictionary
      dictionary.clear();
      dictionary_str = prop.get<std::string>("dictionary", "");
      if (dictionary_str.empty()) dictionary_str = ""; // 無指定の場合はすべての辞書を利用
      boost::split(dictionary, dictionary_str, boost::is_any_of("|"));

      // ne_class
      ne_class.clear();
      ne_class_str = prop.get<std::string>("ne_class", "");
      if (ne_class_str.empty()) ne_class_str = ".*"; // 無指定の場合はすべてのクラスを利用
      boost::split(ne_class, ne_class_str, boost::is_any_of("|"));

      // address_regex
      std::string address_regex_str = prop.get<std::string>("address_regex", "^$");
      address_regex = boost::regex(address_regex_str);

      // データファイルディレクトリを取得
      // 最後が '/' で終わっていない場合、追加する
      data_dir = prop.get<std::string>("data_dir", "");
      if (data_dir.empty()) throw std::runtime_error("data_dir property is not set in the profile.");
      if (data_dir.at(data_dir.length() - 1) != '/') data_dir += "/";

      // log_dir
      log_dir = prop.get<std::string>("log_dir", "");
      if (log_dir.empty()) log_dir = "";
      else if (log_dir.at(log_dir.length() - 1) != '/') log_dir += "/";

#ifdef HAVE_LIBDAMS
      // dams_path
      dams_path = prop.get<std::string>("dams_path", "");
      if (dams_path.empty()) {
	// GeoNLP のライブラリパスを探す
	dams_path = this->get_data_dir() + "dams";
	if (!is_file_exists(dams_path + ".dat")) dams_path = "";

	// DAMS のデフォルトパスを探す
	dams_path = std::string(damswrapper::default_dic_path()) + "dams";
	if (!is_file_exists(dams_path + ".dat")) dams_path = "";
      }
      if (dams_path.empty()) {
	std::string msg = std::string("'dams_path' property is not set in the profile, and DAMS dictionary files can't be found in default paths (") + this->get_data_dir() + "dams.dat, " + damswrapper::default_dic_path() + "dams.dat).";
	throw std::runtime_error(msg);
      }
#endif /* HAVE_LIBDAMS */

    } catch (std::runtime_error& e) {
      throw e;
    }
  }

  // プロファイルを JSON から読み込む
  void Profile::load(const picojson::value& options) {
    picojson::value v;
    try {
      // suffix
      v = options.get("suffix");
      if (v.is<std::string>()) {
	suffix.clear();
	suffix_str = v.get<std::string>();
	std::vector<std::string> suffix_data_strs;
	boost::split(suffix_data_strs, suffix_str, boost::is_any_of("|"));

	for (std::vector<std::string>::iterator it = suffix_data_strs.begin(); 
	     it != suffix_data_strs.end(); it++) {
	  std::vector<std::string> v;
	  boost::split(v, (*it), boost::is_any_of(","));
	  if (v.size() == 3) {
	    Suffix s(v[0], v[1], v[2]);
	    suffix.push_back(s);
	  }
	}
      }
			
      // spatial
      v = options.get("spatial");
      if (v.is<std::string>()) {
	spatial.clear();
	spatial_str = v.get<std::string>();
	boost::split(spatial, spatial_str, boost::is_any_of("|"));
      }

      // non_geoword
      v = options.get("non_geoword");
      if (v.is<std::string>()) {
	non_geoword.clear();
	non_geoword_str = v.get<std::string>();
	boost::split(non_geoword, non_geoword_str, boost::is_any_of("|"));
      }

      // データファイルディレクトリを取得
      // 最後が '/' で終わっていない場合、追加する
      v = options.get("data_dir");
      if (!v.is<std::string>()) {
	throw std::runtime_error("A string value must be set to 'data_dir'.");
      }
      if (v.is<std::string>()) {
	data_dir = v.get<std::string>();
	if (data_dir.empty()) {
	  throw std::runtime_error("data_dir property is not set in the profile.");
	}
	if (data_dir.at(data_dir.length() - 1) != '/') data_dir += "/";
      }

      // log_dir
      v = options.get("log_dir");
      if (v.is<std::string>()) {
	log_dir = v.get<std::string>();
	if (log_dir.empty()) log_dir = "";
	else if (log_dir.at(log_dir.length() - 1) != '/') log_dir += "/";
      }

      // system_dic_dir
      v = options.get("system_dic_dir");
      if (v.is<std::string>()) {
	system_dic_dir = v.get<std::string>();
	if (system_dic_dir.at(system_dic_dir.length() - 1) != '/') {
	  system_dic_dir += "/";
	}
      }

    } catch (std::runtime_error& e) {
      throw e;
    }
  }

  // デフォルトプロファイルを取得する
  void Profile::set_default(void) {
    // formatter
    this->formatter = "DefaultGeowordFormatter";

    // suffix
    this->suffix.clear();
    this->suffix_str = "前,マエ,マエ|内,ナイ,ナイ|立,リツ,リツ|境,サカイ,サカイ|東,ヒガシ,ヒガシ|西,ニシ,ニシ|南,ミナミ,ミナミ|北,キタ,キタ";
    std::vector<std::string> suffix_data_strs;
    boost::split(suffix_data_strs, this->suffix_str, boost::is_any_of("|"));
    for (std::vector<std::string>::iterator it = suffix_data_strs.begin(); 
	 it != suffix_data_strs.end(); it++) {
      std::vector<std::string> v;
      boost::split(v, (*it), boost::is_any_of(","));
      if (v.size() == 3) {
	Suffix s(v[0], v[1], v[2]);
	this->suffix.push_back(s);
      }
    }
			
    // spatial
    this->spatial.clear();
    this->spatial_str = "付近|周辺|周囲|経由|沿線|沿岸|沿い|沖|上流|下流|河口|出身|地区|－|間|地|発|着";
    boost::split(this->spatial, this->spatial_str, boost::is_any_of("|"));

    // non_geoword
    this->non_geoword.clear();
    this->non_geoword_str = "本部|一部|月";
    boost::split(this->non_geoword, this->non_geoword_str, boost::is_any_of("|"));

    // dictionary
    this->dictionary.clear();
    this->dictionary_str = "";
    boost::split(this->dictionary, this->dictionary_str, boost::is_any_of("|"));

    // ne_class
    this->ne_class.clear();
    this->ne_class_str = ".*";
    boost::split(this->ne_class, this->ne_class_str, boost::is_any_of("|"));

    // address_regex
    std::string address_regex_str = "^(都道府県|市区町村|行政地域|居住地名)(\\/.+|)";
    this->address_regex = boost::regex(address_regex_str);

    // データファイルディレクトリを取得
    // 最後が '/' で終わっていない場合、追加する
    this->data_dir = "";

    // log_dir
    this->log_dir = "";

    // system_dic_dir
    this->system_dic_dir = "";
  }

}
