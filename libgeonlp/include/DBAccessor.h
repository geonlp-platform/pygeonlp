///
/// @file
/// @brief DBアクセスクラス DBAccessorの定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2011, NII
///

#ifndef _DBACCESSOR_H
#define _DBACCESSOR_H

#define GEOWORD_CACHE_SIZE  1000

#include <string>
#include <boost/shared_ptr.hpp>
#include "Profile.h"
#include "Geoword.h"
// #include "GeowordCore.h"
#include "Dictionary.h"
#include "Wordlist.h"
#include "SqliteErrException.h"
#include "SqliteNotInitializedException.h"
#include "FormatException.h"
#include "DartsException.h"
#ifdef DEBUG
#include <stdio.h>
#include "picojsonExt.h"
#endif

struct sqlite3;

namespace geonlp
{	
  ///
  /// @brief SQLiteにアクセスするためのクラス。
  ///
  class DBAccessor {
  private:
    /// キャッシュ
    static std::map<std::string, Geoword> geoword_cache;
    static bool searchGeowordFromCache(const std::string& geonlp_id, Geoword& geoword);
    static void addGeowordToCache(const Geoword& geoword);
    static void clearGeowordCache(void);

    /// DBファイルハンドル
    sqlite3* sqlitep;      // 地名語一覧
    sqlite3* wordlistp;    // 単語表記一覧
		
    /// DBファイル名
    std::string sqlite3_fname;
    std::string wordlist_fname;
    /// darts ファイル名
    std::string darts_fname;

#ifdef DEBUG
    /// DB アクセスログのファイルポインタ
    FILE* fplog;
#endif /* DEBUG */

    /// @brief darts ファイル更新時の一時ファイル名を生成
    /// @return 'tmp_' + darts_fname
    inline std::string tmpDartsFilename(void) const { return this->darts_fname + ".tmp"; }
    
    /// @brief wordlist 更新時の一時テーブル wordlist_tmp を生成
    void createTmpWordlistTable(void) const;

    /// @brief wordlist 更新時の一時テーブルを削除
    void dropTmpWordlistTable(void) const;

  public:
    /// @brief コンストラクタ。
    /// @arg @c profilename プロファイルのファイル名
    DBAccessor(const std::string& profile_fname): sqlitep(NULL), wordlistp(NULL) {
      Profile profile;
      profile.load(profile_fname.c_str());
      sqlite3_fname = profile.get_sqlite3_file();
      wordlist_fname = profile.get_wordlist_file();
      darts_fname = profile.get_darts_file();
    }
    /// @brief コンストラクタ。
    /// @arg @c profile Profile オブジェクト
    DBAccessor(const Profile& profile): sqlitep(NULL), wordlistp(NULL) {
      sqlite3_fname = profile.get_sqlite3_file();
      wordlist_fname = profile.get_wordlist_file();
      darts_fname = profile.get_darts_file();
    }
		
    // DBオープン
    void open();

    // DBクローズ
    int close();

    // 指定した GeonlpID を持つ地名語エントリの情報を DB から取得する
    // GeonlpMAImpleSq3 で利用
    bool findGeowordById(const std::string & id, Geoword& ret) const;
    //    const Geoword findSubsetById(const std::string & id) const

    // 指定した辞書 ID と entry_id のペアを持つ地名語エントリの情報を DB から取得する
    // geonlp_id 逆引き用
    bool findGeowordByDictionaryIdAndEntryId(int dictionary_id, const std::string& entry_id, Geoword& ret) const;

    // 指定した名称を持つ地名語エントリ（複数）の情報を DB から取得する
    // geoword テーブルに変更があった場合、 updateWordlists を実行しておくこと
    int findGeowordListBySurface(const std::string& surface, std::vector<Geoword>& ret) const;

    // 辞書一覧を DB から取得する
    int getDictionaryList(std::map<int, Dictionary>& ret ) const;

    // 引数として渡された内部 ID をもつ辞書の情報をDBから取得する
    bool getDictionaryById(int id, Dictionary& ret) const;

