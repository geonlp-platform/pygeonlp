///
/// @file
/// @brief 形態素情報拡張クラスの実装。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///
#include <sstream>
#include <vector>
#include <iostream>
#include "NodeExt.h"
#include "Suffix.h"

namespace geonlp
{
  // デバグ用のテキスト表記を得る。
  std::string NodeExt::toString() const
  {
    std::ostringstream oss;
    oss << Node::toString();
    oss << " [";
    if ( bPrefix) oss << "P";
    if ( bHead) oss << "H";
    if ( bBody) oss << "B";
    if ( bSuffix) oss << "S";
    if ( bAlternative) oss << "A";
    if ( bStop) oss << "X";
    if ( bAntileader) oss << "Q";
    oss << "]";
    return oss.str();
  }

  // 地名以外の可能性（人名、組織名）がある場合、
  // その品詞名を得る。
  std::string NodeExt::getAlternativeValue(const PHBSDefs& phbsdef) const
  {
    if (! bAlternative ) return std::string("");
    for (std::vector<std::string>::const_iterator it = phbsdef.alternatives.begin(); it != phbsdef.alternatives.end(); it++) {
      if ( 0 == feature.compare( 0, it->length(), *it)) {
  // 名詞,固有名詞,人名,姓 の場合「名詞-固有名詞-人名-姓」を、
  // 名詞,固有名詞,組織,*  の場合「名詞-固有名詞-組織」を取得する
  {
    std::vector<std::string> feature_elements;
    const char* sp, *cp;
    sp = cp = feature.c_str();
    // 分割
    for (;; cp++) {
      if (*cp == ',' || !*cp) {
        std::string fstr = std::string(sp, cp - sp);
        feature_elements.push_back(fstr);
        if (!*cp) break;
        cp++;
        sp = cp;
      }
    }
    // 連結
    std::ostringstream oss;
    if (0 == feature_elements.at(3).compare(0, 1, "*")) {
      oss << feature_elements.at(0) << "-" << feature_elements.at(1) << "-" << feature_elements.at(2);
    } else {
      oss << feature_elements.at(0) << "-" << feature_elements.at(1) << "-" << feature_elements.at(2) << "-" << feature_elements.at(3);
    }
    return oss.str();
  }
      }
    }
    return std::string("");
    
  }
  
  /// @brief 形態素が地名語のどの部分になり得るか判定する。
  ///
  /// @arg @c phbsdef 地名接頭辞集合、地名語の先頭となり得る品詞集合、地名語の部分となり得る品詞集合等の定義
  /// @arg @c nextIsHead 素性シーケンス中、次の素性が地名語の先頭となり得るか
  void NodeExt::evaluatePossibility(const PHBSDefs& phbsdef, bool nextIsHead)
  {
    // MeCab のバグ回避：一部の記号が「名詞，サ変」になるので記号に置き換える
    static const std::string sahen = "名詞,サ変接続";
    if ((0 == this->feature.compare(0, sahen.length(), sahen)) &&
        (this->surface.substr(0, 3) == "－"
        || this->surface.substr(0, 3) == "～"
        || this->surface.substr(0, 3) == "♪"
        || this->surface.length() == 1)) {
      this->feature = "記号,一般,*,*,*,*,*";
      this->set_partOfSpeech("記号");
      this->set_subclassification1("一般");
      this->set_subclassification2("*");
    }

    // H(head)：「名詞,固有名詞,*」：地名語の先頭となり得る品詞集合 判定
    bHead = false;
    for ( std::vector<std::string>::const_iterator it = phbsdef.heads.begin(); it != phbsdef.heads.end(); it++){
      if ( 0 == feature.compare( 0, it->length(), *it)){
        bHead = true;
        break;
      }
    }
    // B(body)：「名詞,固有名詞,*, 名詞,接尾,地域,*, 名詞,数, *,... 地名語の部分となり得る品詞集合 判定
    bBody = false;
    for ( std::vector<std::string>::const_iterator it = phbsdef.bodies.begin(); it != phbsdef.bodies.end(); it++){
      if ( 0 == feature.compare( 0, it->length(), *it)){
        bBody = true;
        break;
      }
    }
    // 接尾辞の可能性判定
    bSuffix = false;
    if ( canBeBody()){
      for ( std::vector<Suffix>::const_iterator it = phbsdef.suffixes.begin(); it != phbsdef.suffixes.end(); it++){
        const std::string& s = it->get_surface();
        // 文字列長の確認を行う。素性が接尾辞に一致するような場合は除外する
        if ( s.length() >= surface.length()) continue;
        
        if ( 0 == surface.compare( surface.length() - s.length(), s.length(), s)){
          bSuffix = true;
          suffix = *it;
          break;
        }
      }
    }
    // 単独で地名語になり得ることの可能性判定
    bSingle = false;
    if ( canBeHead()){
      bSingle = true;
      for ( std::vector<std::string>::const_iterator it = phbsdef.extsingle.begin(); it != phbsdef.extsingle.end(); it++){
        if ( 0 == feature.compare( 0, it->length(), *it)){
          bSingle = false;
          break;
        }
      }
      if (bSingle) { // ブラックリストの地名語は単独で地名語にならない
        for (std::vector<std::string>::const_iterator it = phbsdef.non_geowords.begin(); it != phbsdef.non_geowords.end(); it++) {
          if (0 == surface.compare(0, it->length(), *it)) {
            bSingle = false;
            break;
          }
        }
      }
    }
    // 単独で地名語かそれ以外か併記する可能性判定
    bAlternative = false;
    for ( std::vector<std::string>::const_iterator it = phbsdef.alternatives.begin(); it != phbsdef.alternatives.end(); it++){
      if ( 0 == feature.compare( 0, it->length(), *it)){
        bAlternative = true;
        break;
      }
    }
    // X(stopper)：「名詞,一般,*」：地名語に続かない品詞集合 判定
    bStop = false;
    for ( std::vector<std::string>::const_iterator it = phbsdef.stoppers.begin(); it != phbsdef.stoppers.end(); it++){
      if ( 0 == feature.compare( 0, it->length(), *it)){
        bStop = true;
        break;
      }
    }
    if (bStop) {
      // ただし素性が空間語に一致するような場合は除外する
      for ( std::vector<std::string>::const_iterator it = phbsdef.spatials.begin(); it != phbsdef.spatials.end(); it++) {
        if ( *it == surface) {
          bStop = false;
          break;
        }
      }
    }
    // 地名語に先行しない語かどうかの判定
    bAntileader = false;
    for ( std::vector<std::string>::const_iterator it = phbsdef.antileaders.begin(); it != phbsdef.antileaders.end(); it++){
      if ( 0 == feature.compare( 0, it->length(), *it)){
        bAntileader = true;
        break;
      }
    }
  }
  
}
