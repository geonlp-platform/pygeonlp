///
/// @file
/// @brief 地名語抽出API(インタフェース)実装クラスの実装。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///
#include <iostream>
#include <fstream>
#include <sstream>
#include <list>
#include <boost/lexical_cast.hpp>
#include <boost/regex.hpp>
#include <boost/algorithm/string.hpp>
#include "config.h"
#include "GeonlpMA.h"
#include "GeonlpMAImplSq3.h"
#include "Node.h"
#include "NodeExt.h"
#include "Geoword.h"
#include "MeCabAdapter.h"
#include "DBAccessor.h"
#include "Profile.h"
#include "Suffix.h"
#include "GeowordFormatter.h"
#include "FileAccessor.h"
#ifdef HAVE_LIBDAMS
#include <dams.h>
#endif /* HAVE_LIBDAMS */

namespace geonlp
{
	
  /// 設定項目で '-' から始まる場合に除外、それ以外は追加の形式の要素を処理し、
  /// 追加される項目だけもしくは除外される項目だけのリストを作る
  /// @arg    add_list    追加される項目のリスト
  /// @arg    remove_list 除外される項目のリスト
  /// @return 追加の場合は 1, 除外の場合は -1
  static int _getAddRemoveList(const std::vector<std::string>& args, std::vector<std::string>& add_list, std::vector<std::string>& remove_list) {
    add_list.clear();
    remove_list.clear();
    for (std::vector<std::string>::const_iterator it = args.begin(); it != args.end(); it++) {
      const char* p = (*it).c_str();
      if (*p == '-') {
	add_list.push_back(std::string(p + 1));
      } else {
	remove_list.push_back(*it);
      }
    }
    
    int retval = 0;
    if (add_list.size() > 0) {
      retval = 1;
      std::vector<std::string> result;
      // 追加項目が存在する場合、追加項目 - 除外項目 のリストを作成
      for (std::vector<std::string>::iterator it = add_list.begin(); it != add_list.end(); it++) {
	std::string candidate = (*it);
	for (std::vector<std::string>::iterator it2 = remove_list.begin(); it2 != remove_list.end(); it2++) {
	  if (candidate == (*it2)) {
	    candidate = "";
	    break;
	  }
	}
	if (candidate != "") result.push_back(candidate);
      }
      add_list = result;
      remove_list.clear();
    } else {
      retval = -1;
    }
    return retval;
  }

  /// @brief コンストラクタ。
  ///
  /// 地名接頭辞集合および地名接尾辞集合を、それぞれ定義ファイルから読み込む。
  /// 
  /// 利用する形態素情報リストの出力形式定義クラスを決定する。
  /// 
  /// 地名接頭辞集合および地名接尾辞集合の定義、形態素情報リストの出力形式定義クラス名はプロファイル定義ファイルから読み込む。
  /// @arg @c mp  MeCabにアクセスするためのクラスへのポインタ
  /// @arg @c dp  SQLiteにアクセスするためのクラスへのポインタ
  /// @arg @c profilesp  プロファイル読み込みクラスへのポインタ
  /// @exception std::runtime_error プロファイル定義ファイルにキーが存在しない。
  /// @note プロファイル定義ファイル中での出力形式定義クラス名が期待されていない文字列だった場合には"DefaultGeowordFormatter"が指定されたものとする。
  MAImpl::MAImpl(ProfilePtr profilesp): formatter()
  {
    this->profilep = profilesp;
    
    // MeCabAdapterの初期化
    try{
      std::string userdic = profilesp->get_mecab_userdic();
      std::string system_dic_dir = profilesp->get_system_dic_dir();
      // Mecab ユーザ辞書が存在するかどうか確認
      std::ifstream s_in;
      s_in.open((const char*)(userdic.c_str()));
      if (!s_in) userdic = std::string("");
      this->mecabp = MeCabAdapterPtr(new MeCabAdapter());
      this->mecabp->initialize(userdic, system_dic_dir);
    } catch (std::runtime_error& e){
      throw ServiceCreateFailedException( e.what(), ServiceCreateFailedException::MECAB);
    }

    // DBAccessorの初期化
    // std::string dbfilename;
    try{
      this->dbap = DBAccessorPtr(new DBAccessor(*profilesp));
      this->dbap->open();
    }catch( std::runtime_error& e){
      throw ServiceCreateFailedException( e.what(), ServiceCreateFailedException::SQLITE);
    }
		
    // Dartsの初期化
    std::string darts;
    try {
      darts = profilesp->get_darts_file();
      if (darts.length() > 0) {
	FILE* fp = fopen(darts.c_str(), "r");
	if (fp != NULL) {
	  fclose(fp);
	  this->dap = DoubleArrayPtr(new Darts::DoubleArray());
	  this->dap->open(darts.c_str());
	}
      }
    } catch (std::runtime_error& e) {
      throw ServiceCreateFailedException(e.what(), ServiceCreateFailedException::DARTS);
    }

    // prefixおよびsuffixの読み込み
    phbsDefs.readProfile(*profilesp);
		
    std::string formattername = profilesp->get_formatter();
    if ( formattername == "DefaultGeowordFormatter" || formattername == ""){
      formatter = GeowordFormatterPtr(new DefaultGeowordFormatter());
    }else if ( formattername == "ChasenGeowordFormatter"){
      formatter = GeowordFormatterPtr(new ChasenGeowordFormatter());
    }else {
      // 期待されていない文字列だった場合には"DefaultGeowordFormatter"が指定されたものとする
      formatter = GeowordFormatterPtr(new DefaultGeowordFormatter());
    }

    // 利用する辞書とクラスをプロファイルから読み込み
    std::vector<std::string> add_list;
    std::vector<std::string> remove_list;
    std::stringstream ss;
    int v = 0;

    // 辞書は ID の配列で指定する
    this->defaultDictionaries.clear();
    int res = _getAddRemoveList(profilesp->get_dictionary(), add_list, remove_list);
    if (res > 0) { // 利用する辞書IDが指定されている場合、指定された辞書だけ利用する
      Dictionary dictionary;
      for (std::vector<std::string>::iterator it = add_list.begin(); it != add_list.end(); it++) {
	ss.str("");
	ss << (*it);
	ss >> v;
	if (this->getDictionaryById(v, dictionary)) this->defaultDictionaries[v] = dictionary;
      }
    } else { // 利用しない辞書IDが指定されている場合、全辞書から除外する
      this->getDictionaryList(this->defaultDictionaries);
      for (std::vector<std::string>::iterator it = remove_list.begin(); it != remove_list.end(); it++) {
	ss.str("");
	ss << (*it);
	ss >> v;
	this->defaultDictionaries.erase(v);
      }
    }

    // クラスは正規表現の配列で指定する
    this->defaultClasses = profilesp->get_ne_class();

    // アクティブな辞書とクラスをデフォルト値からコピーする
    this->resetActiveDictionaries();
    this->resetActiveClasses();
  }
	
