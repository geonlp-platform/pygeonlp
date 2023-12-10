from logging import getLogger
import os
import site
import sys
from typing import Union

from pygeonlp import capi

from pygeonlp.api.dictionary import Dictionary
from pygeonlp.api.metadata import Metadata

logger = getLogger(__name__)


class DictManager(object):
    """
    地名語辞書の管理を行なうクラスです。

    Attributes
    ----------
    _dict_cache : dict
        辞書ID（整数）をキー、辞書identifier（文字列）を値にもつ
        マッピングテーブル（キャッシュ用）。
    capi_ma : pygeonlp.capi オブジェクト
        C 実装の拡張形態素解析機能を利用するためのオブジェクト。
    db_dir: str
        管理対象データベースディレクトリのパス。
    """

    def __init__(self,
                 db_dir: Union[str, bytes, os.PathLike, None] = None):
        """
        このサービスが利用する辞書や、各種設定を初期化します。

        Parameters
        ----------
        db_dir : PathLike, optional
            利用するデータベースディレクトリのパス。
            省略した場合は ``api.get_db_dir()`` で決定します。
        """
        self._dict_cache = {}
        self.capi_ma = None

        if db_dir is None:
            from . import get_db_dir
            db_dir = get_db_dir()

        self.db_dir = db_dir

        # データベースディレクトリの存在チェック
        if os.path.exists(db_dir):
            self.init_capi_ma()

    def init_capi_ma(self):
        # capi_ma オブジェクトを作成
        if self.capi_ma is None:
            capi_options = {'data_dir': str(self.db_dir)}
            self.capi_ma = capi.MA(capi_options)

    def getDictionary(self, id_or_identifier):
        """
        指定した id または identifier を持つ辞書のメタデータを返します。
        id, identifier に一致する辞書が存在しない場合は None を返します。

        Parameters
        ----------
        id_or_identifier : str or int
            str の場合は辞書 identifier で指定。
            int の場合は内部辞書 id で指定。

        Returns
        -------
        Metadata
            Metadata インスタンス。

        Examples
        --------
        >>> from pygeonlp.api.dict_manager import DictManager
        >>> manager = DictManager()
        >>> manager.getDictionary('geonlp:ksj-station-N02')
        {"@context": "https://schema.org/", "@type": "Dataset", "alternateName": "", "creator": [{"@type": "Organization", "name": "株式会社情報試作室", "sameAs": "https://www.info-proto.com/"}], "dateModified": "2021-08-27T17:18:18+09:00", "description": "国土数値情報「鉄道データ（N02）」から作成した、日本の鉄道駅（地下鉄を含む）の辞書です。hypernym には運営者名と路線名を記載しています。「都営」ではなく「東京都」のようになっていますので注意してください。自由フィールドとして、railway_classに「鉄道区分」、institution_typeに「事業者種別」を含みます。", "distribution": [{"@type": "DataDownload", "contentUrl": "https://www.info-proto.com/static/ksj-station-N02.csv", "encodingFormat": "text/csv"}], "identifier": ["geonlp:ksj-station-N02"], "isBasedOn": {"@type": "CreativeWork", "name": "国土数値情報 鉄道データ", "url": "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_2.html"}, "keywords": ["GeoNLP", "地名辞書"], "license": "https://creativecommons.org/licenses/by/4.0/", "name": "国土数値情報 鉄道データ（駅）", "size": "10191", "spatialCoverage": {"@type": "Place", "geo": {"@type": "GeoShape", "box": "26.193265 127.652285 45.41616333333333 145.59723"}}, "temporalCoverage": "../..", "url": "https://www.info-proto.com/static/ksj-station-N02.html"}
        """  # noqa: E501
        self._check_initialized()
        if id_or_identifier is None:
            return self.capi_ma.getDictionaryList()

        jsonld = self.capi_ma.getDictionaryInfo(id_or_identifier)
        if jsonld:
            return Metadata(jsonld)

        return None

    def getDictionaries(self):
        """
        インストール済み辞書のメタデータ一覧を返します。

        Returns
        -------
        list
            Metadata インスタンスのリスト。

        Examples
        --------
        >>> from pygeonlp.api.dict_manager import DictManager
        >>> manager = Manager()
        >>> sorted([x.get_identifier() for x in manager.getDictionaries()])
        ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02']
        """
        self._check_initialized()
        dictionaries = []
        for id, metadata in self.capi_ma.getDictionaryList().items():
            # metadata['_internal_id'] = int(id)
            dictionaries.append(Metadata(metadata))

        return dictionaries

    def clearDatabase(self):
        """
        データベースに登録されている辞書をクリアします。
        データベース内の地名語も全て削除されます。

        この関数は、データベースを作り直す際に利用します。

        Examples
        --------
        >>> from pygeonlp.api.dict_manager import DictManager
        >>> manager = DictManager()
        >>> manager.clearDatabase()
        True
        >>> manager.addDictionaryFromWeb(
        ...   'https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
        True
        >>> manager.updateIndex()
        True
        """
        self._check_initialized()
        return self.capi_ma.clearDatabase()

    def addDictionaryFromFile(self, jsonfile, csvfile):
        """
        指定したパスにある辞書メタデータ（JSONファイル）と
        地名解析辞書（CSVファイル）をデータベースに登録します。

        既に同じ identifier を持つ辞書データがデータベースに登録されている場合、
        削除してから新しい辞書データを登録します。

        Parameters
        ----------
        jsonfile : str
            辞書メタデータファイルのパス。
        csvfile : str
            地名解析辞書ファイルのパス。

        Returns
        -------
        bool
            常に True。登録に失敗した場合は例外が発生します。

        Examples
        --------
        >>> from pygeonlp.api.dict_manager import DictManager
        >>> manager = DictManager()
        >>> manager.addDictionaryFromFile(
        ...   'base_data/geoshape-city.json', 'base_data/geoshape-city.csv')
        True
        >>> manager.updateIndex()
        True
        """
        self._check_initialized()
        if not isinstance(jsonfile, str) or not isinstance(csvfile, str):
            raise TypeError("jsonfile と csvfile は str で指定してください。")

        dic = Dictionary.load(jsonfile, csvfile)
        new_identifier = dic.get_identifier()
        if self.getDictionary(new_identifier):
            self.removeDictionary(new_identifier)

        return dic.add(self.capi_ma)

    def addDictionaryFromWeb(self, url, params=None, **kwargs):
        """
        指定した URL にあるページに含まれる辞書メタデータ（JSON-LD）を取得し、
        メタデータに記載されている URL から地名解析辞書（CSVファイル）を取得し、
        データベースに登録します。

        既に同じ identifier を持つ辞書データがデータベースに登録されている場合、
        削除してから新しい辞書データを登録します。

        Parameters
        ----------
        url : str
            辞書メタデータを含むウェブページの URL。
        params : dict, optional
            requests.get に渡す params パラメータ。
        **kwargs : dict, optional
            requests.get に渡す kwargs パラメータ。

        Returns
        -------
        bool
            常に True。登録に失敗した場合は例外が発生します。

        Examples
        --------
        >>> from pygeonlp.api.dict_manager import DictManager
        >>> manager = DictManager()
        >>> manager.clearDatabase()
        True
        >>> manager.addDictionaryFromWeb('https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
        True
        >>> manager.updateIndex()
        True
        """
        self._check_initialized()
        dic = Dictionary.download(url, params, **kwargs)
        new_identifier = dic.get_identifier()
        if self.getDictionary(new_identifier):
            self.removeDictionary(new_identifier)

        return dic.add(self.capi_ma)

    def addDictionaryFromCsv(self, csvfile, name=None, identifier=None):
        """
        指定したパスにある地名解析辞書（CSVファイル）をデータベースに登録します。

        辞書の name と identifier を省略した場合、
        CSV ファイル名から自動的に設定されます。

        既に同じ identifier を持つ辞書データがデータベースに登録されている場合、
        削除してから新しい辞書データを登録します。

        Parameters
        ----------
        csvfile : str
            地名解析辞書ファイルのパス。
        name : str, optional
            辞書名。省略した場合、 CSV ファイルの basename を利用します。
        identifier : str, optional
            辞書 identifier。省略した場合、 CSV ファイルの basename を取り、
            ``geonlp:<basename>`` を利用します。

        Returns
        -------
        bool
            常に True。登録に失敗した場合は例外が発生します。

        Examples
        --------
        >>> from pygeonlp.api.dict_manager import DictManager
        >>> manager = DictManager()
        >>> manager.addDictionaryFromCsv(
        ...   'base_data/ksj-station-N02-2020.csv',
        ...   name='日本の鉄道駅（2020年）')
        True
        >>> manager.updateIndex()
        True
        """
        self._check_initialized()
        if not isinstance(csvfile, str):
            raise TypeError("csvfile は str で指定してください。")

        dic = Dictionary.create(csvfile, name, identifier)
        new_identifier = dic.get_identifier()
        if self.getDictionary(new_identifier):
            self.removeDictionary(new_identifier)

        return dic.add(self.capi_ma)

    def saveDictionaryFromWeb(self, jsonfile, csvfile, url,
                              params=None, **kwargs):
        """
        指定した URL にあるページに含まれる辞書メタデータ（JSON-LD）を取得し、
        メタデータに記載されている URL から地名解析辞書（CSVファイル）を取得し、
        指定されたファイルに保存します。

        Parameters
        ----------
        jsonfile : str
            json-ld を保存するファイル名。
        csvfile : str
            CSV データを保存するファイル名。
        url : str
            辞書メタデータを含むウェブページの URL。
        params : dict, optional
            requests.get に渡す params パラメータ。
        **kwargs : dict, optional
            requests.get に渡す kwargs パラメータ。

        Returns
        -------
        bool
            常に True。ダウンロードに失敗した場合は例外が発生します。

        Examples
        --------
        >>> from pygeonlp.api.dict_manager import DictManager
        >>> manager = DictManager()
        >>> manager.saveDictionaryFromWeb('geoshape.json', 'geoshape.csv', 'https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
        True
        >>> import os
        >>> os.remove('geoshape.json')
        >>> os.remove('geoshape.csv')
        """  # noqa: E501
        self._check_initialized()
        dic = Dictionary.download(url, params, **kwargs)
        return dic.save(jsonfile, csvfile)

    def removeDictionary(self, identifier):
        """
        identifier で指定した辞書をデータベースから削除します。

        Parameters
        ----------
        identifier : str
            辞書の identifier ("geonlp:xxxxx")。

        Returns
        -------
        bool
            常に True。

        Raises
        ------
        RuntimeError
            指定した辞書が登録されていない場合は RUntimeError が発生します。

        Examples
        --------
        >>> from pygeonlp.api.dict_manager import DictManager
        >>> manager = DictManager()
        >>> manager.removeDictionary('geonlp:geoshape-city')
        True
        >>> manager.updateIndex()
        True
        """
        self._check_initialized()
        ret = self.capi_ma.removeDictionary(identifier)
        return ret

    def updateIndex(self):
        """
        辞書のインデックスを更新して検索可能にします。

        Examples
        --------
        >>> from pygeonlp.api.dict_manager import DictManager
        >>> manager = DictManager()
        >>> manager.clearDatabase()
        True
        >>> manager.addDictionaryFromWeb('https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
        True
        >>> manager.updateIndex()
        True
        """
        self._check_initialized()
        return self.capi_ma.updateIndex()

    @staticmethod
    def get_package_files():
        """
        pip list コマンドを実行し、pygeonlp パッケージとしてインストールされた
        ファイルのフルパス一覧を取得します。

        参考： https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
        """
        import subprocess
        import pygeonlp.api

        show_args = [sys.executable, '-m',
                     'pip', 'show', '--files', 'pygeonlp']
        result = subprocess.check_output(show_args).decode('utf-8')
        lines = result.split("\n")
        files = None
        for i, line in enumerate(lines):
            if line.strip() == "Files:":
                files = lines[i+1:]
                break

        if files is None:
            raise RuntimeError("パッケージ内のファイル一覧が取得できません。")

        # pygeonlp.api.__file__ は '../site-packages/pygeonlp/api/__init__.py'
        # '../site-packages/' を base_path としてフルパスを取得する
        base_path = os.path.abspath(
            os.path.join(pygeonlp.api.__file__, '../../..'))
        files = [os.path.abspath(os.path.join(base_path, x.strip()))
                 for x in files]
        return files

    def setupBasicDatabase(self, src_dir=None):
        """
        基本的な地名解析辞書を登録したデータベースを作成します。

        Parameters
        ----------
        src_dir : str, optional
            地名解析辞書ファイルが配置されているディレクトリ。
            省略された場合には、 ``sys.prefix`` または ``site.USER_BASE`` の
            下に ``pygeonlp_basedata`` がないか探します。
            見つからない場合は ``RuntimeError`` を送出しますので、
            ディレクトリを指定してください。
        """
        data_dir = None
        base_dir = os.getcwd()
        candidates = []
        if src_dir:
            candidates.append(src_dir)

        candidates += [
            os.path.join(sys.prefix, 'pygeonlp_basedata'),
            os.path.join(site.USER_BASE, 'pygeonlp_basedata'),
            os.path.join(base_dir, 'base_data'),
            os.path.join(base_dir, 'pygeonlp_basedata'),
        ]

        for cand in candidates:
            if os.path.exists(cand):
                data_dir = cand
                break

        if not data_dir:
            files = self.__class__.get_package_files()
            for path in files:
                pos = path.find('/pygeonlp_basedata')
                if pos < 0:
                    continue

                data_dir = path[0:pos + len('/pygeonlp_basedata')]

        if not data_dir:
            raise RuntimeError("地名解析辞書がインストールされたディレクトリが見つかりません。")

        os.makedirs(self.db_dir, 0o755, exist_ok=True)
        self.init_capi_ma()

        updated = False
        if self.getDictionary('geonlp:geoshape-city') is None:
            self.addDictionaryFromFile(
                jsonfile=os.path.join(data_dir, 'geoshape-city.json'),
                csvfile=os.path.join(data_dir, 'geoshape-city.csv'))
            updated = True

        if self.getDictionary('geonlp:geoshape-pref') is None:
            self.addDictionaryFromFile(
                jsonfile=os.path.join(data_dir, 'geoshape-pref.json'),
                csvfile=os.path.join(data_dir, 'geoshape-pref.csv'))
            updated = True

        if self.getDictionary('geonlp:ksj-station-N02') is None:
            self.addDictionaryFromFile(
                jsonfile=os.path.join(data_dir, 'ksj-station-N02.json'),
                csvfile=os.path.join(data_dir, 'ksj-station-N02.csv'))
            updated = True

        if updated:
            self.updateIndex()

    def _check_initialized(self):
        """
        capi オブジェクトが初期化されていることを確認します。
        """
        if self.capi_ma is None:
            raise RuntimeError("CAPI が初期化されていません。")

    def _add_dict_identifier(self, word):
        """
        語に含まれる辞書の内部 ID "dictionary_id" を見て
        語に辞書の識別子 "dictionary_identifier" を追加します。
        """
        if word is None or 'dictionary_id' not in word or \
                'dictionary_identifier' in word:
            return word

        dictionary_id = word['dictionary_id']
        if dictionary_id in self._dict_cache:
            identifier = self._dict_cache[dictionary_id]
        else:
            identifier = self.capi_ma.getDictionaryIdentifierById(
                dictionary_id)

            self._dict_cache[dictionary_id] = identifier

        word['dictionary_identifier'] = identifier
        return word
