///
/// @file
/// @brief 地名接頭辞集合、地名語の先頭となり得る品詞集合、地名語の部分となり得る品詞集合等を定義するクラスの定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///

#ifndef _PHBSDEFS_H
#define _PHBSDEFS_H

#include <string>
#include <vector>
#include <stdexcept>
#include "Profile.h"
#include "Suffix.h"

namespace geonlp
{
  class Suffix;
	
  /// @brief 地名接頭辞集合、地名語の先頭となり得る品詞集合、地名語の部分となり得る品詞集合等を定義するクラス。
  /// 
  struct PHBSDefs {
		
    /// @brief 地名接尾辞集合
    /// プロファイルから読み込み
    std::vector<Suffix> suffixes;
		
    /// @brief 地名語に続く単語集合
    /// プロファイルから読み込み
    std::vector<std::string> spatials;
    
    /// @brief 地名語にならない単語集合
    /// プロファイルから読み込み
    std::vector<std::string> non_geowords;
		
    /// @brief 地名語の先頭となり得る品詞集合
    std::vector<std::string> heads;
		
    /// @brief 地名語の部分となり得る品詞集合
    std::vector<std::string> bodies;
		
    /// @brief 地名語の先頭となり得る品詞のうち、単独で地名語になり得ない品詞集合
    std::vector<std::string> extsingle;

    /// @brief 一語の場合、地名とそれ以外の可能性を併記する品詞集合
    std::vector<std::string> alternatives;

    /// @brief 地名語に続かない品詞集合
    std::vector<std::string> stoppers;

    /// @brief 地名語に先行しない品詞集合
    std::vector<std::string> antileaders;

    /// @brief コンストラクタ。
    PHBSDefs();
		
    // プロファイルの読み込み。
    void readProfile(const Profile& profile);
  };
}
#endif
