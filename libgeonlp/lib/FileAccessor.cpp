///
/// @file
/// @brief Fileアクセスクラス FileAccessorの実装
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///
#include <iostream>
#include <fstream>
#include <sstream>
#include <boost/regex.hpp>
#include "Geoword.h"
#include "Dictionary.h"
#include "FormatException.h"
#include "FileAccessor.h"
#include "CSVReader.h"

namespace geonlp
{
  // Trim white characters from end in place.
  static inline void rtrim(std::string &s) {
    size_t pos = s.find_last_not_of(" \t\n\r");
    s.erase(pos + 1);
  }
  
  /// @brief 辞書 CSV ファイルから地名語と辞書情報を読み込む
  ///
  /// @arg @c csvfilename   CSV ファイル名（地名語データ）
  /// @arg @c jsonfilename  JSON ファイル名（辞書データ）
  /// @return 読み込んだ地名語の件数
  /// @exception SqliteNotInitaizliedException Sqlite3 が初期化されていない
  /// @exception SqliteErrException Sqlite3 の処理中にエラーが発生
  int FileAccessor::importDictionaryCSV(const std::string& csvfilename, const std::string& jsonfilename) const {
    std::string err = "";
    
    // 辞書データ読み込み
    std::ifstream fs_json(jsonfilename.c_str());
    if (!fs_json.is_open()) {
      std::ostringstream sstr;
      sstr << "Dictionary Data (JSON) file is not readable : " << jsonfilename;
      throw std::runtime_error(sstr.str());
    }
    /// c++ の全部読み込みは少しトリッキー
    int filesize = 0;
    fs_json.seekg(0, std::ios::end);
    filesize = fs_json.tellg();
    fs_json.seekg(0, std::ios::beg);
    char* buf = new char[filesize + 1];
    fs_json.read(buf, filesize);
    buf[filesize] = '\0';
    std::string json_str(buf, filesize);
    delete[] buf;

    // std::cerr << "-----\n" << json_str << "-----\n" << std::endl;
    geonlp::Dictionary dic_in;
    dic_in.initByJson(json_str);
    if (!dic_in.isValid(err)) {
      std::ostringstream sstr;
      sstr << "Dictionary Data (JSON) is not valid. " << err;
      throw geonlp::FormatException(sstr.str());
    }
    std::vector<Dictionary> dictionaries;
    dictionaries.push_back(dic_in);
    this->_dbap->setDictionaries(dictionaries);
    std::string dic_identifier = dic_in.get_identifier();
    int dic_id = this->_dbap->getDictionaryInternalId(dic_identifier); // 内部ID
    std::stringstream ss;
    std::string dic_id_str;
    ss << "_" << dic_id << "_";
    ss >> dic_id_str;

    // 地名語データ読み込み
    std::fstream fs_csv(csvfilename.c_str(), std::ios::in);
    if (!fs_csv.is_open()) return 0;
    CSVReader csv(fs_csv);
    int lineno = 0;
    std::vector<std::string> fields;
    std::vector<std::string> tokens;
    Geoword geoword_in;
    std::vector<Geoword> geowords;
    while (!csv.Read(tokens)) {
      geoword_in.clear();
      if (lineno == 0) {
	// 見出し行
	for (unsigned int i = 0; i < tokens.size(); i++) {
	  rtrim(tokens[i]);
	  fields.push_back(tokens[i]);
	}
      } else {
	// データ行
	for (unsigned int i = 0; i < tokens.size(); i++) {
	  rtrim(tokens[i]);
	  // 複数可のフィールドはフィールド名を明示的に
	  // 指定することで、文字列が分割され、配列として登録される
	  if (fields[i] == "prefix") {
	    geoword_in.set_prefix(tokens[i]);
	  } else if (fields[i] == "suffix") {
	    geoword_in.set_suffix(tokens[i]);
	  } else if (fields[i] == "prefix_kana") {
	    geoword_in.set_prefix_kana(tokens[i]);
	  } else if (fields[i] == "suffix_kana") {
	    geoword_in.set_suffix_kana(tokens[i]);
	  } else if (fields[i] == "hypernym") {
	    geoword_in.set_hypernym(tokens[i]);
	  } else if (fields[i] == "code") {
	    geoword_in.set_code(tokens[i]);
	  } else {
	    geoword_in.set_value(fields[i], tokens[i]);
	  }
	}
	geoword_in.set_dictionary_id(dic_id);
	if (!geoword_in.has_key("geonlp_id")) {
	  if (geoword_in.has_key("geolod_id")) {
	    // geolod_id がセットされているので geonlp_id に乗せ換える
	    geoword_in.set_geonlp_id(geoword_in._get_string("geolod_id"));
	    geoword_in.erase("geolod_id");
	  } else if (geoword_in.has_key("entry_id")) {
	    // geonlp_id がセットされていないので内部IDをセットする
	    std::string tmp_id = dic_id_str + geoword_in.get_entry_id();
	    geoword_in.set_geonlp_id(tmp_id);
	  }
	}
	if (geoword_in.isValid(err)) {
	  geowords.push_back(geoword_in);
	}
      }
      lineno++;
    }
    if (geowords.size() == 0) {
      throw std::runtime_error("No geoword stored. Check the csv file format.");
    }
    this->_dbap->setGeowords(geowords);
    return geowords.size();
  }

}