  /// @brief デストラクタ。
  MAImpl::~MAImpl()
  {
    if ( mecabp.get()){
      mecabp->terminate();
    }
    if ( dbap.get()){
      dbap->close();
    }
    if (dap.get()) {
      ; // darts はクローズ処理不要？
    }
#ifdef HAVE_LIBDAMS
    damswrapper::final();
#endif /* HAVE_LIBDAMS */
    // std::cerr << "MAImplSq3 destructed." << std::endl;
  }

  /// @brief ID で指定した辞書情報を取得する
  bool MAImpl::getDictionaryById(int dictionary_id, Dictionary& ret) const {
    return this->dbap->getDictionaryById(dictionary_id, ret);
  }

  /// @brief identifier で指定した辞書情報を取得する
  bool MAImpl::getDictionary(const std::string&  identifier, Dictionary& ret) const {
    return this->dbap->getDictionary(identifier, ret);
  }

  /// @brief 内部 ID で指定した辞書の identifier を取得する
  const std::string MAImpl::getDictionaryIdentifierById(int dictionary_id) const {
    Dictionary dic;
    if (! this->getDictionaryById(dictionary_id, dic)) {
      return std::string("");
    }
    return dic.get_identifier();
  }

  /// @brief 辞書一覧を取得する
  int MAImpl::getDictionaryList(std::map<int, Dictionary>& ret) const {
    this->dbap->getDictionaryList(ret);
    return ret.size();
  }

  /// @brief 利用する辞書を指定する
  /// @arg @c dics   利用する辞書のIDリスト
  ///                空の場合、登録されている全辞書を利用する
  void MAImpl::setActiveDictionaries(const std::vector<int>& dics) {
    this->activeDictionaries.clear();
    if (dics.size() == 0) {
      this->getDictionaryList(this->activeDictionaries);
    } else {
      this->addActiveDictionaries(dics);
    }
  }

  /// @brief 利用する辞書をリセットする（デフォルトに戻す）
  void MAImpl::resetActiveDictionaries() {
    this->activeDictionaries = this->defaultDictionaries;
  }

  /// @brief 利用する辞書を追加する
  /// @arg @c dics 追加する辞書IDのリスト
  void MAImpl::addActiveDictionaries(const std::vector<int>& dics) {
    Dictionary dictionary;
    for (std::vector<int>::const_iterator it = dics.begin(); it != dics.end(); it++) {
      if (this->getDictionaryById((*it), dictionary)) this->activeDictionaries[(*it)] = dictionary;
    }
  }

  /// @brief 利用する辞書から除外する
  /// @arg @c dics 除外する辞書IDのリスト
  void MAImpl::removeActiveDictionaries(const std::vector<int>& dics) {
    for (std::vector<int>::const_iterator it = dics.begin(); it != dics.end(); it++) {
      this->activeDictionaries.erase((*it));
    }
  }

  /// @brief 利用している辞書を返す
  const std::map<int, Dictionary>& MAImpl::getActiveDictionaries(void) const {
    return this->activeDictionaries;
  }

  /// @brief 利用するクラス正規表現を指定する
  void MAImpl::setActiveClasses(const std::vector<std::string>& ne_classes) {
    this->activeClasses = ne_classes;
  }

