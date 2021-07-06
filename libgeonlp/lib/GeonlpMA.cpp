///
/// @file
/// @brief 地名語抽出API(インタフェース)の実装。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///
#include <config.h>
#include <iostream>
#ifdef HAVE_CONFIG_H
#include <stdlib.h>
#endif /* HAVE_CONFIG_H */
#include "GeonlpMA.h"
#include "Profile.h"
#include "MeCabAdapter.h"
#include "DBAccessor.h"
#include "GeonlpMAImplSq3.h"

/// @brief プロファイル定義ファイルのデフォルトディレクトリ
/// @note configure 時の prefix に合わせて Makefile 中に定義される
//#define PROFILE_DEFAULT_DIR_PATH "/usr/local/etc/"

namespace geonlp
{
  // MAインタフェースを取得する。
  // @arg @c profile プロファイル名。
  // @exception ServiceCreateFailedException 取得失敗。	
  MAPtr createMA(const std::string& dict_dir, const std::string& profile)
  {
    // Profileの読み込み
    ProfilePtr profilesp = ProfilePtr(new Profile());
    if (profile == "") {
      profilesp->set_default();
      profilesp->set_data_dir(dict_dir);
    } else {
      std::string profilepath = Profile::searchProfile(profile);
      try{
	profilesp->load(profilepath);
      } catch( std::runtime_error& e){
	throw ServiceCreateFailedException(e.what(), ServiceCreateFailedException::PROFILE);
      }
    }

    try{
      return MAPtr(new MAImpl(profilesp));
    } catch( std::runtime_error& e){
      throw ServiceCreateFailedException( e.what(), ServiceCreateFailedException::SERVICE);
    }
  }


  // MAインタフェースを取得する。
  // @arg @c settings 設定情報を含む picojson::object
  // @exception ServiceCreateFailedException 取得失敗。	
  MAPtr createMA(const picojson::value& settings) {
    ProfilePtr profilesp = ProfilePtr(new Profile());
    profilesp->set_default();
    
    if (! settings.is<picojson::object>()) {
      throw ServiceCreateFailedException("Parameter must be an key-value object.", ServiceCreateFailedException::SERVICE);
    }

    profilesp->load(settings);
    /*
    // system_dic_dir
    const picojson::value& v = settings.get("system_dic_dir");
    if (!v.is<picojson::null>()) {
      if (! v.is<std::string>()) {
	throw ServiceCreateFailedException("String value must be set to 'system_dic_dir'.", ServiceCreateFailedException::SERVICE);
      }
      profilesp->set_system_dic_dir(v.to_str());
    }
    */
    
    try{
      return MAPtr(new MAImpl(profilesp));
    } catch( std::runtime_error& e){
      throw ServiceCreateFailedException( e.what(), ServiceCreateFailedException::SERVICE);
    }
  }
  
}
