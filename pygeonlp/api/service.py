from collections.abc import Iterable
from logging import getLogger
import os
import re

from pygeonlp import capi

from pygeonlp.api.dictionary import Dictionary
from pygeonlp.api.metadata import Metadata
from pygeonlp.api.parser import Parser

logger = getLogger(__name__)


class ServiceError(RuntimeError):
    """
    サービス実行時に例外が起こると、このクラスが発生します。
    """
    pass


class Service(object):
    """
    GeoNLP API を提供するサービスクラスです。

    pygeonlp.api.init() を実行すると、このクラスのインスタンスが
    _default_service として作成されて利用されます。

    異なる辞書を利用する複数のサービスを並行して利用したい場合などは
    Service のインスタンスを複数作成し、それぞれのメソッドを呼びだしてください。

    Attributes
    ----------
    _dict_cache : dict
        辞書ID（整数）をキー、辞書identifier（文字列）を値にもつ
        マッピングテーブル（キャッシュ用）。
    capi_ma : pygeonlp.capi オブジェクト
        C 実装の拡張形態素解析機能を利用するためのオブジェクト。

    """

    def __init__(self, db_dir=None, geoword_rules={}, **options):
        """
        このサービスが利用する辞書や、各種設定を初期化します。

        Parameters
        ----------
        db_dir : str, optional
            利用するデータベースディレクトリのパス。
            省略した場合は ``api.get_db_dir()`` で決定します。
        geoword_rules: dict, optional
            地名語を解析するルールセットを指定します。
        options : dict, optional
            その他の解析オプションを指定します。

        Notes
        -----
        geoword_rules, options の詳細およびデフォルト値は
        ``pygeonlp.api.init()`` を参照してください。
        """
        self._dict_cache = {}
        self.options = options
        self.capi_ma = None

        if db_dir is None:
            from . import get_db_dir
            db_dir = get_db_dir()

        # データベースディレクトリの存在チェック
        if not os.path.exists(db_dir):
            raise RuntimeError(
                ("データベースディレクトリ {} がありません。".format(db_dir),
                 "setup_basic_database() で作成してください。"))

        # デフォルト値を設定
        if 'address_class' not in self.options:
            self.options['address_class'] \
                = r'^(都道府県|市区町村|行政地域|居住地名)(\/.+|)'
        elif self.options['address_class'] is None or \
                self.options['address_class'] == '':
            self.options['address_class'] = '^$'

        # capi.ma 用のオプションを構築
        capi_options = {'data_dir': db_dir}
        if 'suffix' in geoword_rules:
            if isinstance(geoword_rules['suffix'], str):
                capi_options['suffix'] = geoword_rules['suffix']
            elif isinstance(geoword_rules['suffix'], Iterable):
                capi_options['suffix'] = '|'.join(
                    list(geoword_rules['suffix']))
            else:
                raise TypeError(
                    "'suffix' は文字列またはリストで指定してください。")

        if 'excluded_word' in geoword_rules:
            if isinstance(geoword_rules['excluded_word'], str):
                capi_options['non_geoword'] = geoword_rules['excluded_word']
            elif isinstance(geoword_rules['excluded_word'], Iterable):
                capi_options['non_geoword'] = '|'.join(
                    list(geoword_rules['excluded_word']))
            else:
                raise TypeError(
                    "'excluded_word' は文字列またはリストで指定してください。")

        # その他の解析オプション
        if 'address_class' in self.options:
            if isinstance(self.options['address_class'], str):
                capi_options['address_regex'] = self.options['address_class']
            else:
                raise TypeError(
                    "'address_class' は正規表現文字列で指定してください。")

        if 'system_dic_dir' in self.options:
            if isinstance(self.options['system_dic_dir'], str):
                capi_options['system_dic_dir'] = self.options['system_dic_dir']
            else:
                raise TypeError(
                    "'system_dic_dir' は文字列で指定してください。")

        self.capi_ma = capi.MA(capi_options)

    def ma_parse(self, sentence):
        """
        センテンスを形態素解析した結果を MeCab 互換の文字列として返します。

        Parameters
        ----------
        sentence : str
            解析する文字列。

        Returns
        -------
        str
            解析結果の改行区切りテキスト。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> print(service.ma_parse('今日は国会議事堂前まで歩きました。'))
        <BLANKLINE>
        今日    名詞,副詞可能,*,*,*,*,今日,キョウ,キョー
        は      助詞,係助詞,*,*,*,*,は,ハ,ワ
        国会議事堂前    名詞,固有名詞,地名語,fuquyv:国会議事堂前駅/QUy2yP:国会議事堂前駅,*,*,国会議事堂前,,
        まで    助詞,副助詞,*,*,*,*,まで,マデ,マデ
        歩き    動詞,自立,*,*,五段・カ行イ音便,連用形,歩く,アルキ,アルキ
        まし    助動詞,*,*,*,特殊・マス,連用形,ます,マシ,マシ
        た      助動詞,*,*,*,特殊・タ,基本形,た,タ,タ
        。      記号,句点,*,*,*,*,。,。,。
        EOS
        <BLANKLINE>
        """
        self._check_initialized()
        return self.capi_ma.parse(sentence)

    def ma_parseNode(self, sentence):
        """
        センテンスを形態素解析した結果を MeCab 互換のノード配列として返します。

        Parameters
        ----------
        sentence : str
            解析する文字列。

        Returns
        -------
        list
            解析結果のリスト。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.ma_parseNode('今日は国会議事堂前まで歩きました。')
        [{'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': 'BOS/EOS', 'prononciation': '*', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': '', 'yomi': '*'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '今日', 'pos': '名詞', 'prononciation': 'キョー', 'subclass1': '副詞可能', 'subclass2': '*', 'subclass3': '*', 'surface': '今日', 'yomi': 'キョウ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '国会議事堂前', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'fuquyv:国会議事堂前駅/QUy2yP:国会議事堂前駅', 'surface': '国会議事堂前', 'yomi': ''}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'まで', 'pos': '助詞', 'prononciation': 'マデ', 'subclass1': '副助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'まで', 'yomi': 'マデ'}, {'conjugated_form': '五段・カ行イ音便', 'conjugation_type': '連用形', 'original_form': '歩く', 'pos': '動詞', 'prononciation': 'アルキ', 'subclass1': '自立', 'subclass2': '*', 'subclass3': '*', 'surface': '歩き', 'yomi': 'アルキ'}, {'conjugated_form': '特殊・マス', 'conjugation_type': '連用形', 'original_form': 'ます', 'pos': '助動詞', 'prononciation': 'マシ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'まし', 'yomi': 'マシ'}, {'conjugated_form': '特殊・タ', 'conjugation_type': '基本形', 'original_form': 'た', 'pos': '助動詞', 'prononciation': 'タ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'た', 'yomi': 'タ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': 'BOS/EOS', 'prononciation': '*', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': '', 'yomi': '*'}]
        """
        self._check_initialized()
        return self.capi_ma.parseNode(sentence)

    def getWordInfo(self, geolod_id):
        """
        指定した geolod_id を持つ語の情報を返します。
        id が辞書に存在しない場合は None を返します。

        Parameters
        ----------
        geolod_id : str or Iterable
            語の ID または ID のリストを返すイテレータ。

        Returns
        -------
        dict
            geolod_id をキー、語の情報を値に持つ dict。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.getWordInfo('fuquyv')
        {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'e630bf128884455c4994e0ac5ca49b8d', 'geolod_id': 'fuquyv', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}
        """
        self._check_initialized()
        if isinstance(geolod_id, str):
            geoword = self.capi_ma.getWordInfo(geolod_id)
            return self._add_dict_identifier(geoword)

        results = {}
        for id in geolod_id:
            geoword = self.capi_ma.getWordInfo(id)
            if geoword is None:
                results[id] = None
            else:
                results[id] = self._add_dict_identifier(geoword)

        return results

    def searchWord(self, key):
        """
        指定した表記または読みを持つ語の情報を返します。
        一致する語が辞書に存在しない場合は None を返します。

        Parameters
        ----------
        key : str
            語の表記または読み。

        Returns
        -------
        dict
            geolod_id をキー、語の情報を値に持つ dict。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.searchWord('国会議事堂前')
        {'QUy2yP': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': '1b5cc77fc2c83713a6750642f373d01f', 'geolod_id': 'QUy2yP', 'hypernym': ['東京地下鉄', '9号線千代田線'], 'institution_type': '民営鉄道', 'latitude': '35.673543333333335', 'longitude': '139.74305333333334', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}, 'fuquyv': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'e630bf128884455c4994e0ac5ca49b8d', 'geolod_id': 'fuquyv', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}
        """
        self._check_initialized()
        results = {}
        for k, w in self.capi_ma.searchWord(key).items():
            results[k] = self._add_dict_identifier(w)

        return results

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
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.getDictionary('geonlp:ksj-station-N02-2019')
        {"@context": "https://schema.org/", "@type": "Dataset", "alternateName": "", "creator": [{"@type": "Organization", "name": "株式会社情報試作室", "sameAs": "https://www.info-proto.com/"}], "dateModified": "2019-12-31T00:00:00+09:00", "description": "国土数値情報「鉄道データ（令和元年度）N02-19」（https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_3.html）から作成した、日本の鉄道駅（地下鉄を含む）の辞書です。hypernymには運営者名と路線名を記載しています。「都営」ではなく「東京都」のようになっていますので注意してください。自由フィールドとして、railway_typeに「鉄道区分」、institution_typeに「事業者種別」を含みます。", "distribution": [{"@type": "DataDownload", "contentUrl": "https://www.info-proto.com/static/ksj-station-N02-2019.csv", "encodingFormat": "text/csv"}], "identifier": ["geonlp:ksj-station-N02-2019"], "isBasedOn": {"@type": "CreativeWork", "name": "鉄道データ（令和元年度）N02-19", "url": "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_3.html"}, "keywords": ["GeoNLP", "地名辞書", "鉄道", "駅"], "license": "https://nlftp.mlit.go.jp/ksj/other/agreement.html", "name": "日本の鉄道駅（2019年）", "size": "10311", "spatialCoverage": {"@type": "Place", "geo": {"@type": "GeoShape", "box": "26.193265 127.652285 45.4161633333333 145.59723"}}, "temporalCoverage": "../..", "url": "https://www.info-proto.com/static/ksj-station-N02-2019.html"}
        """
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
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> [x.get_identifier() for x in service.getDictionaries()]
        ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02-2019']
        """
        self._check_initialized()
        dictionaries = []
        for id, metadata in self.capi_ma.getDictionaryList().items():
            # metadata['_internal_id'] = int(id)
            dictionaries.append(Metadata(metadata))

        return dictionaries

    def getActiveDictionaries(self):
        """
        インストール済み辞書のうち、解析に利用する辞書のメタデータ一覧を返します。
        デフォルトでは全てのインストール済み辞書を利用します。

        一時的に辞書を利用したくない場合、 ``disactivateDictionaries()`` で除外できます。
        除外された辞書は ``activateDictionaries()`` で再び利用可能になります。

        Returns
        -------
        list
            Metadata インスタンスのリスト。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> [x.get_identifier() for x in service.getActiveDictionaries()]
        ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02-2019']
        """
        self._check_initialized()
        dictionaries = []
        for id, metadata in self.capi_ma.getActiveDictionaries().items():
            dictionaries.append(Metadata(metadata))

        return dictionaries

    def setActiveDictionaries(self, idlist=None, pattern=None):
        """
        インストール済み辞書のうち、解析に利用する辞書を指定します。

        Parameters
        ----------
        idlist : list, optional
            利用する辞書の id または identifier のリスト。
        pattern : str, optional
            利用する辞書の identifier の正規表現。

        Raises
        ------
        RuntimeError
            idlist, pattern で指定した条件に一致する辞書が
            1つも存在しない場合に発生します。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.setActiveDictionaries(pattern=r'geonlp:geoshape')
        >>> [x.get_identifier() for x in service.getActiveDictionaries()]
        ['geonlp:geoshape-pref', 'geonlp:geoshape-city']

        Notes
        -----
        idlist と pattern のどちらかは指定する必要があります。
        """
        self._check_initialized()
        if idlist is not None and not isinstance(idlist, (list, set, tuple)):
            raise TypeError("idlist は None またはリストで指定してください。")

        if pattern is not None and not isinstance(pattern, str):
            raise TypeError("pattern は正規表現文字列で指定してください。")

        dictionaries = self.capi_ma.getDictionaryList()
        active_dictionaries = []
        for dic_id, dictionary in dictionaries.items():
            metadata = Metadata(dictionary)
            identifier = metadata.get_identifier()

            if idlist is not None and \
               (dic_id in idlist or identifier in idlist):
                logger.debug("id または identifier が idlist に含まれる")
                active_dictionaries.append(int(dic_id))
                continue

            if pattern is not None and re.search(pattern, identifier):
                logger.debug("identifier が pattern に一致")
                active_dictionaries.append(int(dic_id))
                continue

        if len(active_dictionaries) == 0:
            raise RuntimeError("条件に一致する辞書がありません。")

        self.capi_ma.setActiveDictionaries(active_dictionaries)

    def disactivateDictionaries(self, idlist=None, pattern=None):
        """
        指定した辞書を一時的に除外し、利用しないようにします。
        既に除外されている辞書は除外されたままになります。

        Parameters
        ----------
        idlist : list
            除外する辞書の内部 id または identifier のリスト。
        pattern : str
            除外する辞書の identifier を指定する正規表現。

        Raises
        ------
        RuntimeError
            全ての辞書が除外されてしまう場合に発生します。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.disactivateDictionaries(pattern=r'geonlp:geoshape')
        >>> [x.get_identifier() for x in service.getActiveDictionaries()]
        ['geonlp:ksj-station-N02-2019']
        >>> service.disactivateDictionaries(pattern=r'ksj-station')
        Traceback (most recent call last):
          ...
        RuntimeError: 全ての辞書が除外されます。

        Notes
        -----
        idlist と pattern を同時に指定した場合、どちらか一方の条件に
        一致する辞書は除外されます。
        """
        self._check_initialized()
        if idlist is not None and not isinstance(idlist, (list, set, tuple)):
            raise TypeError("idlist は None またはリストで指定してください。")

        if pattern is not None and not isinstance(pattern, str):
            raise TypeError("pattern は正規表現文字列で指定してください。")

        current_active_dictionaries = self.capi_ma.getActiveDictionaries()
        new_active_dictionaries = []
        for dic_id, dictionary in current_active_dictionaries.items():
            metadata = Metadata(dictionary)
            identifier = metadata.get_identifier()

            if idlist is not None and \
               (dic_id in idlist or identifier in idlist):
                logger.debug("id または identifier が idlist に含まれる")
                continue

            if pattern is not None and re.search(pattern, identifier):
                logger.debug("identifier が pattern に一致")
                continue

            new_active_dictionaries.append(int(dic_id))

        if len(new_active_dictionaries) == 0:
            raise RuntimeError("全ての辞書が除外されます。")

        self.capi_ma.setActiveDictionaries(new_active_dictionaries)

    def activateDictionaries(self, idlist=None, pattern=None):
        """
        指定した辞書を再び利用するようにします。
        既に利用可能な辞書は指定しなくても利用可能なままになります。

        Parameters
        ----------
        idlist : list
            利用する辞書の内部 id または identifier のリスト。
        pattern : str
            利用する辞書の identifier を指定する正規表現。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.disactivateDictionaries(pattern=r'ksj-station')
        >>> [x.get_identifier() for x in service.getActiveDictionaries()]
        ['geonlp:geoshape-city', 'geonlp:geoshape-pref']
        >>> service.activateDictionaries(pattern=r'ksj-station')
        >>> [x.get_identifier() for x in service.getActiveDictionaries()]
        ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02-2019']

        Notes
        -----
        idlist と pattern を同時に指定した場合、どちらか一方の条件に
        一致する辞書は利用可能になります。
        """
        self._check_initialized()
        if idlist is not None and not isinstance(idlist, (list, set, tuple)):
            raise TypeError("idlist は None またはリストで指定してください。")

        if pattern is not None and not isinstance(pattern, str):
            raise TypeError("pattern は正規表現文字列で指定してください。")

        dictionaries = self.capi_ma.getDictionaryList()
        active_dictionaries = [
            int(x) for x in self.capi_ma.getActiveDictionaries().keys()
        ]
        for dic_id, dictionary in dictionaries.items():
            metadata = Metadata(dictionary)
            identifier = metadata.get_identifier()

            if idlist is not None and \
               (dic_id in idlist or identifier in idlist):
                logger.debug("id または identifier が idlist に含まれる")
                active_dictionaries.append(int(dic_id))
                continue

            if pattern is not None and re.search(pattern, identifier):
                logger.debug("identifier が pattern に一致")
                active_dictionaries.append(int(dic_id))
                continue

        self.capi_ma.setActiveDictionaries(active_dictionaries)

    def getActiveClasses(self):
        """
        解析に利用する固有名クラスの一覧を返します。
        デフォルトは '.*' で、全ての固有名クラスが利用されます。

        一時的に特定の固有名クラスだけを解析対象としたい場合、
        setActiveClasses() で対象クラスを指定できます。

        Returns
        -------
        list
            利用する固有名クラス（正規表現）のリスト。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.getActiveClasses()
        ['.*']
        """
        self._check_initialized()
        return self.capi_ma.getActiveClasses()

    def setActiveClasses(self, patterns=None):
        """
        解析対象とする固有名クラスの正規表現リストを指定します。
        いずれかの正規表現に一致する固有名クラスは解析対象となります。

        '-' から始まる場合、その正規表現に一致する固有名クラスは対象外となります。

        Parameters
        ----------
        patterns : list, optional
            解析対象とする固有名クラス（str）のリスト。
            省略した場合 ['.*'] （全固有名クラス）を対象とします。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.getActiveClasses()
        ['.*']
        >>> service.searchWord('東京都')
        {'ALRYpP': {'address': '新宿区西新宿２－８－１', 'address_level': '1"', 'body': '東京', 'body_kana': 'トウキョウ', 'code': {'jisx0401': '13', 'lasdec': '130001'}, 'dictionary_id': 2, 'entry_id': '13', 'fullname': '東京都', 'geolod_id': 'ALRYpP', 'latitude': '35.6895', 'longitude': '139.69164', 'ne_class': '都道府県', 'phone': '03-5321-1111', 'suffix': ['都', ''], 'suffix_kana': ['ト', ''], 'dictionary_identifier': 'geonlp:geoshape-pref'}}
        >>> service.setActiveClasses(['.*', '-都道府県'])
        >>> service.searchWord('東京都')
        {}
        >>> service.setActiveClasses()
        >>> service.getActiveClasses()
        ['.*']
        """
        self._check_initialized()
        if patterns is None:
            patterns = ['.*']
        elif isinstance(patterns, str):
            patterns = [patterns]

        self.capi_ma.setActiveClasses(patterns)

    def clearDatabase(self):
        """
        データベースに登録されている辞書をクリアします。
        データベース内の地名語も全て削除されます。

        この関数は、データベースを作り直す際に利用します。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.clearDatabase()
        True
        >>> service.addDictionaryFromWeb(
        ...   'https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
        True
        >>> service.updateIndex()
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
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.addDictionaryFromFile(
        ...   'base_data/geoshape-city.json', 'base_data/geoshape-city.csv')
        True
        >>> service.updateIndex()
        True
        """
        self._check_initialized()
        if not isinstance(jsonfile, str) or not isinstance(csvfile, str):
            raise TypeError("jsonfile と csvfile は str で指定してください。")

        dic = Dictionary.load(jsonfile, csvfile)
        return dic.add(self.capi_ma)

    def addDictionaryFromWeb(self, url, params=None, **kwargs):
        """
        指定した URL にあるページに含まれる辞書メタデータ（JSON-LD）を取得し、
        メタデータに記載されている URL から地名解析辞書（CSVファイル）を取得し、
        データベースに登録します。

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
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.clearDatabase()
        True
        >>> service.addDictionaryFromWeb('https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
        True
        >>> service.updateIndex()
        True
        """
        self._check_initialized()
        dic = Dictionary.download(url, params, **kwargs)
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
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.saveDictionaryFromWeb('geoshape.json', 'geoshape.csv', 'https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
        True
        >>> import os
        >>> os.remove('geoshape.json')
        >>> os.remove('geoshape.csv')
        """
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
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.removeDictionary('geonlp:geoshape-city')
        True
        >>> service.updateIndex()
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
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.clearDatabase()
        True
        >>> service.addDictionaryFromWeb('https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
        True
        >>> service.updateIndex()
        True
        """
        self._check_initialized()
        return self.capi_ma.updateIndex()

    def _check_initialized(self):
        """
        capi オブジェクトが初期化されていることを確認します。
        """
        if self.capi_ma is None:
            raise ServiceError("Service が初期化されていません。")

    def _add_dict_identifier(self, word):
        """
        語に含まれる辞書の内部 ID "dictionary_id" を見て
        語に辞書の識別子 "dictionary_identifier" を追加します。
        """
        if 'dictionary_id' not in word or \
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

    def analyze(self, sentence, **kwargs):
        """
        文を解析した結果をラティス表現で返します。

        Parameters
        ----------
        sentence : str
            解析するテキスト。

        Returns
        -------
        list
            解析結果のラティス表現。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.analyze('今日は国会議事堂前まで歩きました。')
        [[{"surface": "今日", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "今日", "pos": "名詞", "prononciation": "キョー", "subclass1": "副詞可能", "subclass2": "*", "subclass3": "*", "surface": "今日", "yomi": "キョウ"}, "geometry": null, "prop": null}], [{"surface": "は", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "は", "pos": "助詞", "prononciation": "ワ", "subclass1": "係助詞", "subclass2": "*", "subclass3": "*", "surface": "は", "yomi": "ハ"}, "geometry": null, "prop": null}], [{"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "fuquyv:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geometry": {"type": "Point", "coordinates": [139.74534166666666, 35.674845]}, "prop": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "e630bf128884455c4994e0ac5ca49b8d", "geolod_id": "fuquyv", "hypernym": ["東京地下鉄", "4号線丸ノ内線"], "institution_type": "民営鉄道", "latitude": "35.674845", "longitude": "139.74534166666666", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02-2019"}}, {"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "QUy2yP:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geometry": {"type": "Point", "coordinates": [139.74305333333334, 35.673543333333335]}, "prop": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "1b5cc77fc2c83713a6750642f373d01f", "geolod_id": "QUy2yP", "hypernym": ["東京地下鉄", "9号線千代田線"], "institution_type": "民営鉄道", "latitude": "35.673543333333335", "longitude": "139.74305333333334", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02-2019"}}], [{"surface": "まで", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "まで", "pos": "助詞", "prononciation": "マデ", "subclass1": "副助詞", "subclass2": "*", "subclass3": "*", "surface": "まで", "yomi": "マデ"}, "geometry": null, "prop": null}], [{"surface": "歩き", "node_type": "NORMAL", "morphemes": {"conjugated_form": "五段・カ行イ音便", "conjugation_type": "連用形", "original_form": "歩く", "pos": "動詞", "prononciation": "アルキ", "subclass1": "自立", "subclass2": "*", "subclass3": "*", "surface": "歩き", "yomi": "アルキ"}, "geometry": null, "prop": null}], [{"surface": "まし", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・マス", "conjugation_type": "連用形", "original_form": "ます", "pos": "助動詞", "prononciation": "マシ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "まし", "yomi": "マシ"}, "geometry": null, "prop": null}], [{"surface": "た", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・タ", "conjugation_type": "基本形", "original_form": "た", "pos": "助動詞", "prononciation": "タ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "た", "yomi": "タ"}, "geometry": null, "prop": null}], [{"surface": "。", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "。", "pos": "記号", "prononciation": "。", "subclass1": "句点", "subclass2": "*", "subclass3": "*", "surface": "。", "yomi": "。"}, "geometry": null, "prop": null}]]

        Notes
        -----
        ラティス表現では全ての地名語の候補を列挙して返します。
        """
        jageocoder = kwargs.get('jageocoder', None)
        address_regex = self.options.get('address_regex', None)
        parser = Parser(service=self, jageocoder=jageocoder,
                        address_regex=address_regex)
        varray = parser.analyze_sentence(sentence, **kwargs)

        if jageocoder:
            varray = parser.add_address_candidates(varray, **kwargs)

        return varray

    def geoparse(self, sentence, jageocoder=None, filters=None,
                 scoring_class=None, scoring_options=None):
        """
        文を解析した結果を GeoJSON Feature 形式に変換可能な dict のリストを返します。

        Parameters
        ----------
        sentence : str
            解析する文字列。
        jageocoder : jageocoder, optional
            住所ジオコーダのインスタンス。
        filters : list, optional
            強制的に適用する Filter インスタンスのリスト。
        scoring_class : class, optional
            パスのスコアとノード間のスコアを計算するメソッドをもつ
            スコアリングクラス。
            省略した場合は ``scoring.ScoringClass`` を利用します。
        scoring_options : any, optional
            スコアリングクラスの初期化に渡すオプションパラメータ。

        Returns
        -------
        list
            形態素で分割した各要素のジオメトリや形態素情報、地名語情報を
            GeoJSON Feature 形式に変換可能な dict で表現し、
            そのリストを返します。

        Examples
        --------
        >>> import json
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> json.dumps({'type':'FeatureCollection', 'features':service.geoparse('今日は 国会議事堂前まで歩きました。')}, ensure_ascii=False)
        '{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": null, "properties": {"surface": "今日", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "今日", "pos": "名詞", "prononciation": "キョー", "subclass1": "副詞可能", "subclass2": "*", "subclass3": "*", "surface": "今日", "yomi": "キョウ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "は", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "は", "pos": "助詞", "prononciation": "ワ", "subclass1": "係助詞", "subclass2": "*", "subclass3": "*", "surface": "は", "yomi": "ハ"}}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [139.74305333333334, 35.673543333333335]}, "properties": {"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "QUy2yP:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geoword_properties": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "1b5cc77fc2c83713a6750642f373d01f", "geolod_id": "QUy2yP", "hypernym": ["東京地下鉄", "9号線千代田線"], "institution_type": "民営鉄道", "latitude": "35.673543333333335", "longitude": "139.74305333333334", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02-2019"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "まで", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "まで", "pos": "助詞", "prononciation": "マデ", "subclass1": "副助詞", "subclass2": "*", "subclass3": "*", "surface": "まで", "yomi": "マデ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "歩き", "node_type": "NORMAL", "morphemes": {"conjugated_form": "五段・カ行イ音便", "conjugation_type": "連用形", "original_form": "歩く", "pos": "動詞", "prononciation": "アルキ", "subclass1": "自立", "subclass2": "*", "subclass3": "*", "surface": "歩き", "yomi": "アルキ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "まし", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・マス", "conjugation_type": "連用形", "original_form": "ます", "pos": "助動詞", "prononciation": "マシ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "まし", "yomi": "マシ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "た", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・タ", "conjugation_type": "基本形", "original_form": "た", "pos": "助動詞", "prononciation": "タ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "た", "yomi": "タ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "。", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "。", "pos": "記号", "prononciation": "。", "subclass1": "句点", "subclass2": "*", "subclass3": "*", "surface": "。", "yomi": "。"}}}]}'

        Notes
        -----
        このメソッドは解析結果から適切なフィルタを判断し、候補の絞り込みやランキングを行ないます。
        """
        address_regex = self.options.get('address_class', None)
        parser = Parser(service=self, jageocoder=jageocoder,
                        address_regex=address_regex,
                        scoring_class=scoring_class,
                        scoring_options=scoring_options)
        return parser.geoparse(sentence, filters)
