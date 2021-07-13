///
/// @file
/// @brief ユーティリティクラスの定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///

#ifndef _UTIL_H
#define _UTIL_H

#include <stdexcept>
#include <string>
#include <vector>
#include <boost/regex.hpp>

namespace geonlp
{
  /// @brief 例外クラス
  class UtilException : public std::runtime_error{
  public:
  UtilException(const std::string& message): std::runtime_error(message) {}
    ~UtilException() throw() {}
  };

  /// @brief ユーティリティクラス。
  ///
  class Util {
  private:
    static boost::regex pattern_url;

  public:
    // ひらがなカタカナのみからなる文字列であればカタカナに変換して返す。
    static std::string checkKana( const std::string& );
		
    // 引数文字列をデリミタで区切って文字列の配列として返す。
    static void explode( const std::string& src, std::vector<std::string>& strlist, const char delim = ',');

    // 経緯度で表された二点間の直線距離を計算する
    static double latlonDist(const double& lat0, const double& lon0, const double& lat1, const double& lon1);

    // URL を分解する
    // 分解した結果は result に格納される
    // 0 - url 全体
    // 1 - scheme
    // 2 - server
    // 3 - port
    // 4 - path (full)
    // 5 - path
    // 6 - param
    static bool split_url(const std::string& url, std::vector<std::string>& result);

    // ファイルが存在するかどうか調べる
    // 存在していれば true, なければ false
    static bool fileExists(const std::string& path);

  };
	
}
#endif
