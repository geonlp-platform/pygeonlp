///
/// @file
/// @brief 見出し語IDに対応する地名語IDリストクラスWordListの定義。
///        MeCab 結果出力を生成する際に利用する
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///

#ifndef _WORDLIST_H
#define _WORDLIST_H

#include <string>
#include <vector>
#include <sstream>
#include "picojson.h"

namespace geonlp
{
  /// 地名語IDリストのエントリを表すクラス。
  class Wordlist {

  private:
    /// 見出し語ID (シリアル）
    /// 一つの単語リストエントリには複数の地名語が含まれるため
    /// geonlp_id は使えない
    unsigned int id;

    /// 標準化された表記
    std::string key;
    
    /// 見出し語（表記）
    std::string surface;

    /// 地名語IDリスト geonlp_id:代表表記/geonlp_id:代表表記/... 形式の文字列
    std::string idlist;

    /// 読み
    std::string yomi;

  public:
    /// コンストラクタ。
    Wordlist(): key(""), surface(""), idlist(""), yomi("") {}
  Wordlist(unsigned int id, const std::string& key, const std::string& surface, const std::string& idlist, const std::string& yomi):
    id(id), key(key), surface(surface), idlist(idlist), yomi(yomi) {}
    
    /// デストラクタ。
    ~Wordlist() {}
	
    /// 見出し語IDを設定する。
    inline void set_id(unsigned int id) { this->id = id; }

    /// 見出し語IDを得る。
    inline unsigned int get_id() const { return this->id; }

    /// 標準化表記を設定する。
    inline void set_key(const std::string& key) { this->key = key; }

    /// 標準化表記を得る。
    inline const std::string get_key() const { return this->key; }

    /// 見出し語（表記）を設定する。
    inline void set_surface(const std::string& surface) { this->surface = surface; }

    /// 見出し語（表記）を得る。
    inline const std::string get_surface() const { return this->surface; }

    /// 地名語IDリスト を設定する。
    inline void set_idlist(const std::string& idlist) { this->idlist = idlist; }

    /// 地名語IDリスト を得る。
    inline const std::string get_idlist() const { return this->idlist; }

    /// 読み を設定する。
    inline void set_yomi(const std::string& yomi) { this->yomi = yomi; }

    /// 読み を得る。
    inline const std::string get_yomi() const { return this->yomi; }

    /// デバグ用のテキスト表記を得る。
    inline std::string toString() const;

    /// 有効かどうか判断する。
    inline bool isValid(void) { return (this->surface.length() > 0); }
	
  };

  inline std::string Wordlist::toString() const {
    std::ostringstream oss;
    oss.str("");
    oss << this->id << "\t" << this->key << "\t" << this->surface << "\t" << this->idlist << "\t" << this->yomi;
    return oss.str();
  }

}

#endif
