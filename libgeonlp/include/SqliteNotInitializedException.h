///
/// @file
/// @brief 例外の定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///

#ifndef _SQLITE_NOT_INITIALIZED_EXCEPTION_H
#define _SQLITE_NOT_INITIALIZED_EXCEPTION_H

#include <stdexcept>

namespace geonlp
{
	/// Sqlite3が初期化されていないことを示す例外。
	class SqliteNotInitializedException : public std::runtime_error {
	public:
		SqliteNotInitializedException(): runtime_error("Sqlite not initialized.")
		{
		}
	};
}
#endif
