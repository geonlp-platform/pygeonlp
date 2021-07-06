///
/// @file
/// @brief MeCabにアクセスするためのクラスの実装。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///
#include <iostream>
#include <fstream>

#include "MeCabAdapter.h"
#include "Node.h"
#include <mecab.h>


namespace geonlp
{
  /// @brief 初期化。
  ///
  /// @exception std::runtime_error ユーザ辞書ファイルが存在しない。あるいは MeCabの初期化に失敗した。
  void MeCabAdapter::initialize(const std::string& userdic, const std::string& system_dic_dir) {

    if (!userdic.empty()){
      // ファイルがない場合に例外
      // ファイルの存在確認
      std::ifstream ifs;
      ifs.open(userdic.c_str(), std::ifstream::in);
      if (ifs.fail()){
	throw std::runtime_error(std::string("Cannot open userdic file '") + userdic + "'. Use command line option '--rc' or set 'GEONLP_DIR environmental variable to specify the dictionary directory.");
      }
      ifs.close();
    }
    std::string initparam = "";
    if (!userdic.empty()) {
      initparam += std::string("--userdic=") + userdic;
    }
    if (!system_dic_dir.empty()) {
      if (!initparam.empty()) initparam += " ";
      initparam += std::string("--dicdir=") + system_dic_dir;
    }
    mecabp = MeCab::createTagger( initparam.c_str());
    if ( mecabp == NULL){
      throw std::runtime_error( MeCab::getTaggerError());
    }
  }
	
  /// @brief 終了処理。
  void MeCabAdapter::terminate() {
    if (mecabp) delete mecabp;
    mecabp = NULL;
  }
	
  /// @brief 引数として渡された自然文を形態素解析し、解析結果の各行を要素とするノードの配列を返す。
  ///
  /// @arg @c sentence 解析対象の自然文。
  /// @return 形態素情報のリスト。
  /// @exception MeCabNotInitializedException MeCabが未初期化。
  /// @exception MeCabErrException MeCabでエラー。
  MeCabAdapter::NodeList MeCabAdapter::parse(const std::string & sentence) {
			
    if ( mecabp ==NULL) throw MeCabNotInitializedException();
    const MeCab::Node *mecab_node = mecabp->parseToNode( sentence.c_str());
    if (! mecab_node) {
      throw MeCabErrException( mecabp->what());
    }
			
    MeCabAdapter::NodeList nodelist;
    for (;  mecab_node; mecab_node = mecab_node->next) {
      Node node( std::string( mecab_node->surface, mecab_node->length), mecab_node->feature);
      nodelist.push_back(node);
    }
    return nodelist;
  }
}