  /// @brief 利用する固有名クラスの正規表現を追加する
  /// @arg @c ne_classes 追加するクラスの正規表現リスト
  void MAImpl::addActiveClasses(const std::vector<std::string>& ne_classes) {
    for (std::vector<std::string>::const_iterator it = ne_classes.begin(); it != ne_classes.end(); it++) {
      bool is_exist = false;
      for (std::vector<std::string>::iterator it2 = this->activeClasses.begin(); it2 != this->activeClasses.end(); it2++) {
	if (*it2 == *it) {
	  is_exist = true;
	  break;
	}
      }
      if (!is_exist) this->activeClasses.push_back((*it));
    }
  }

  /// @brief 利用する固有名クラスの正規表現を除外する
  /// @arg @c ne_classes 除外するクラスの正規表現リスト
  void MAImpl::removeActiveClasses(const std::vector<std::string>& ne_classes) {
    for (std::vector<std::string>::const_iterator it = ne_classes.begin(); it != ne_classes.end(); it++) {
      for (std::vector<std::string>::iterator it2 = this->activeClasses.begin(); it2 != this->activeClasses.end(); it2++) {
	if (*it2 == *it) {
	  this->activeClasses.erase(it2);
	  break;
	}
      }
    }
  }

  /// @brief 利用するクラス正規表現をリセットする（デフォルトに戻す）
  void MAImpl::resetActiveClasses() {
    this->activeClasses = this->defaultClasses;
  }

  /// @brief 利用しているクラス正規表現のリストを返す
  const std::vector<std::string>& MAImpl::getActiveClasses() const {
    return this->activeClasses;
  }
	
  /// @brief 引数として渡された自然文を形態素解析し、解析結果をテキストとして返す。
  ///
  /// 解析結果テキストの書式は、プロファイル定義ファイルでの指定に従う。
  /// @arg @c sentence 解析対象の自然文。
  /// @return 解析結果としてのテキスト。
  /// @exception SqliteNotInitializedException Sqlite3が未初期化。
  /// @exception MeCabNotInitializedException MeCabが未初期化。
  /// @exception SqliteErrException Sqlite3でエラー。
  /// @exception MeCabErrException MeCabでエラー。	
  std::string MAImpl::parse(const std::string & sentence) const
  {
    std::ostringstream oss;
    std::vector<Node> nodelist; 
    this->parseNode(sentence, nodelist);
    return formatter->formatNodeList(nodelist);
  }
	
  /// @brief 引数として渡された自然文を形態素解析し、解析結果の各行を要素とするノードの配列を返す。
  ///
  /// @arg @c sentence 解析対象の自然文。
  /// @arg ret 解析結果。形態素情報クラスの配列。 
  /// @return 結果のノード数
  /// @exception SqliteNotInitializedException Sqlite3が未初期化。
  /// @exception MeCabNotInitializedException MeCabが未初期化。
  /// @exception SqliteErrException Sqlite3でエラー。
  /// @exception MeCabErrException MeCabでエラー。	
  int MAImpl::parseNode(const std::string & sentence, std::vector<Node>& ret) const
  {
    // 改行コードをエスケープする
    std::string sentence_for_mecab("");
    int pos = 0, offset = 0;
    for (;;) {
      pos = sentence.find("\n", offset);
      if (pos == int(std::string::npos)) {
	sentence_for_mecab += sentence.substr(offset, pos - offset);
	break;
      } else {
	sentence_for_mecab += sentence.substr(offset, pos - offset) + "\\n";
	offset = pos + 1;
      }
    }
    // MeCabでパースする
    std::list<Node> nodes = mecabp->parse(sentence_for_mecab);
    for (std::list<Node>::iterator it = nodes.begin(); it != nodes.end(); it++) {
      std::string surface = (*it).get_surface();
      if (surface != "\\") continue;
      std::list<Node>::iterator it_next = it; it_next++;
      if (it_next == nodes.end()) break;
      std::string next_surface = (*it_next).get_surface();
      if (next_surface.at(0) == 'n') {
	if (next_surface.length() > 1) {
	  (*it_next).set_surface(next_surface.substr(1));
	} else {
	  nodes.erase(it_next);
	}
	(*it) = Node("\n", "記号,制御コード,改行,*,*,*");
	//	(*it).set_partOfSpeech("記号");
	//	(*it).set_subclassification1("制御コード");
	//	(*it).set_subclassification2("改行");
      }
    }
    ret.clear();
    ret.reserve(nodes.size()); 
    // MeCabによるパース結果を地名語辞書を参照して変換する
    convertMeCabNodeToNodeList(nodes, ret);
    return ret.size();
  }
	
