///
/// @file
/// @brief 地名語抽出API(インタフェース)実装クラスの定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010, NII
///

#ifndef _GEONLP_MA_IMPL_SQ3_H
#define _GEONLP_MA_IMPL_SQ3_H

#include "GeonlpMA.h"
#include "MeCabAdapter.h"
#include "PHBSDefs.h"
#include <fstream>
#include "darts.h"

#ifdef GEOWORD_UNITTEST
#define PUBLIC_IF_UNITTEST public:
#else 
#define PUBLIC_IF_UNITTEST
#endif

namespace geonlp

{
  class MeCabAdapter;
  class DBAccessor;
  class Profile;
  class Suffix;
  //	class Prefix;
  class Geoword;
  class Dictionary;
  class GeowordSubset;
  class AbstructGeowordFormatter;
  class NodeExt;
  typedef boost::shared_ptr<MeCabAdapter> MeCabAdapterPtr;
  typedef boost::shared_ptr<DBAccessor> DBAccessorPtr;
  typedef boost::shared_ptr<Profile> ProfilePtr;
  typedef boost::shared_ptr<AbstructGeowordFormatter> GeowordFormatterPtr;
  typedef boost::shared_ptr<Darts::DoubleArray> DoubleArrayPtr;
	
  /// @brief MAのインタフェース実装クラス。
  class MAImpl: public MA {
  private:
    /// 初期設定 Profile へのポインタ。
    ProfilePtr profilep;
    
    /// MeCabにアクセスするためのクラスへのポインタ。
    MeCabAdapterPtr mecabp;
		
    /// SQLiteにアクセスするためのクラスへのポインタ。
    DBAccessorPtr dbap;

    /// SQLite に登録されている地名語の darts クラスへのポインタ。
    DoubleArrayPtr dap;

    /// 形態素情報リストの出力形式定義クラスへのポインタ。
    GeowordFormatterPtr formatter;
		
    /// 地名接頭辞集合、地名語の先頭となり得る品詞集合、地名語の部分となり得る品詞集合等の定義
    PHBSDefs phbsDefs;

    /// プロファイルで指定された辞書IDのリスト、リセット用に記憶
    std::map<int, Dictionary> defaultDictionaries;

    /// プロファイルで指定された利用可能クラスのリスト、リセット用に記憶
    std::vector<std::string> defaultClasses;

    /// 利用する辞書 ID のリスト、高速化のため記憶
    std::map<int, Dictionary> activeDictionaries;

    /// 利用するクラスのリスト、高速化のため記憶
    std::vector<std::string> activeClasses;
    
    typedef MeCabAdapter::NodeList NodeList;
		
    typedef std::list<NodeExt> NodeExtList;

  public:
    // コンストラクタ
    MAImpl(ProfilePtr p);
		
    // デストラクタ
    ~MAImpl();

    /// ID で指定した辞書情報を取得する
    bool getDictionaryById(int dictionary_id, Dictionary& ret) const;

    /// identifer で指定した辞書情報を取得する
    bool getDictionary(const std::string& identifier, Dictionary& ret) const;

    // 辞書一覧を取得する
    int getDictionaryList(std::map<int, Dictionary>& ret) const;

    // 内部 ID で指定した辞書の identifier を取得する
    const std::string getDictionaryIdentifierById(int dictionary_id) const;

    // 引数として渡された自然文を形態素解析し、解析結果をテキストとして返す。
    std::string parse(const std::string & sentence) const;

    // 引数として渡された自然文を形態素解析し、解析結果の各行を要素とするノードの配列を返す。
    int parseNode(const std::string & sentence, std::vector<Node>& ret) const;

    // 引数として渡されたIDを持つ地名語エントリの全ての情報を地名語辞書システムから取得する。
    bool getGeowordEntry(const std::string& geonlp_id, Geoword& ret) const;

    // 引数に与えられた（上位語）文字列からGeoword候補を取得する。
    // 戻り値は、「keyがgeonlp_id、valueがGeowordオブジェクト」のマップ。
    int getGeowordEntries(const std::string & geoword, std::map<std::string, Geoword>& ) const;
	  
    /// @brief Node が地名語の場合、地名語のリストを得る
    ///        地名語ではない場合は空のマップを返す
    /// @arg   node idlist を含む Node
    /// @return 地名語の場合、 idlist を展開し、 keyがgeonlp_id、valueがGeowordオブジェクトのマップ
    int getGeowordEntries(const Node& node, std::map<std::string, Geoword>& ret) const;

