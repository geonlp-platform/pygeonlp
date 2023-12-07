from collections.abc import Iterable
from logging import getLogger
import os
import re
from typing import Union

from pygeonlp import capi

from pygeonlp.api.metadata import Metadata

logger = getLogger(__name__)


class ServiceError(RuntimeError):
    """
    サービス実行時に例外が起こると、このクラスが発生します。
    """
    pass


class Service(object):
    """
    文の解析や地名語の検索機能を提供する低水準APIサービスクラスです。

    Attributes
    ----------
    _dict_cache : dict
        辞書ID（整数）をキー、辞書identifier（文字列）を値にもつ
        マッピングテーブル（キャッシュ用）。
    capi_ma : pygeonlp.capi オブジェクト
        C 実装の拡張形態素解析機能を利用するためのオブジェクト。
    db_dir: str
        このサービスが利用するデータベースディレクトリのパス。
    """

    def __init__(self,
                 db_dir: Union[str, bytes, os.PathLike, None] = None,
                 geoword_rules: dict = {}, **options):
        """
        このサービスが利用する辞書や、各種設定を初期化します。

        Parameters
        ----------
        db_dir : PathLike, optional
            利用するデータベースディレクトリのパス。
            省略した場合は ``api.get_db_dir()`` で決定します。
        geoword_rules: dict, optional
            地名語を解析するルールセットを指定します。
        options : dict, optional
            その他の解析オプションを指定します。

        Note
        ----
        地名語抽出ルールとして指定できる項目は以下の通りです。

        suffix : list of str
            地名接尾語を定義します。通常、一般名詞などの前に地名がくる場合、
            地名修飾語として解析されます。
            例：千代田区立 -> 千代田（名詞・固有名詞・地名語）＋区立（名詞・一般）

            地名接尾語として「立」を定義すると、
            千代田区（名詞・固有名詞・地名語）＋立（名詞・接尾・地名語）と
            解析されるようになります。
            地名接尾辞は "立,リツ,リツ" のように表層形、読み、発音を
            カンマで区切った文字列として定義してください。
            デフォルト値は ["前,マエ,マエ", "内,ナイ,ナイ", "立,リツ,リツ",
            "境,サカイ,サカイ", "東,ヒガシ,ヒガシ", "西,ニシ,ニシ",
            "南,ミナミ,ミナミ", "北,キタ,キタ"] です。

        excluded_word : list of str
            非地名語を定義します。
            地名解析辞書に登録されている語は地名語として解析されます。
            例：本部に行く -> 本部（名詞・固有名詞・地名語）＋に（助詞）……
            しかし特定の語を地名語として解析したくない場合は非地名語として
            定義してください。
            デフォルト値は ["本部","一部","月"] です。
            環境変数 GEONLP_EXCLUDED_WORD でデフォルト値を設定できます。


        その他の解析オプションは以下の通りです。

        address_class : str
            住所要素とみなす固有名クラスを正規表現で指定します。
            たとえば固有名クラスが「都道府県」である地名語から始まる住所表記だけを
            住所として解析したい（市区町村から始まる場合は無視したい）場合は
            r"^都道府県" を指定します。
            デフォルト値は r"^(都道府県|市区町村|行政地域|居住地名)(/.+|)" です。
            環境変数 GEONLP_ADRESS_CLASS でデフォルト値を設定できます。

        system_dic_dir : str
            MeCab システム辞書のディレクトリを指定します。
            省略した場合はデフォルトシステム辞書を利用します。
            環境変数 GEONLP_MECAB_DIC_DIR でデフォルト値を設定できます。
        """
        self._dict_cache = {}
        self.options = options
        self.capi_ma = None

        if db_dir is None:
            from . import get_db_dir
            db_dir = get_db_dir()

        self.db_dir = db_dir

        # データベースディレクトリの存在チェック
        if not os.path.exists(db_dir):
            raise RuntimeError(
                ("データベースディレクトリ {} がありません。".format(db_dir),
                 "setup_basic_database() で作成してください。"))

        # capi.ma 用のオプションを構築
        capi_options = {'data_dir': str(db_dir)}
        if 'suffix' in geoword_rules:
            suffix = geoword_rules["suffix"]
            if isinstance(suffix, str):
                capi_options['suffix'] = suffix
            elif isinstance(geoword_rules['suffix'], Iterable):
                capi_options['suffix'] = '|'.join(list(suffix))
            else:
                raise TypeError(
                    "'suffix' は文字列またはリストで指定してください。")

        excluded_word = geoword_rules.get(
            "excluded_word",
            os.environ.get("GEONLP_EXCLUDED_WORD", None)
        )
        if isinstance(excluded_word, str):
            capi_options['non_geoword'] = excluded_word
        elif isinstance(excluded_word, Iterable):
            capi_options['non_geoword'] = '|'.join(list(excluded_word))
        elif excluded_word is not None:
            raise TypeError(
                "'excluded_word' は文字列またはリストで指定してください。")

        # その他の解析オプション
        address_class = self.options.get(
            "address_class",
            os.environ.get(
                "GEONLP_ADDRESS_CLASS",
                r'^(都道府県|市区町村|行政地域|居住地名)(\/.+|)'
            )
        )
        if isinstance(address_class, str):
            if address_class == "":
                address_class = "^$"

            capi_options['address_regex'] = address_class
        else:
            raise TypeError(
                "'address_class' は正規表現文字列で指定してください。")

        system_dic_dir = self.options.get(
            "system_dic_dir",
            os.environ.get("GEONLP_MECAB_DIC_DIR", None)
        )
        if system_dic_dir is None:
            pass
        elif isinstance(system_dic_dir, str):
            capi_options['system_dic_dir'] = system_dic_dir
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
        国会議事堂前    名詞,固有名詞,地名語,Bn4q6d:国会議事堂前駅/cE8W4w:国会議事堂前駅,*,*,国会議事堂前,,
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
        [{'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': 'BOS/EOS', 'prononciation': '*', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': '', 'yomi': '*'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '今日', 'pos': '名詞', 'prononciation': 'キョー', 'subclass1': '副詞可能', 'subclass2': '*', 'subclass3': '*', 'surface': '今日', 'yomi': 'キョウ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '国会議事堂前', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'Bn4q6d:国会議事堂前駅/cE8W4w:国会議事堂前駅', 'surface': '国会議事堂前', 'yomi': ''}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'まで', 'pos': '助詞', 'prononciation': 'マデ', 'subclass1': '副助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'まで', 'yomi': 'マデ'}, {'conjugated_form': '五段・カ行イ音便', 'conjugation_type': '連用形', 'original_form': '歩く', 'pos': '動詞', 'prononciation': 'アルキ', 'subclass1': '自立', 'subclass2': '*', 'subclass3': '*', 'surface': '歩き', 'yomi': 'アルキ'}, {'conjugated_form': '特殊・マス', 'conjugation_type': '連用形', 'original_form': 'ます', 'pos': '助動詞', 'prononciation': 'マシ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'まし', 'yomi': 'マシ'}, {'conjugated_form': '特殊・タ', 'conjugation_type': '基本形', 'original_form': 'た', 'pos': '助動詞', 'prononciation': 'タ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'た', 'yomi': 'タ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': 'BOS/EOS', 'prononciation': '*', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': '', 'yomi': '*'}]
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
        >>> service.getWordInfo('Bn4q6d')
        {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'LrGGxY', 'geolod_id': 'Bn4q6d', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02'}
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
        {'Bn4q6d': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'LrGGxY', 'geolod_id': 'Bn4q6d', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02'}, 'cE8W4w': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': '4NFELa', 'geolod_id': 'cE8W4w', 'hypernym': ['東京地下鉄', '9号線千代田線'], 'institution_type': '民営鉄道', 'latitude': '35.673543333333335', 'longitude': '139.74305333333334', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02'}}
        """
        self._check_initialized()
        results = {}
        for k, w in self.capi_ma.searchWord(key).items():
            results[k] = self._add_dict_identifier(w)

        return results

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
        >>> sorted([x.get_identifier() for x in service.getActiveDictionaries()])
        ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02']
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

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.setActiveDictionaries(pattern=r'geonlp:geoshape')
        >>> sorted([x.get_identifier() for x in service.getActiveDictionaries()])
        ['geonlp:geoshape-city', 'geonlp:geoshape-pref']

        Note
        ----
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
            logger.debug("条件に一致する辞書がありません。")

        self.capi_ma.setActiveDictionaries(active_dictionaries)

    def disactivateDictionaries(self, idlist=None, pattern=None):
        """
        指定した辞書を一時的に除外し、利用しないようにします。
        既に除外されている辞書は除外されたままになります。
        新たに除外された辞書のリストを返します。

        Parameters
        ----------
        idlist : list
            除外する辞書の内部 id または identifier のリスト。
        pattern : str
            除外する辞書の identifier を指定する正規表現。

        Returns
        -------
        list
            新たに除外された辞書の identifier のリスト。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> service.disactivateDictionaries(pattern=r'geonlp:geoshape')
        ['geonlp:geoshape-city', 'geonlp:geoshape-pref']
        >>> [x.get_identifier() for x in service.getActiveDictionaries()]
        ['geonlp:ksj-station-N02']
        >>> service.disactivateDictionaries(pattern=r'ksj-station')
        ['geonlp:ksj-station-N02']
        >>> [x.get_identifier() for x in service.getActiveDictionaries()]
        []

        Note
        ----
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
        disactivated_dictionaries = []
        for dic_id, dictionary in current_active_dictionaries.items():
            metadata = Metadata(dictionary)
            identifier = metadata.get_identifier()

            if idlist is not None and \
               (dic_id in idlist or identifier in idlist):
                logger.debug("id または identifier が idlist に含まれる")
                disactivated_dictionaries.append(identifier)
                continue

            if pattern is not None and re.search(pattern, identifier):
                logger.debug("identifier が pattern に一致")
                disactivated_dictionaries.append(identifier)
                continue

            new_active_dictionaries.append(int(dic_id))

        if len(new_active_dictionaries) == 0:
            logger.debug("全ての辞書が除外されます。")

        self.capi_ma.setActiveDictionaries(new_active_dictionaries)

        return disactivated_dictionaries

    def activateDictionaries(self, idlist=None, pattern=None):
        """
        指定した辞書を再び利用するようにします。
        既に利用可能な辞書は指定しなくても利用可能なままになります。
        新たに利用可能になった辞書のリストを返します。

        Parameters
        ----------
        idlist : list
            利用する辞書の内部 id または identifier のリスト。
        pattern : str
            利用する辞書の identifier を指定する正規表現。

        Returns
        -------
        list
            新たに利用可能になった辞書の identifier のリスト。

        Examples
        --------
        >>> from pygeonlp.api.service import Service
        >>> service = Service()
        >>> sorted(service.disactivateDictionaries(pattern=r'.*'))
        ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02']
        >>> [x.get_identifier() for x in service.getActiveDictionaries()]
        []
        >>> service.activateDictionaries(pattern=r'ksj-station')
        ['geonlp:ksj-station-N02']
        >>> [x.get_identifier() for x in service.getActiveDictionaries()]
        ['geonlp:ksj-station-N02']

        Note
        ----
        idlist と pattern を同時に指定した場合、どちらか一方の条件に
        一致する辞書は利用可能になります。
        """
        self._check_initialized()
        if idlist is not None and not isinstance(idlist, (list, set, tuple)):
            raise TypeError("idlist は None またはリストで指定してください。")

        if pattern is not None and not isinstance(pattern, str):
            raise TypeError("pattern は正規表現文字列で指定してください。")

        dictionaries = self.capi_ma.getDictionaryList()
        activated_dictionaries = []
        active_dictionaries = [
            int(x) for x in self.capi_ma.getActiveDictionaries().keys()
        ]
        for dic_id, dictionary in dictionaries.items():
            metadata = Metadata(dictionary)
            identifier = metadata.get_identifier()

            if int(dic_id) in active_dictionaries:
                # 既に有効
                continue

            if idlist is not None and \
               (dic_id in idlist or identifier in idlist):
                logger.debug("id または identifier が idlist に含まれる")
                active_dictionaries.append(int(dic_id))
                activated_dictionaries.append(identifier)
                continue

            if pattern is not None and re.search(pattern, identifier) and \
                    int(dic_id) not in active_dictionaries:
                logger.debug("identifier が pattern に一致")
                active_dictionaries.append(int(dic_id))
                activated_dictionaries.append(identifier)
                continue

        self.capi_ma.setActiveDictionaries(active_dictionaries)

        return activated_dictionaries

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
        {'QknGsa': {...'dictionary_identifier': 'geonlp:geoshape-pref'}}
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