  /// @brief MeCabによるパース結果を地名語辞書を参照して変換する。
  ///
  /// @arg @c nodes [in] MeCabによるパース結果としての、形態素情報リスト。
  /// @arg @c nodelist [out] 地名語辞書を参照して地名語変換を行った後の形態素情報リスト。
  void MAImpl::convertMeCabNodeToNodeList( NodeList& nodes, std::vector<Node>& nodelist) const
  {
    nodelist.clear();
    NodeExtList nodeExts;
    NodeExtList::iterator it;
    NodeExt* lastNode = NULL;

    // 形態素情報クラスのリストを、形態素情報拡張クラスのリストに変換する。
    nodeListToNodeExtList( nodes, nodeExts);

    if ( nodeExts.size() > 0){
      it = nodeExts.end();
      bool nextIsHead = false;
      do {
        it--;
        // PHBSになり得るか判定しておく
        it->evaluatePossibility( phbsDefs, nextIsHead);
        nextIsHead = it->canBeHead();
        // std::cout << it->toString() << std::endl;
      } while( it != nodeExts.begin());
    }

    it = nodeExts.begin();
    while( it != nodeExts.end()){
      NodeExtList::iterator ex;
      NodeExtList::iterator s, e;

      // 最長の地名語候補を得る。
      getLongestGeowordCandidate( it, nodeExts.end(), ex, s, e);

      // 地名語候補にならないnodeはそのままpush_back
      if (ex != nodeExts.end()){
        for ( NodeExtList::iterator itex = it; ; itex++){
          nodelist.push_back( *itex);
          lastNode = &(*itex);
          if ( itex == ex) break;
        }
        it = ex; it++; // itは未処理の素性をさす
      }

      // ex（地名語候補にならない素性列）の次がend()であれば、そのままループを抜ける。
      if ( it== nodeExts.end()){
        break;
      }

      // 処理済みの最後の要素が地名に先行しない素性列の場合、スキップする。

      if (lastNode && lastNode->canBeAntileader()) {
        // std::cerr << "Antileader: " << lastNode->toString() << std::endl;
        nodelist.push_back(*s);
        lastNode = &(*s);
        it = s;
        it ++;
        continue;
      }

      // (これ以降、地名語候補が得られている（sはend()でない）ことが保証されている。)
      // 地名語を得る。
      NodeExtList::iterator next;
      std::vector<Node> geowords;
      int l;
      
      l = getLongestGeoword( s, e, next, geowords);
      if (l > 0){
	// 地名語が得られた
	if (l > 1) {
	  // 「福島県南相馬市」が
	  // 「福島県」「南（名詞,接尾,地名語）」となる問題への対応
	  Node n = geowords.at(l - 1); // 結果の最後の語
	  if (n.get_partOfSpeech() == "名詞" && n.get_subclassification1() == "接尾" && n.get_subclassification2() == "地名語") {
	    geowords.pop_back(); // 「南」を結果から除去
	    NodeExt odd(n);      // mecab 解析結果に挿入
	    odd.setBeHead(true); // この語は地名の先頭になり得る
	    odd.setBeAntileader(false); // この語に続く語は地名語の可能性がある
	    next = nodeExts.insert(next, odd);
	  }
	}
	// 直前に登録した語が地名修飾語の場合、
	// 地名語の前には地名修飾語はこないので変更する
	// 「むかわ町花園」など
	int nl = nodelist.size();
	if (nl > 0) {
	  Node lastnode = nodelist.at(nl - 1);
	  if (lastnode.get_conjugatedForm() == "名詞-固有名詞-地名修飾語") {
	    lastnode.set_conjugatedForm("");
	    nodelist.pop_back();
	    nodelist.push_back(lastnode);
	  }
	}
	nodelist.insert( nodelist.end(), geowords.begin(), geowords.end());
	lastNode = NULL;
	it = next;
      } else {
	// 地名語候補の最初の素性をそのままpush_backし、次から再度処理する。
	nodelist.push_back( *s);
	lastNode = &(*s);
	it = s;
	it ++;
      }
    }

  }
	
  /// @brief 形態素情報クラスのリストを、形態素情報拡張クラスのリストに変換する。
  ///
  /// @arg @c nodes [in] 形態素情報クラスのリスト
  /// @arg @c nodeextlist [out] 形態素情報拡張クラスのリスト
  void MAImpl::nodeListToNodeExtList( NodeList& nodes, NodeExtList& nodeextlist) const
  {
    nodeextlist.clear();
    for ( NodeList::iterator it = nodes.begin(); it != nodes.end(); it++){
      nodeextlist.push_back( NodeExt( *it));
    }		
  }
	
  /// @brief 引数として渡されたIDを持つ地名語エントリの全ての情報を地名語辞書システムから取得する。
  ///
  /// IDに対応する地名語が存在しない場合、出力Geowordのget_id()が空文字となる。
  /// @arg @c id 地名語ID
  /// @arg ret 地名語エントリクラス 
  /// @return IDに対応する地名語が存在する場合は true
  /// @exception SqliteNotInitializedException Sqlite3が未初期化。
  /// @exception SqliteErrException Sqlite3でエラー。
  bool MAImpl::getGeowordEntry(const std::string& geonlp_id, Geoword& ret) const
  {
    return dbap->findGeowordById(geonlp_id, ret);
  }
	
