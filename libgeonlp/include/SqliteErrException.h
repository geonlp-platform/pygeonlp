///
/// @file
/// @brief 例外の定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///

#ifndef _SQLITE_ERR_EXCEPTION_H
#define _SQLITE_ERR_EXCEPTION_H

#include <stdexcept>

namespace geonlp
{
	/// @brief Sqlite3のエラーが生じたことを示す例外。
	///
	/// Sqlite3のリターンコードとエラーメッセージが設定される。
	class SqliteErrException : public std::runtime_error {
	public:
		int rc; ///< sqlite3のリターンコード
		SqliteErrException( int c, const char* msg): runtime_error(msg), rc(c)
		{
		}
	};
}
#endif
