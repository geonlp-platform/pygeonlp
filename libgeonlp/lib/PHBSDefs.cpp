///
/// @file
/// @brief 地名接頭辞集合、地名語の先頭となり得る品詞集合、地名語の部分となり得る品詞集合等を定義するクラスの実装。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///
#include <iostream>
#include <fstream>
#include "PHBSDefs.h"

namespace geonlp
{
	///
	/// 地名語の先頭となり得る品詞集合、地名語の部分となり得る品詞集合、地名語の先頭となり得る品詞のうち、単独で地名語になり得ない品詞集合
	/// を定義する。
	/// @note それぞれの品詞集合を変更する場合は、この関数の実装を変更する。
	PHBSDefs::PHBSDefs() 
	{
		// H(head)：地名語の先頭となり得る品詞集合を定義
		heads.push_back("名詞,固有名詞");
		heads.push_back("名詞,サ変接続");
		heads.push_back("名詞,一般");
		heads.push_back("名詞,副詞可能");
		heads.push_back("接続詞");
		// B(body)：地名語の部分となり得る品詞集合を定義
		bodies.push_back("名詞,固有名詞");
		bodies.push_back("名詞,サ変接続");
		bodies.push_back("名詞,一般");
		bodies.push_back("名詞,副詞可能");
		bodies.push_back("名詞,接尾,地域");
		bodies.push_back("名詞,数");
		bodies.push_back("名詞,接尾,助数詞");
		bodies.push_back("名詞,接尾,一般");
		bodies.push_back("接頭詞,名詞接続");
		bodies.push_back("接頭詞,数接続");
		bodies.push_back("助詞,連体化");
		// Hのうち、単独で地名語になり得ない品詞集合を定義
		// extsingle.push_back("名詞,固有名詞,人名");
		// 一語の場合、地名またはそれ以外の可能性を併記する品詞集合
		alternatives.push_back("名詞,固有名詞,人名");
		alternatives.push_back("名詞,固有名詞,組織");
		alternatives.push_back("名詞,固有名詞,一般");
		alternatives.push_back("名詞,形容動詞語幹");
		alternatives.push_back("名詞,副詞可能");
		alternatives.push_back("名詞,サ変接続");
		alternatives.push_back("名詞,一般");
		alternatives.push_back("接続詞");
		alternatives.push_back("動詞,自立");
		alternatives.push_back("形容詞,自立");
		alternatives.push_back("接頭詞,名詞接続");
		// X(stopper): 地名語に続かない品詞集合を定義
		// stoppers.push_back("名詞,固有名詞,人名");
		stoppers.push_back("名詞,固有名詞,組織");
		stoppers.push_back("名詞,固有名詞,一般");
		stoppers.push_back("名詞,サ変接続");
		stoppers.push_back("名詞,一般");
		stoppers.push_back("名詞,形容動詞語幹");
		stoppers.push_back("名詞,接尾,地域"); // 接尾付きで地名語登録
		stoppers.push_back("名詞,接尾,一般");
		// stoppers.push_back("名詞,接尾,人名");
		// stoppers.push_back("名詞,固有名詞,人名,名");
		// Q(antileader): 地名語に先行しない品詞集合を定義
		antileaders.push_back("名詞,サ変接続");
		// antileaders.push_back("名詞,一般");
		antileaders.push_back("名詞,形容動詞語幹");
		// antileaders.push_back("名詞,接尾,地域"); // 接尾付きで地名語登録 -> 直前の地名が未登録の可能性もある
		antileaders.push_back("名詞,接尾,一般");
	};
	
	/// @brief 地名接頭辞集合および地名接尾辞集合をプロファイルから読み込む。
	///
	/// @arg @c profile プロファイル
	void PHBSDefs::readProfile(const Profile& profile) {
		suffixes = profile.get_suffix();
		spatials = profile.get_spatial();
		non_geowords = profile.get_non_geoword();
	}
}