  /// @brief 引数に与えられた文字列に一致するGeoword候補を取得する。
  ///        読みでも検索する。
  /// @arg @c surface
  /// @arg ret 地名語エントリクラスのマップ。keyがgeonlp_id、valueがGeoword(地名語エントリクラス)オブジェクト。 
  /// @return 取得した地名語エントリの数
  /// @exception SqliteNotInitializedException Sqlite3が未初期化。
  /// @exception SqliteErrException Sqlite3でエラー。	
  int MAImpl::getGeowordEntries(const std::string & surface, std::map<std::string, Geoword>& ret) const
  {
    Wordlist wordlist;
    if (!this->getWordlistBySurface(surface, wordlist)) return 0;
    std::vector<Geoword> vec;
    dbap->getGeowordListFromWordlist(wordlist, vec); //dbap->findGeowordListBySurface(surface);
    ret.clear();
    for (std::vector<Geoword>::iterator it = vec.begin(); it != vec.end(); it++) {
      if (this->isInActiveDictionaryAndClass(*it)) {
	// アクティブな辞書/クラスに含まれる
	ret.insert(std::make_pair((*it).get_geonlp_id(), (*it)));
      }
    }
    return ret.size();
  }
	
  /// @brief 引数に与えられた文字列からGeoword候補を取得する。読みも対象とする。
  ///
  /// @arg @c geoword 語幹または全体の表記
  /// @return Wordlist オブジェクト
  /// @exception SqliteNotInitializedException Sqlite3が未初期化。
  /// @exception SqliteErrException Sqlite3でエラー。
  bool MAImpl::getWordlistBySurface(const std::string& key, Wordlist& ret) const
  {
    // 表記に一致する Wordlist を Darts で検索する
    Darts::DoubleArray::result_pair_type lpair = this->getLongestResultWithDarts(key, false);
#ifdef HAVE_LIBDAMS
    if (lpair.length != damswrapper::get_standardized_string(key).length()) return false; // 見つからない
#else
    if (lpair.length != key.length()) return false; // 見つからない
#endif /* HAVE_LIBDAMS */
    return dbap->findWordlistById(lpair.value, ret);
  }

  /// @brief 地名語候補を得る。
  ///
  /// 与えられた素性シーケンスから、P?HB*に合致する素性シーケンスを得る。
  /// @arg @c start [in] 素性シーケンスの先頭(形態素情報拡張クラスリストの先頭)
  /// @arg @c end [in] 素性シーケンスの末尾(形態素情報拡張クラスリストの末尾)
  /// @arg @c ex [out] 地名語候補にならない最後の素性(形態素情報拡張クラスのイテレータ)
  /// @arg @c s [out] 地名語候補となる最初の素性(形態素情報拡張クラスのイテレータ)
  /// @arg @c e [out] 地名語候補となる最後の素性(形態素情報拡張クラスのイテレータ)
  /// @note ex, s, eは、それぞれ存在しない場合にはendと等しくなる。
  void MAImpl::getLongestGeowordCandidate( const NodeExtList::iterator start, const NodeExtList::iterator end,
     NodeExtList::iterator& ex,
	   NodeExtList::iterator& s, NodeExtList::iterator& e) const
  {
    unsigned int len = 0;
    ex = s = e = end;
    // H(head)：地名語の先頭となり得る品詞 あるいは P(prefix):接頭辞を見つける
    NodeExtList::iterator it;
    for ( it = start; it != end; it++) {
      if ( (*it).canBeHead()) {
        // Hが見つかった
        // std::cout << "H found: " << it->get_surface() << std::endl;
        s = e = it;
        len += (*it).get_surface().length();
        it++;
        break;
      } else if ( (*it).canBePrefix()){
        NodeExtList::iterator nextnode = it;
        nextnode++;
        if ( (*nextnode).canBeHead()) {
          // Pが見つかった
          // std::cout << "P found: " << it->get_surface() << std::endl;
          s = it;
          it = nextnode;
          e = it;
          len += (*it).get_surface().length();
          it++;
          break;
        }
      }
      ex = it;
    }
    // B(Body)：地名語の部分となり得る品詞集合を見つける
    for ( ; it != end; it++) {
      if (!(*it).canBeBody()) break;
      e = it;
      len += (*it).get_surface().length();
      // std::cout << "B found: " << it->get_surface() << std::endl;
#ifdef DEBUG
      std::cerr << "  : " << e->get_surface() << "(" << len << " bytes)" << std::endl;
#endif /* DEBUG */
      if (len > MAX_GEOWORD_LENGTH) {
        // 最長文字数に達した
        break;
      }
    }
  }

