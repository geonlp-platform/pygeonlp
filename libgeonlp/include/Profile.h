///
/// @file
/// @brief プロファイルクラス。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///

#ifndef _PROFILE_H
#define _PROFILE_H

#include "config.h"
#include <string>
#include <vector>
#include <stdexcept>
#include <boost/regex.hpp>
#include "Suffix.h"
#include "picojson.h"

#ifdef HAVE_LIBDAMS
#include <dams.h>
#endif /* HAVE_LIBDAMS */

/// @brief プロファイル定義ファイルのファイル名は、プロファイル名にこの拡張子を付加したもの。
#define PROFILE_FILE_EXT ".rc"

namespace geonlp {
	
  class Profile {
	
  private:
    std::string filepath;
    std::string formatter;
    std::string suffix_str;
    std::vector<Suffix> suffix;
    std::string spatial_str;
    std::vector<std::string> spatial;
    std::string non_geoword_str;
    std::vector<std::string> non_geoword;
    std::string dictionary_str;
    std::vector<std::string> dictionary;
    std::string ne_class_str;
    std::vector<std::string> ne_class;
    boost::regex address_regex;
    std::string data_dir;
    std::string system_dic_dir;
    std::string log_dir;
#ifdef HAVE_LIBDAMS
    std::string dams_path;
#endif /* HAVE_LIBDAMS */

  public:

    // デフォルトプロファイルパスを探す
    static std::string searchProfile(const std::string& basename = PACKAGE_NAME);
		
    Profile() {}
    
    void load(const std::string& f);
    void load(const picojson::value& v);

    void set_default(void);
		
    inline const std::string& get_filepath() const {
      return filepath;
    }
		
    inline const std::string& get_formatter() const {
      return formatter;
    }
		
    inline const std::string& get_suffix_str() const {
      return suffix_str;
    }
		
    inline const std::vector<Suffix>& get_suffix() const {
      return suffix;
    }
		
    inline const std::string& get_spatial_str() const {
      return spatial_str;
    }

    inline const std::vector<std::string>& get_spatial() const {
      return spatial;
    }

    inline const std::string& get_non_geoword_str() const {
      return non_geoword_str;
    }

    inline const std::vector<std::string>& get_non_geoword() const {
      return non_geoword;
    }

    inline const std::string& get_dictionary_str() const {
      return dictionary_str;
    }

    inline const std::vector<std::string>& get_dictionary() const {
      return dictionary;
    }

    inline const std::string& get_ne_class_str() const {
      return ne_class_str;
    }

    inline const boost::regex& get_address_regex() const {
      return address_regex;
    }

    inline const std::vector<std::string>& get_ne_class() const {
      return ne_class;
    }

    inline std::string get_data_dir() const {
      std::string data_dir = this->data_dir;
      if (data_dir.at(data_dir.length() - 1) != '/') data_dir += "/";
      return data_dir;
    }

    inline const std::string& get_system_dic_dir() const {
      return system_dic_dir;
    }

    inline void set_data_dir(const std::string& data_dir) {
      this->data_dir = data_dir;
      if (this->data_dir.at(this->data_dir.length() - 1) != '/')
        this->data_dir += "/";
    }

    inline const std::string& get_log_dir() const {
      return log_dir;
    }
		
    inline const std::string get_sqlite3_file() const {
      return this->get_data_dir() + "geodic.sq3";
    }
		
    inline const std::string get_darts_file() const {
      return this->get_data_dir() + "geo_name_fullname.drt";
    }
		
    inline const std::string get_wordlist_file() const {
      return this->get_data_dir() + "wordlist.sq3";
    }
		
    inline const std::string get_mecab_userdic() const {
      return this->get_data_dir() + "mecabusr.dic";
    }

#ifdef HAVE_LIBDAMS
    inline const std::string get_damsfile() const { return dams_path; }
#endif /* HAVE_LIBDAMS */

  };
}

#endif
