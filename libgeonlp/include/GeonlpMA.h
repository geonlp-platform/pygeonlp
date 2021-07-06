///
/// @file
/// @brief 地名語抽出API(インタフェース)の定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2021, NII
///

#ifndef _GEONLP_MA_H
#define _GEONLP_MA_H

#include <map>
#include <boost/shared_ptr.hpp>
#include "config.h"
#include "picojson.h"
#include "Geoword.h"
#include "Dictionary.h"
#include "Wordlist.h"
#include "Node.h"
#include "Exception.h"
#include "SqliteNotInitializedException.h"
#include "SqliteErrException.h"

/// @namespace geonlp
/// 地名語抽出システム
namespace geonlp
{
  /// @brief MAのインタフェース定義。
  class MA {
  public:

    /// @brief 引数として渡された自然文を形態素解析し、解析結果をテキストとして返す。
    ///
    /// 解析結果テキストの書式はMeCabのデフォルトに準じる(実際には実装クラスの実装に依る)。
    /// @arg @c sentence 解析対象の自然文。
    /// @return 解析結果としてのテキスト。
    /// @exception SqliteNotInitializedException Sqlite3が未初期化。
    /// @exception MeCabNotInitializedException MeCabが未初期化。
    /// @exception SqliteErrException Sqlite3でエラー。
    /// @exception MeCabErrException MeCabでエラー。
    virtual std::string parse(const std::string & sentence) const = 0;
		
    /// @brief 引数として渡された自然文を形態素解析し、解析結果の各行を要素とするノードの配列を返す。
    ///
    /// @arg @c sentence 解析対象の自然文。
    /// @arg ret 解析結果。形態素情報クラスの配列。
    /// @return 結果のノード数
    /// @exception SqliteNotInitializedException Sqlite3が未初期化。
    /// @exception MeCabNotInitializedException MeCabが未初期化。
    /// @exception SqliteErrException Sqlite3でエラー。
    /// @exception MeCabErrException MeCabでエラー。
    virtual int parseNode(const std::string & sentence, std::vector<Node>& ret) const = 0;
    
    /// @brief 引数として渡されたIDを持つ地名語エントリの全ての情報を地名語辞書システムから取得する。
    ///
    /// @arg @c id 地名語ID
    /// @arg ret 地名語エントリクラス 
    /// @return IDに対応する地名語が存在する場合は true
    /// @exception SqliteNotInitializedException Sqlite3が未初期化。
    /// @exception SqliteErrException Sqlite3でエラー。
    virtual bool getGeowordEntry(const std::string & id, Geoword& ret) const = 0;
		
    /// @brief 引数に与えられた文字列に一致するGeoword候補を取得する。
    ///
    /// @arg @c surface
    /// @arg ret 地名語エントリクラスのマップ。keyがgeonlp_id、valueがGeoword(地名語エントリクラス)オブジェクト。 
    /// @return 取得した地名語エントリの数
    /// @exception SqliteNotInitializedException Sqlite3が未初期化。
    /// @exception SqliteErrException Sqlite3でエラー。
    virtual int getGeowordEntries(const std::string & surface, std::map<std::string, Geoword>& ret) const = 0;
	  
    /// @brief Node が地名語の場合、地名語のリストを得る
    ///        地名語ではない場合は空のマップを返す
    /// @arg   node idlist を含む Node
    /// @arg   ret  地名語の場合、 idlist を展開し、 keyがgeonlp_id、valueがGeowordオブジェクトのマップ
    /// @return 取得した地名語の数
    virtual int getGeowordEntries(const Node& node, std::map<std::string, Geoword>& ret) const = 0;
	
    /// @brief 引数に与えられた文字列に対応する Wordlist を得る
    ///
    /// @arg @c geoword 語幹または全体の表記
    /// @arg ret Wordlist オブジェクト 
    /// @return 対応するWordlistが存在した場合はtrue
    /// @exception SqliteNotInitializedException Sqlite3が未初期化。
    /// @exception SqliteErrException Sqlite3でエラー。
    virtual bool getWordlistBySurface(const std::string& key, Wordlist& ret) const = 0;

