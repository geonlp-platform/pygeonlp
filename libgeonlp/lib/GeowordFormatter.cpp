///
/// @file
/// @brief 形態素情報リストの出力形式定義クラス群の実装。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///
#include <sstream>
#include "GeowordFormatter.h"

namespace geonlp
{
	// 形態素情報リストを整形して文字列として返す。
	//
	// @arg @c nodelist 形態素情報リスト
	// @return 整形された形態素情報	
	std::string AbstructGeowordFormatter::formatNodeList(const std::vector<Node> & nodelist) 
	{
		std::ostringstream oss;
		for (std::vector<Node>::const_iterator it = nodelist.begin(); it != nodelist.end(); it++) {
			if ( it->get_partOfSpeech() == "BOS/EOS"){
				if ( it == nodelist.begin()){
				  oss << BOS();
				} else {
				  oss << EOS();
				}
			} else {
				oss << formatNode(*it) << std::endl;
			}
		}
		return oss.str();
	}
	
	const char *DefaultGeowordFormatter::delim = ",";
	
	/// @brief 形態素情報を整形して文字列として返す。
	///
	/// @arg @c node 形態素情報
	/// @return 整形された形態素情報
	std::string DefaultGeowordFormatter::formatNode(const Node & node) 
	{
		std::ostringstream oss;
		oss << node.get_surface() << "\t";
		oss << node.get_partOfSpeech() << delim;
		oss << node.get_subclassification1() << delim;
		oss << node.get_subclassification2() << delim;
		oss << node.get_subclassification3() << delim;
		oss << node.get_conjugatedForm() << delim;
		oss << node.get_conjugationType() << delim;
		oss << node.get_originalForm() << delim;
		oss << node.get_yomi() << delim;
		oss << node.get_pronunciation();
		return oss.str();
	}
	
	/// @brief BOSに対応する文字列を返す。
	///
	/// @return 整形されたBOS("")
	std::string DefaultGeowordFormatter::BOS()
	{
		return "\n";
	}
	
	/// @brief EOSに対応する文字列を返す。
	///
	/// @return 整形されたEOS("EOS")
	std::string DefaultGeowordFormatter::EOS()
	{
		return "EOS\n";
	}
	
	/// @brief 形態素情報を整形して文字列として返す。
	///
	/// @arg @c node 形態素情報
	/// @return 整形された形態素情報
	/// @note node-format-chasen = \%m\\t\%f[7]\\t\%f[6]\\t\%F-[0,1,2,3]\\t\%f[4]\\t\%f[5]\\n
	/// @todo Chasenフォーマットにあっているか確認
	std::string ChasenGeowordFormatter::formatNode(const Node & node) 
	{
		// node-format-chasen = %m\t%f[7]\t%f[6]\t%F-[0,1,2,3]\t%f[4]\t%f[5]\n
		std::ostringstream oss;
		oss << node.get_surface() << "\t";          // %m\t
		oss << (( node.get_yomi() != "*")? node.get_yomi(): "") << "\t";                // %f[7]\t
		oss << (( node.get_originalForm() != "*")? node.get_originalForm():"") << "\t"; // %f[6]\t
		oss << node.get_partOfSpeech();
		if ( node.get_subclassification1() != "*") oss << "-" << node.get_subclassification1();
		if ( node.get_subclassification2() != "*") oss << "-" << node.get_subclassification2();
		if ( node.get_subclassification3() != "*") oss << "-" << node.get_subclassification3();
		oss << "\t";                                // %F-[0,1,2,3]\t
		oss << (( node.get_conjugatedForm() != "*")? node.get_conjugatedForm(): "") << "\t";  // %f[4]\t
		oss << (( node.get_conjugationType() != "*")? node.get_conjugationType(): "");        // %f[5]
		return oss.str();
	}

	/// @brief BOSに対応する文字列を返す。
	///
	/// @return 整形されたBOS("")
	std::string ChasenGeowordFormatter::BOS()
	{
		return "";
	}
	
	/// @brief EOSに対応する文字列を返す。
	///
	/// @return 整形されたEOS("EOS")
	std::string ChasenGeowordFormatter::EOS()
	{
		return "EOS";
	}
}