    /// 引数に与えられた文字列からGeoword候補を取得する
    /// @return Wordlist オブジェクト
    /// @exception SqliteNotInitializedException Sqlite3が未初期化。
    /// @exception SqliteErrException Sqlite3でエラー。
    bool getWordlistBySurface(const std::string& key, Wordlist&) const;

    /// @brief 利用する辞書を辞書IDのリストで指定する。プロファイルのデフォルトに対する差分。
    /// @arg @c dics 利用する辞書ID、複数指定した場合は OR、- から始まる場合は除外
    /// @return なし
    void setActiveDictionaries(const std::vector<int>& dics);

    /// @brief 利用する辞書を追加する
    /// @arg @c dics 追加する辞書IDのリスト
    void addActiveDictionaries(const std::vector<int>& dics);

    /// @brief 利用する辞書から除外する
    /// @arg @c dics 除外する辞書IDのリスト
    void removeActiveDictionaries(const std::vector<int>& dics);

    /// @brief 利用する辞書をプロファイルのデフォルトに戻す。
    void resetActiveDictionaries(void);

    /// @brief アクティブな辞書 ID のリストを取得する。
    const std::map<int, Dictionary>& getActiveDictionaries(void) const;

    /// @brief 利用する固有名クラスをクラス名正規表現のリストで指定する
    /// @arg @c ne_classes 利用するクラス名、複数指定した場合は OR、- から始まる場合は除外する
    /// @return なし
    void setActiveClasses(const std::vector<std::string>& ne_classes);

    /// @brief 利用する固有名クラスの正規表現を追加する
    /// @arg @c ne_classes 追加するクラスの正規表現リスト
    void addActiveClasses(const std::vector<std::string>& ne_classes);

    /// @brief 利用する固有名クラスの正規表現を除外する
    /// @arg @c ne_classes 除外するクラスの正規表現リスト
    void removeActiveClasses(const std::vector<std::string>& ne_classes);

    /// @brief 利用する固有名クラスをプロファイルのデフォルトに戻す。
    void resetActiveClasses(void);

    /// @brief アクティブな固有名クラスの正規表現リストを取得する。
    const std::vector<std::string>& getActiveClasses(void) const;

    void clearDatabase(void);
    int addDictionary(const std::string& jsonfile, const std::string& csvfile) const;
    bool removeDictionary(const std::string& identifier) const;
    void updateIndex(void);

  private:
    PUBLIC_IF_UNITTEST
		
      // MeCabによるパース結果を地名語辞書を参照して変換する
      void convertMeCabNodeToNodeList( NodeList& nodes, std::vector<Node>& nodelist) const;

    // 形態素情報クラスのリストを、形態素情報拡張クラスのリストに変換する。
    void nodeListToNodeExtList( NodeList& nodes, NodeExtList& nodeextlist) const; 
		
    // 地名語候補を得る。
    void getLongestGeowordCandidate( const NodeExtList::iterator start, const NodeExtList::iterator end,
				     NodeExtList::iterator& ex,
				     NodeExtList::iterator& s, NodeExtList::iterator& e) const;
    // 地名語を得る。
    int getLongestGeoword( const NodeExtList::iterator& s, const NodeExtList::iterator& e, 
			   NodeExtList::iterator& next, std::vector<Node>& ret) const;
		
    // 素性の表層形を連結した文字列を得る。
    std::string joinGeowords( NodeExtList::iterator s, NodeExtList::iterator e) const;
		
    // 地名語候補から、地名語Nodeを得る。
    bool findGeowordNode( const std::string& surface, Node& node) const;

    // 見出し語IDから地名語Nodeを得る。
    Node getGeowordNode(unsigned int id, std::string& alternative) const;
	  
    std::string removeSuffix( const std::string& surface, const std::string &suffix) const;
		
    // 地名接尾辞を表すNodeを得る。
    Node suffixNode( const Suffix& suffix) const;

    // DARTS で最長一致する候補を得る。
    Darts::DoubleArray::result_pair_type getLongestResultWithDarts(const std::string& key, bool bSurfaceOnly = true) const;

    // 指定した地名語がアクティブな辞書/クラスに含まれているかチェックする
    bool isInActiveDictionaryAndClass(const Geoword& geo) const;

    // 指定した地名語の表記が検索表記と一致していれば true を返す
    bool isSurfaceMatched(const Geoword& geo, const std::string& surface) const;

  };
}
#endif
