///
/// @file
/// @brief 形態素情報リストの出力形式定義クラス群の定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///

#ifndef _GEOWORDFORMATTER_H
#define _GEOWORDFORMATTER_H

#include <vector>
#include <string>
#include "Node.h"

namespace geonlp
{
	/// @brief 形態素情報リストの出力形式定義抽象クラス。
	class AbstructGeowordFormatter {
	public:
		/// @brief 形態素情報を整形して文字列として返す。
		///
		/// @arg @c node 形態素情報
		/// @return 整形された形態素情報
		virtual std::string formatNode(const Node & node) = 0;

		/// @brief 形態素情報リストを整形して文字列として返す。
		///
		/// @arg @c nodelist 形態素情報リスト
		/// @return 整形された形態素情報
		std::string formatNodeList(const std::vector<Node> & nodelist);

		/// @brief BOSに対応する文字列を返す。
		///
		/// @return 整形されたBOS
		virtual std::string BOS() = 0;

		/// @brief EOSに対応する文字列を返す。
		///
		/// @return 整形されたEOS
		virtual std::string EOS() = 0;
                
	  virtual ~AbstructGeowordFormatter() {};

	};

	/// @brief 形態素情報リストの出力形式定義クラス。
	///
	/// MeCabのデフォルト出力に準じた形式で出力する。
	class DefaultGeowordFormatter : public AbstructGeowordFormatter {
		static const char *delim;
	public:
		std::string formatNode(const Node & node);

		std::string BOS();
		
		std::string EOS();
		
	};

	/// @brief 形態素情報リストの出力形式定義クラス(chasenフォーマット)。
	///
	/// chasenフォーマットに準じた形式で出力する。
	class ChasenGeowordFormatter : public AbstructGeowordFormatter {
	public:
		std::string formatNode(const Node & node);
	
		std::string BOS();
		
		std::string EOS();
	};
}
#endif
