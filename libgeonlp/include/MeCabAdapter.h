///
/// @file
/// @brief MeCabにアクセスするためのクラスの定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///

#ifndef _MECABADAPTER_H
#define _MECABADAPTER_H

#include <list>
#include <boost/shared_ptr.hpp>
#include <mecab.h>
#include "Exception.h"

namespace MeCab{
	class Tagger;
}

namespace geonlp
{
	
	class Node;

	/// @brief MeCabにアクセスするためのクラス。
	class MeCabAdapter {

	public:
		/// @brief @link parse() @endlinkの戻り値型定義。
		typedef std::list<Node> NodeList;
		
		/// @brief コンストラクタ。
		MeCabAdapter(): mecabp(NULL) {};

		// 初期化。
		/// @arg @c userdic ユーザ辞書ファイル名
		/// @arg @c system_dic_dir システム辞書ディレクトリ
		void initialize(const std::string& userdic, const std::string& system_dic_dir);

		// 終了処理。
		void terminate();
	
	private:
		/// @brief MeCabのハンドラ。
		MeCab::Tagger* mecabp;
		
		/// @brief ユーザ辞書名
		std::string userdic;


	public:
		// パースする。
		NodeList parse(const std::string & sentence);

	};
	
	typedef boost::shared_ptr<MeCabAdapter> MeCabAdapterPtr;
}
#endif