    // 引数として渡された identifier を持つ辞書の情報を DB から取得する
    bool getDictionary(const std::string& identifier, Dictionary& ret) const;

    // 指定された identifier を持つ辞書の内部 ID を DB から取得する
    int getDictionaryInternalId(const std::string& identifier) const;

    // 全ての単語IDリストの情報を取得する
    // geonlp_ma_makedic で利用
    bool findAllWordlist(std::vector<Wordlist>& wordlists) const;

    // 引数として渡されたIDを持つ単語IDリストの情報を取得する。
    // GeonlpMAImpleSq3 で利用
    bool findWordlistById(unsigned int id, Wordlist& ret) const;
    
    // 引数として渡された見出し語を持つ単語IDリストの情報を取得する。
    // 該当する Wordlist が存在しない場合は 戻り値の get_surface() == "" になる
    bool findWordlistBySurface(const std::string& surface, Wordlist& ret) const;

    // 引数として渡された読みを持つ単語IDリストの情報を取得する。
    // 該当する Wordlist が存在しない場合は 戻り値の get_surface() == "" になる
    bool findWordlistByYomi(const std::string& yomi, Wordlist& ret) const;

    // 地名語を一括でDBにセット（insert）する
    // note: 個別に登録すると毎回ファイルに書くので非常に遅い
    // geoword テーブルが無い場合にはテーブルの作成も行う
    void setGeowords(const std::vector<Geoword>& geowords) const;

    // 辞書を一括でDBにセット（insert）する
    // dictionary テーブルが無い場合にはテーブルの作成も行う
    void setDictionaries(const std::vector<Dictionary>& dictionaries) const;

    // 単語IDリストを一括でDBにセットする
    // wordlist テーブルが無い場合にはテーブルの作成も行う
    void setWordlists(const std::vector<Wordlist>& wordlists) const;

    // 地名語テーブルをクリアする
    void clearGeowords() const;

    // 辞書テーブルをクリアする
    void clearDictionaries() const;

    // 単語IDリストテーブルをクリアする
    void clearWordlists() const;

    // 地名語テーブルの内容から Wordlist を更新する
    // darts ファイルも更新される
    void updateWordlists() const;

    // 地名語テーブルの内容から Wordlist を更新する（更新結果を取得する）
    // darts ファイルも更新される
    void updateWordlists(std::vector<Wordlist>& wordlists) const;

    // 辞書 CSV ファイルから地名語と辞書情報を読み込む
    // 読み込んだ件数を返す
    int addDictionary(const std::string& jsonfile, const std::string& csvfile) const;

    // 辞書をデータベースから削除する
    void removeDictionary(const std::string& identifier) const;

    // wordlist に含まれる ID を持つ Geoword をデータベースから取得する
    int getGeowordListFromWordlist(const Wordlist& wordlist, std::vector<Geoword>& ret, int limit = 0) const;

  private:
    // geowordテーブルから得られた情報が、期待する順序でカラムが並んでいることを確認する
    int assertGeowordColumns( char**, int) const ;

    // dictionaryテーブルから得られた情報が、期待する順序でカラムが並んでいることを確認する
    int assertDictionaryColumns(char**, int) const;

    // wordlistテーブルから得られた情報が、期待する順序でカラムが並んでいることを確認する
    int assertWordlistColumns(char**, int) const;

    // geowordテーブルから得られた情報を地名語エントリクラスに変換する
    void resultToGeoword( char **azResult, Geoword& out) const;
		
    // dictionaryテーブルから得られた情報を辞書クラスに変換する
    void resultToDictionary(char** azResult, Dictionary& out) const;

    // wordlistテーブルから得られた情報を単語IDリストクラスに変換する
    void resultToWordlist(char** azResult, Wordlist& out) const;

    // geoword, dictionary, wordlist テーブルを作成する（もしなければ）
    void createTables() const;

    void beginTransaction(sqlite3*) const;
    void commit(sqlite3*) const;

  };

  typedef boost::shared_ptr<DBAccessor> DBAccessorPtr;

}
#endif
