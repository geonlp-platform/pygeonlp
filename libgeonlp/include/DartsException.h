///
/// @file
/// @brief 例外の定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2013, NII
///

#ifndef _DARTS_EXCEPTION_H
#define _DARTS_EXCEPTION_H

#include <stdexcept>

namespace geonlp
{
  /// DARTS ファイル読み書きでの例外
  class DartsException : public std::runtime_error {
  public:
    DartsException(): runtime_error("Darts file access error.") {}
    DartsException(const std::string& message): runtime_error(message.c_str()) {}
  };
}
#endif
