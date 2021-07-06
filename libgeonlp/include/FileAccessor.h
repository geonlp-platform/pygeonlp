///
/// @file
/// @brief Fileアクセスクラス FileAccessorの定義
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///

#ifndef _FILE_ACCESSOR_H
#define _FILE_ACCESSOR_H

#include <string>
#include "DBAccessor.h"

namespace geonlp
{	
  ///
  /// @brief File にアクセスするためのクラス。
  ///
  class FileAccessor {
  private:
    const DBAccessor* _dbap;

  public:
    /// @brief コンストラクタ。
    FileAccessor(const DBAccessor& dba) { this->_dbap = &dba; } // リファレンスポインタを保持, 解放不要

    // 辞書 CSV ファイルから地名語と辞書情報を読み込む
    // 読み込んだ件数を返す
    int importDictionaryCSV(const std::string& csvfilename, const std::string& txtfilename) const;
  };

}
#endif
