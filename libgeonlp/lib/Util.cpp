///
/// @file
/// @brief ユーティリティクラスの実装。
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///
#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif /* _USE_MATH_DEFINES */
#include <sys/stat.h>
#include <cmath>
#include <sstream>
#include "Util.h"

namespace
{
  struct TmpArray{
    unsigned char* p;
    TmpArray( const std::string& src): p(NULL){
      p = new unsigned char[src.length()];
    };
    ~TmpArray(){
      delete[] p;
    };
  };
}

namespace geonlp
{
  boost::regex Util::pattern_url("(https?)://(.+?)?:?(\\d+)?((/.*?)([&?=#!].*)?)$", boost::regex::perl | boost::regex::icase);

  /// @brief 引数がカタカナとひらがなのみの場合、ひらがなをカタカナに変換した文字列を返す。
  ///
  /// 引数にカタカナひらがな意外の文字が含まれている場合には空文字列を返す。
  /// @arg @c src 変換対象の文字列
  /// @return カタカナに変換された文字列（あるいは空文字列）
  /// @note UTF8前提のコードである。
  std::string Util::checkKana( const std::string& src)
  {
    std::string emptystring;
    if ( src.length() % 3 != 0) return emptystring;
    ::TmpArray ta( src);
    const unsigned char* ucp = reinterpret_cast<const unsigned char*>(src.data());
    for ( size_t i = 0; i< src.length(); i += 3){
      if ( ucp[i] != 0xE3) return emptystring;
      ta.p[i]= ucp[i];
      switch( ucp[i+1]){
      case 0x81:
	if ( 0x81 <= ucp[i+2] && ucp[i+2] <= 0x9F){
	  // ぁ〜た
	  ta.p[i+1]= 0x82;
	  ta.p[i+2]= ucp[i+2] - 0x81 + 0xA1;
	}else if ( 0xA0 <= ucp[i+2] && ucp[i+2] <= 0xBF){
	  // だ〜み
	  ta.p[i+1]= 0x83;
	  ta.p[i+2]= ucp[i+2] - 0xA0 + 0x80;
	}else{
	  return emptystring;
	}
	break;
      case 0x82:
	if ( (0x80 <= ucp[i+2] && ucp[i+2] <= 0x96) || (0x9D <= ucp[i+2] && ucp[i+2] <= 0x9F)){
	  // む〜んゔゕゖ || ゝゞ	ゟ
	  ta.p[i+1]= 0x83;
	  ta.p[i+2]= ucp[i+2] - 0x80 + 0xA0;
	}else if ( 0xA0 <= ucp[i+2] && ucp[i+2] <= 0xBF){
	  // ゠ァ〜タ
	  ta.p[i+1]= ucp[i+1];
	  ta.p[i+2]= ucp[i+2];
	}else if ( 0x99 <= ucp[i+2] && ucp[i+2] <= 0x9C){
	  // ゛゜
	  ta.p[i+1]= ucp[i+1];
	  ta.p[i+2]= ucp[i+2];
	}else{
	  return emptystring;
	}
	break;
      case 0x83:
	if ( 0x80 <= ucp[i+2] && ucp[i+2] <= 0xBF){
	  // ダ〜ヶヷヸヹヺ・ーヽヾヿ
	  ta.p[i+1]= ucp[i+1];
	  ta.p[i+2]= ucp[i+2];
	}else{
	  return emptystring;
	}
	break;
      case 0x87:
	if ( 0xB0 <= ucp[i+2] && ucp[i+2] <= 0xBF){
	  // ㇰㇱㇲㇳㇴㇵㇶㇷㇸㇹㇺㇻㇼㇽㇾㇿ(Unicode 片仮名の音声用用拡張)
	  ta.p[i+1]= ucp[i+1];
	  ta.p[i+2]= ucp[i+2];
	}else{
	  return emptystring;
	}
	break;
      default:
	return emptystring;
      }
    }
    return std::string( reinterpret_cast<const char*>(ta.p), src.length());
  }
	
  /// @brief 引数文字列をデリミタで区切って文字列の配列として返す。
  ///
  /// @arg @c src [in] 入力文字列
  /// @arg @c strlist [out] 分解された文字列の配列
  /// @arg @c delim デリミタとなるキャラクタ
  void Util::explode( const std::string& src, std::vector<std::string>& strlist, const char delim)
  {
    std::vector<std::string>::size_type delimpos;
    std::string temp = src;
    strlist.clear();
    while( (delimpos = temp.find_first_of(delim)) != temp.npos )
      {
	if(delimpos > 0)
	  {
	    strlist.push_back(temp.substr(0, delimpos));
	  }
	temp = temp.substr(delimpos + 1);
      }
    if(temp.length() > 0)
      {
	strlist.push_back(temp);
      }
  }

  /// @brief 経緯度で表された二点間の直線距離を計算する
  /// cf. http://yamadarake.jp/trdi/report000001.html
  ///
  /// 引数に不正な経緯度値が含まれている場合には例外 UtilException を発生する
  /// @arg @c lat0, lon0, lat1, lon1 二点の緯度、経度
  /// @return 直線距離（単位：km）
  /// @note ヒュベニの公式なので、精度は 1/1000 程度（1kmに対して1m以内の誤差）
  double Util::latlonDist(const double& lat0, const double& lon0, const double& lat1, const double& lon1) {
    if (lat0 > 90.0 || lat0 < -90.0) {
      std::stringstream sstr;
      sstr << "The 1st latitude value is invalid (" << lat0 << ").";
      throw UtilException(sstr.str());
    }
    if (lat1 > 90.0 || lat1 < -90.0) {
      std::stringstream sstr;
      sstr << "The 2nd latitude value is invalid (" << lat1 << ").";
      throw UtilException(sstr.str());
    }
    
    // ラジアンに変換
    double x0 = lon0 * M_PI / 180.0;
    double y0 = lat0 * M_PI / 180.0;
    double x1 = lon1 * M_PI / 180.0;
    double y1 = lat1 * M_PI / 180.0;
    
    // 二点間の平均緯度、緯度差、経度差
    double ave_lat   = (y0 + y1) / 2.0;
    double delta_lat = (y1 - y0);
    double delta_lon = (x1 - x0);

    // 子午線曲率半径
    // 半径 a(1- e^2) = 6,335.439 km
    // 離心率^2 0.00669438
    double large_w = sqrt(1.0 - 0.00669438 * sin(ave_lat) * sin(ave_lat));
    double large_m = 6335.439 / (large_w * large_w * large_w);

    // 卯酉線曲率半径
    // 半径を 6378.137 km
    // 離心率を 0.00669438
    double large_n = 6378.137 / large_w;

    // Hubeny の簡易式
    double x = delta_lat * large_m;
    double y = delta_lon * large_n * cos(ave_lat);
    double dist = sqrt(x * x + y * y);
    return dist;
  }
  
  bool Util::split_url(const std::string& url, std::vector<std::string>& result) {
    boost::smatch what;
    result.clear();
    if (!regex_match(url, what, Util::pattern_url)) {
      return false;
    }
    for (int i = 0; i < 7; i++) {
      result.push_back(std::string(what[i].first, what[i].second));
    }
    return true;
  }

  /// @brief ファイルの存在チェック
  /// @arg @c path  ファイルパス（相対または絶対）
  /// @return true if path exists
  bool Util::fileExists(const std::string& path) {
    static struct stat st_stat;
    int result;

    result = stat(path.c_str(), &st_stat);
    if (result == 0) {
      return true;
    }

    return false;
  }

}
