///
/// @file
/// @brief 例外の定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2013, NII
///

#ifndef _FORMAT_EXCEPTION_H
#define _FORMAT_EXCEPTION_H

#include <stdexcept>

namespace geonlp
{
  /// 読み込んだデータ（Geoword, Dictionary等）のフォーマット異常
  class FormatException : public std::runtime_error {
  public:
    FormatException(): runtime_error("Data format is not valid.") {}
    FormatException(const std::string& message): runtime_error(message.c_str()) {}
  };
}
#endif