    /// @brief 利用する辞書を直接指定する
    /// @arg @c 辞書IDのリスト
    virtual void setActiveDictionaries(const std::vector<int>& dics) = 0;

    /// @brief 利用する辞書を追加する
    /// @arg @c dics 追加する辞書IDのリスト
    virtual void addActiveDictionaries(const std::vector<int>& dics) = 0;

    /// @brief 利用する辞書から除外する
    /// @arg @c dics 除外する辞書IDのリスト
    virtual void removeActiveDictionaries(const std::vector<int>& dics) = 0;

    /// @brief 利用する辞書をプロファイルのデフォルトに戻す。
    virtual void resetActiveDictionaries(void) = 0;

    /// @brief アクティブな辞書 ID のリストを取得する。
    virtual const std::map<int, Dictionary>& getActiveDictionaries(void) const = 0;

    /// @brief 利用する固有名クラスをクラス名正規表現のリストで指定する
    /// @arg @c ne_classes 利用するクラス名、複数指定した場合は OR、- から始まる場合は除外する
    /// @return なし
    virtual void setActiveClasses(const std::vector<std::string>& ne_classes) = 0;

    /// @brief 利用する固有名クラスの正規表現を追加する
    /// @arg @c ne_classes 追加するクラスの正規表現リスト
    virtual void addActiveClasses(const std::vector<std::string>& ne_classes) = 0;

    /// @brief 利用する固有名クラスの正規表現を除外する
    /// @arg @c ne_classes 除外するクラスの正規表現リスト
    virtual void removeActiveClasses(const std::vector<std::string>& ne_classes) = 0;

    /// @brief 利用する固有名クラスをプロファイルのデフォルトに戻す。
    virtual void resetActiveClasses(void) = 0;

    /// @brief アクティブな固有名クラスの正規表現リストを取得する。
    virtual const std::vector<std::string>& getActiveClasses(void) const = 0;

    virtual ~MA() {}

    /// @brief ID で指定した辞書情報を取得する
    virtual bool getDictionaryById(int dictionary_id, Dictionary& ret) const = 0;

    /// @brief identifier で指定した辞書情報を取得する
    virtual bool getDictionary(const std::string& identifier, Dictionary& ret) const = 0;

    /// @brief 辞書一覧を取得する
    virtual int getDictionaryList(std::map<int, Dictionary>& ret) const = 0;

    /// @brief 内部 ID で指定した辞書の identifier を取得する
    virtual const std::string getDictionaryIdentifierById(int) const = 0;

    /// @brief 地名語辞書をクリアする
    /// バイナリ辞書も削除する
    virtual void clearDatabase(void) = 0;

    /// @brief 地名語辞書を追加する
    /// 地名語も追加するがコンパイルはしない
    /// @exception PicojsonException JSON 読み込みエラー
    virtual int addDictionary(const std::string& jsonfile, const std::string& csvfile) const = 0;

    /// @brief 地名語辞書を削除する
    /// 地名語も削除するがコンパイルはしない
    /// @arg @c identifier 辞書の identifier ("geonlp:japan_pref")
    /// @return 削除に成功した場合は True, 失敗した場合は False
    virtual bool removeDictionary(const std::string& identifier) const = 0;

    /// @brief 地名語辞書をコンパイルしてインデックスを更新する
    virtual void updateIndex(void) = 0;

  };
	
  /// MAのポインタ
  typedef boost::shared_ptr<MA> MAPtr;
	
  /// @brief MAインタフェースを取得する。
  /// 
  /// @arg @c dict_dir 辞書ディレクトリ。
  /// @arg @c profile プロファイル名。
  /// @exception ServiceCreateFailedException 取得失敗。
  MAPtr createMA(const std::string& dict_dir, const std::string& profile = "");

  /// @brief MAインタフェースを取得する。
  /// 
  /// @arg @c settings  辞書ディレクトリを含む初期設定 (picojson)
  /// @exception ServiceCreateFailedException 取得失敗。
  MAPtr createMA(const picojson::value& settings);

}
#endif