  /// @brief 地名語を得る。
  /// 
  /// @arg @c s [in] 地名語候補を構成する素性シーケンスの先頭
  /// @arg @c e [in] 地名語候補を構成する素性シーケンスの末尾
  /// @arg @c next [out] 地名語に合致しない最初の素性
  /// @arg ret 地名語のリスト
  /// @return 得られた地名語の数
  int MAImpl::getLongestGeoword( const NodeExtList::iterator& s, const NodeExtList::iterator& e, NodeExtList::iterator& next, std::vector<Node>& ret) const
  {
    NodeExtList::iterator end = e;
    next = e; next++;
    std::string surface, standardized;
    Node node("","");
    Darts::DoubleArray::result_pair_type lpair;
    ret.clear();
		
    // Darts で最長一致する候補を絞り込む
    std::string key = joinGeowords(s, end);
    lpair = getLongestResultWithDarts(key);

    for (end = e; ; end--, next--) {

      if (lpair.length == 0) {
	// 前方一致する候補が一つもないので、探さないで終了
	break;
      }

      surface = joinGeowords(s, end);
#ifdef HAVE_LIBDAMS
      standardized = damswrapper::get_standardized_string(surface);
#else
      standardized = surface;
#endif /* HAVE_LIBDAMS */
#ifdef DEBUG
      std::cerr << "surface: '" << surface << "', lpair:[" << lpair.value << ", " << lpair.length << "]" <<std::endl;
#endif /* DEBUG */

      if (standardized.length() > lpair.length) {
	// この長さを持つ候補は存在しないので、最後の一単語を削って再チェック
	for (unsigned int l = standardized.length(); l > lpair.length;) {
	  if (s == end) return 0; // 一致する地名語は見つからなかった
	  end--;
	  surface = joinGeowords(s, end);
#ifdef HAVE_LIBDAMS
	  standardized = damswrapper::get_standardized_string(surface);
#else
	  standardized = surface;
#endif /* HAVE_LIBDAMS */
	  l = standardized.length();
	  if (l < lpair.length) {
	    next = end;
	    next++;
	    if (next->canBeSuffix()) {
	      // 削りすぎた＆接尾辞の可能性があるので一単語戻す
	      end++;
	    } else {
	      // 短くなった文字列に対し、Darts の最長一致候補を再検索
	      surface = joinGeowords(s, end);
	      lpair = getLongestResultWithDarts(surface);
	      if (lpair.length == 0) {
		// これより短い地名語は存在しない
		return ret.size();
	      }
	    }
	  }
	}
	next = end;
	next++;
	surface = joinGeowords(s, end);
	
#ifdef DEBUG
	std::cerr << "  -> " << surface << std::endl;
#endif /* DEBUG */
      }

      if ( s == end && !s->canBeSingleGeoword()){
	// 一単語では地名語にならない単語は除外する
	break;
      }

      // std::cerr << "surface = " << surface << std::endl;
			
      // 地名辞書を参照
      if (standardized.length() == lpair.length) {
	std::string alternative = "*";
	// Darts の候補と一致する場合、地名語が存在する
	if (s == end) { // 1素性の場合
	  // 人名ならば MeCab の返す素性を補助フィールドに登録
	  // 次の語が地名語語幹に後続しない語（空間語以外）の場合は
	  // 1素性ならば conjugatedType に記録する
	  // 「愛宕神社」「甲府市役所」…
	  // 後続しない語の品詞は PHBSDefs.cpp で定義
	  // 空間語は GeoParser.rc で定義
	  alternative = s->getAlternativeValue(phbsDefs);
	  // std::cerr << "一語: " << surface << ", " << alternative << std::endl;
	  if (alternative.find("人名", 0) == std::string::npos) {
	    // 人名ではない場合
	    if (next->canBeStop() ) {
	      // 地名語に続かない語が続く場合は地名修飾語として扱う
	      //  std::cerr << "stop = true: " << next->get_surface() << std::endl;
	      // alternative = "名詞-固有名詞-地名修飾語";
	      ;
	    } else {
	      // 地名語として扱う場合は次行のコメントを解除する
	      // alternative = "*";
	      ;
	    }
	  } else {
	    ; // 人名-姓, 人名-名の場合は alternative に素性を入れる
	  }
	}
	node = getGeowordNode(lpair.value, alternative);
	node.set_surface(surface);
	ret.push_back(node);
	return ret.size();
      }
			
      // 一素性になったら終了。
      if ( s== end){
	break;
      }

      std::string withoutSuffix;
      // 接尾辞を削ってみる
      if ( end->canBeSuffix()){
	withoutSuffix = removeSuffix(surface, end->get_suffix().get_surface());
	if ( withoutSuffix.length() == 0) break;
	//	if ( findGeowordNode( withoutSuffix, node)){
	if (withoutSuffix.length() == lpair.length) {
	  std::string alternative = "*";
	  node = getGeowordNode(lpair.value, alternative);
	  ret.push_back( node);
	  ret.push_back( suffixNode( end->get_suffix()));
	  return ret.size();
	}
      }

      // darts 候補の方が短いので、もう一度候補を取得しなおす
      lpair = getLongestResultWithDarts(key);
			
    }
    return ret.size();
  }
	
  /// @brief 素性の表層形を連結した文字列を得る。
  /// 
  /// @arg @c s [in] 地名語候補を構成する素性シーケンスの先頭
  /// @arg @c e [in] 地名語候補を構成する素性シーケンスの末尾
  /// @return 得られた地名語候補
  std::string MAImpl::joinGeowords( NodeExtList::iterator s, NodeExtList::iterator e) const
  {
    std::string surface;
    for ( ; ; s++){
      surface += s->get_surface();
      if ( s== e) break;
    }
    return surface;
  }
	
