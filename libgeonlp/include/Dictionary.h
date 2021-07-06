///
/// @file
/// @brief テーマクラス Dictionary の定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///

#ifndef _DICTIONARY_H
#define _DICTIONARY_H

#include <string>
#include "picojsonExt.h"

namespace geonlp
{
  class Dictionary : public picojson::ext {
  private:

  public:
    /// コンストラクタ
    Dictionary() { this->clear(); }
    
    /// 初期化
    void clear() { this->initByJson("{}"); }

    /// JSON からオブジェクトを復元する
    static Dictionary fromJson(const std::string& json_str);

    /// 必須項目が揃っていることを確認する
    bool isValid(void) const;
    bool isValid(std::string& err) const;
	
    /// 定義済み項目についてはメソッドを用意し、型のチェックを行う

    // 辞書識別子
    const std::string get_identifier(void) const; //{ return this->_get_string("identifier"); }

    // 辞書名
    inline std::string get_name() const { return this->_get_string("name"); }

    // キーワード
    inline std::vector<std::string> get_keywords() const { return this->_get_string_list("keywords"); }

    // 辞書説明
    inline std::string get_description() const { return this->_get_string("description"); }

    // URL
    inline std::string get_url() const { return this->_get_string("url"); }

    // CSV URL
    const std::string get_content_url() const;

    // 修正日時
    inline std::string get_date_modified() const { return this->_get_string("dateModified"); }

    // レコード数
    inline std::string get_size() const { return this->_get_string("size"); }
  };

}

#endif