  /// @brief 地名接尾辞を表すNodeを得る。
  ///
  /// @arg @c suffix 地名接尾辞
  /// @return 地名接尾辞を表すNode。
  Node MAImpl::suffixNode( const Suffix& suffix) const
  {
    Node node( suffix.get_surface(), "名詞,接尾,地名語,*,*,*,-,-,-");
    node.set_originalForm( suffix.get_surface());
    node.set_yomi( suffix.get_yomi());
    node.set_pronunciation( suffix.get_pronunciation());
    return node;
  }
	
  /// @brief 地名語候補から、地名語Nodeを得る。
  ///
  /// @arg @c surface [in] 地名語候補
  /// @arg @c node [out] 地名語Node
  /// @retval true 地名語が見つかった。
  /// @retval false 地名語が見つからなかった。
  bool MAImpl::findGeowordNode(const std::string& surface, Node& node) const {
    Wordlist wordlist;
    this->dbap->findWordlistBySurface(surface, wordlist);
    if (!wordlist.isValid()) return false; // 該当なし

    std::vector<Geoword> geowords;
    this->dbap->getGeowordListFromWordlist(wordlist, geowords, 1);
    Geoword geoword = geowords[0];
    Node newnode(surface, "名詞,固有名詞,地名語,-,*,*,-,-,-");
    node = newnode;
    node.set_originalForm(geoword.get_typical_name());
    node.set_yomi(geoword.get_typical_kana());
    node.set_pronunciation(geoword.get_typical_kana());
    node.set_subclassification3(wordlist.get_idlist());
    return true;
  }
	
  /// @brief darts 見出し語IDから、地名語Nodeを得る。
  ///              読みしか一致しない場合は結果に含めない。
  /// @arg @c lpair [in] darts 見出し語ID
  /// @retval 地名語Node
  Node MAImpl::getGeowordNode(unsigned int id, std::string& alternative) const
  {
    std::string surface;
    geonlp::Wordlist wordlist;
    dbap->findWordlistById(id, wordlist);
    surface = wordlist.get_surface();
    if (!wordlist.isValid()) {
      std::ostringstream oss;
      oss << "No entry in wordlist with id=" << id;
      throw std::runtime_error(oss.str());
    }
    std::string feature = "名詞,固有名詞,地名語,-," + alternative + ",*,-,-,-";
    Node node( surface, feature);
    node.set_originalForm(surface);
    node.set_yomi(wordlist.get_yomi());
    node.set_pronunciation(wordlist.get_yomi());

    // アクティブな地名語に限定した idlist を再構築
    std::vector<Geoword> geowords;
    this->dbap->getGeowordListFromWordlist(wordlist, geowords);
    std::string new_idlist = "";
    for (std::vector<Geoword>::iterator it = geowords.begin(); it != geowords.end(); it++) {
      if (this->isInActiveDictionaryAndClass(*it) && this->isSurfaceMatched(*it, surface)) { // アクティブ
	Geoword geoword = (*it);
	std::string elem = geoword.get_geonlp_id() + ":" + geoword.get_typical_name();
	if (new_idlist.length() == 0) {
	  new_idlist = elem;
	} else {
	  new_idlist += "/" + elem;
	}
      } // アクティブではない場合、追加しない
    }
    //    std::cerr << std::endl << "new_idlist = '" << new_idlist << "'" << std::endl;
    node.set_subclassification3(new_idlist);
    return node;
  }
	
  /// @brief 末尾に地名接尾辞を含む表層形から、地名接尾辞を除いた文字列を得る。
  ///
  /// @arg @c surface [in] 末尾に地名接尾辞を含む地名語候補
  /// @arg @c suffix [in] 地名接尾辞
  /// @return 地名接尾辞を除いた地名語候補
  std::string MAImpl::removeSuffix( const std::string& surface, const std::string &suffix) const
  {
    int len = surface.length() - suffix.length();
    if ( len < 0) return ""; 
    return surface.substr( 0, len);
  }

  /// @brief darts を利用して与えられた文字列に前方最長一致する wordlist を探す。
  /// @arg @c key [in] 先頭が地名の可能性のある検索対象文字列
  /// @arg bSurfaceOnly true の時、読みしか一致しない地名語は含めない。
  /// @return 最長一致する lpair 構造体、 lpair.length に一致したバイト数、 lpair.value に wordlist_id
  Darts::DoubleArray::result_pair_type MAImpl::getLongestResultWithDarts(const std::string& key, bool bSurfaceOnly) const
  {
    Darts::DoubleArray::result_pair_type result_pair[1024];
    Darts::DoubleArray::result_pair_type lpair;
    geonlp::Wordlist wordlist;
    std::vector<geonlp::Geoword> geowords;
    std::string idlist;

    lpair.value = 0; lpair.length = 0;

#ifdef HAVE_LIBDAMS
    std::string key_standardized(damswrapper::get_standardized_string(key));
#else  /* HAVE_LIBDAMS */
    std::string key_standardized = key;
#endif /* HAVE_LIBDAMS */

    if (this->dap == NULL) {
      throw IndexNotExistsException();
    }
    size_t num = dap->commonPrefixSearch(key_standardized.c_str(), result_pair, sizeof(result_pair));

    for (size_t i = 0; i < num; ++i) {
      if (result_pair[i].length > lpair.length) {
	std::string surface = key_standardized.substr(0, result_pair[i].length); // 一致した文字列
	// wordlist を取得し、 idlist を展開する
	if (dbap->findWordlistById(result_pair[i].value, wordlist)) {
	  this->dbap->getGeowordListFromWordlist(wordlist, geowords, 0);
	  // アクティブな辞書／クラスに含まれる地名語が一つでも存在するかチェック
	  for (std::vector<Geoword>::iterator it = geowords.begin(); it != geowords.end(); it++) {
	    if (bSurfaceOnly && !this->isSurfaceMatched(*it, surface)) continue;
	    if (this->isInActiveDictionaryAndClass(*it)) {
	      lpair = result_pair[i]; // アクティブな地名語を含む
	      break;
	    }
	  }
	}
      }
    }
    return lpair;
  }

  // アクティブな辞書/クラスに含まれているかチェックする
  // @arg @c geo  地名語
  // @return      アクティブな辞書、クラスに含まれていれば true を
  //              含まれていなければ false を返す
  bool MAImpl::isInActiveDictionaryAndClass(const Geoword& geo) const {
    bool is_in = false;
    // 辞書チェック
    if (this->activeDictionaries.size() > 0) {
      for (std::map<int, Dictionary>::const_iterator it = this->activeDictionaries.begin(); it != this->activeDictionaries.end(); it++) {
	if ((*it).first == geo.get_dictionary_id()) {
	  is_in = true;
	  break;
	}
      }
      if (!is_in) return false;
    }
    is_in = false;

    // クラスのチェック
    if (this->activeClasses.size() > 0) {
      std::string ne_class = geo.get_ne_class();
      boost::regex pattern;
      for (std::vector<std::string>::const_iterator it = this->activeClasses.begin(); it != this->activeClasses.end(); it++) {
	if ((*it).c_str()[0] == '-') { // 除外パターン指定
	  pattern = boost::regex((*it).substr(1), boost::regex_constants::egrep);
	  if (boost::regex_match(ne_class, pattern)) {
	    return false; // 除外パターンに一致したら常に不一致とする
	  }
	} else if (!is_in) { // まだ一致するパターンが見つかっていない場合は探す
	  pattern = boost::regex((*it), boost::regex_constants::egrep);
	  if (boost::regex_match(geo.get_ne_class(), pattern)) is_in = true;
	}
      }
      if (!is_in) return false;
    }
    return true;
  }

  // 表記で一致しているかチェックする
  bool MAImpl::isSurfaceMatched(const Geoword& geo, const std::string& surface) const {
    std::string prefix_str, suffix_str;
    if (geo.get_parts_for_surface(surface, prefix_str, suffix_str)) {
      // 表記が一致した
      return true;
    }
    return false;
  }

  /// @brief Node が地名語の場合、地名語のリストを得る
  ///        地名語ではない場合は空のマップを返す
  /// @arg   node idlist を含む Node
  /// @return 地名語の場合、 idlist を展開し、 keyがgeonlp_id、valueがGeowordオブジェクトのマップ
  int MAImpl::getGeowordEntries(const Node& node, std::map<std::string, Geoword>& ret) const 
  {
    ret.clear();
    if (node.get_subclassification2() != "地名語") return 0;

    std::string subclass3 = node.get_subclassification3();

    boost::regex pattern = boost::regex("([^\\/:]+):([^\\/:]*)", boost::regex_constants::egrep);
    for (boost::sregex_iterator it = boost::make_regex_iterator(subclass3, pattern); it != boost::sregex_iterator(); it++) {
      std::string geonlp_id = (*it)[1]; // geonlp_id
      // std::string typical_name = (*it)[2]; // typical name
      // std::cerr << "geonlp_id:'" << geonlp_id << "', name:'" << typical_name << "'" << std::endl;
      Geoword geoword;
      if (this->getGeowordEntry(geonlp_id, geoword))
	ret.insert(std::make_pair(geonlp_id, geoword));
    }
    return ret.size();
  }

  void MAImpl::clearDatabase(void) {
    this->dbap->clearGeowords();
    this->dbap->clearDictionaries();
  }

  int MAImpl::addDictionary(const std::string& jsonfile, const std::string& csvfile) const {
    return this->dbap->addDictionary(jsonfile, csvfile);
  }

  bool MAImpl::removeDictionary(const std::string& identifier) const {
    this->dbap->removeDictionary(identifier);
    return true;
  }

  void MAImpl::updateIndex(void) {
    this->dbap->updateWordlists();
    // Darts ファイルが変更されている可能性があるので初期化が必要
    std::string darts;
    try {
      darts = this->profilep->get_darts_file();
      if (darts.length() > 0) {
	this->dap = DoubleArrayPtr(new Darts::DoubleArray());
	this->dap->open(darts.c_str());
      }
    } catch (std::runtime_error& e) {
      throw ServiceCreateFailedException(e.what(), ServiceCreateFailedException::DARTS);
    }

  }

}
