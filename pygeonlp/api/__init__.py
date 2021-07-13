from logging import getLogger
import os
import site
import sys

from .service import Service, ServiceError

logger = getLogger(__name__)
_default_service = None


def get_db_dir():
    """
    データベースディレクトリを取得します。
    データベースディレクトリは次の優先順位に従って決定します。

    - 環境変数 ``GEONLP_DB_DIR`` の値
    - 環境変数 ``HOME`` が指すディレクトリの下の ``geonlp/db/``

    どちらの環境変数も指定されていない場合は ``RuntimeError`` を送出して
    終了します。

    Return
    ------
    str
        ディレクトリの絶対パス。
    """
    # 環境変数 GEONLP_DIR をチェック
    db_dir = os.environ.get('GEONLP_DB_DIR')
    if db_dir:
        db_dir = os.path.abspath(db_dir)

    # 環境変数 HOME が利用できれば $HOME/geonlp/db
    home = os.environ.get('HOME')
    if not db_dir and home:
        db_dir = os.path.join(home, 'geonlp/db')
        db_dir = os.path.abspath(db_dir)

    if not db_dir:
        raise RuntimeError(("データベースディレクトリを環境変数 "
                            "GEONLP_DB_DIR で指定してください。"))

    return db_dir


def get_jageocoder_db_dir():
    """
    jageocoder の辞書が配置されているディレクトリを取得します。
    次の優先順位に従って決定します。

    - 環境変数 ``JAGEOCODER_DB_DIR`` の値
    - 環境変数 ``HOME`` が指すディレクトリの下の ``jageocoder/db``
    - どちらの環境変数も指定されていない場合は None

    Return
    ------
    str
        ディレクトリの絶対パス、または None。
    """
    try:
        import jageocoder
        jageocoder.tree  # Flake8 の F401 エラーを回避
    except ModuleNotFoundError:
        return None

    # 環境変数 JAGEOCODER_DB_DIR をチェック
    jageocoder_db_dir = os.environ.get('JAGEOCODER_DB_DIR')
    if jageocoder_db_dir:
        return os.path.abspath(jageocoder_db_dir)

    # 環境変数 HOME が利用できれば $HOME/jageocoder/db
    home = os.environ.get('HOME')
    if home:
        jageocoder_db_dir = os.path.join(home, 'jageocoder/db')
        return os.path.abspath(jageocoder_db_dir)

    return None


def init(db_dir=None, geoword_rules={}, **options):
    """
    API を与えられたパラメータで初期化します。

    Parameters
    ----------
    db_dir : str, optional
        利用するデータベースディレクトリのパス。
        省略した場合、環境変数 ``GEONLP_DB_DIR`` が定義されていれば
        そのディレクトリを、定義されていない場合は
        ``$HOME/geonlp/db/`` を参照します。
    geoword_rules : dict, optional
        地名語抽出ルールを細かく指定します。
        詳細は下記を参照してください。
    options : dict, optional
        その他の解析オプションを指定します。
        詳細は下記を参照してください。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()

    >>> import os
    >>> import pygeonlp.api as api
    >>> api.init(geoword_rules={'excluded_word':['医療センター']})

    Notes
    -----
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


    その他の解析オプションは以下の通りです。

    address_class : str
        住所要素とみなす固有名クラスを正規表現で指定します。
        たとえば固有名クラスが「都道府県」である地名語から始まる住所表記だけを
        住所として解析したい（市区町村から始まる場合は無視したい）場合は
        r"^都道府県" を指定します。
        デフォルト値は r"^(都道府県|市区町村|行政地域|居住地名)(/.+|)" です。

    system_dic_dir : str
        MeCab システム辞書のディレクトリを指定します。
        省略した場合はデフォルトのシステム辞書を利用します。

    実際には、この関数は初期化した Service オブジェクト
    ``_default_service`` を作成して利用可能な状態にします。
    ``pygeonlp.api`` の各関数は、この Service オブジェクトの
    メンバ関数を呼びだすヘルパー関数として実装されています。

    異なるパラメータで初期化した Service オブジェクトを複数生成し、
    それぞれのメンバ関数を呼びだすことも可能です。
    """
    global _default_service
    if _default_service:
        del _default_service

    _default_service = Service(db_dir, geoword_rules, **options)


def ma_parse(sentence):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> print(ma_parse('今日は国会議事堂前まで歩きました。'))
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
    _check_initialized()
    return _default_service.ma_parse(sentence)


def ma_parseNode(sentence):
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

    Example
    -------
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.ma_parseNode('今日は国会議事堂前まで歩きました。')
    [{'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': 'BOS/EOS', 'prononciation': '*', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': '', 'yomi': '*'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '今日', 'pos': '名詞', 'prononciation': 'キョー', 'subclass1': '副詞可能', 'subclass2': '*', 'subclass3': '*', 'surface': '今日', 'yomi': 'キョウ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '国会議事堂前', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'fuquyv:国会議事堂前駅/QUy2yP:国会議事堂前駅', 'surface': '国会議事堂前', 'yomi': ''}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'まで', 'pos': '助詞', 'prononciation': 'マデ', 'subclass1': '副助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'まで', 'yomi': 'マデ'}, {'conjugated_form': '五段・カ行イ音便', 'conjugation_type': '連用形', 'original_form': '歩く', 'pos': '動詞', 'prononciation': 'アルキ', 'subclass1': '自立', 'subclass2': '*', 'subclass3': '*', 'surface': '歩き', 'yomi': 'アルキ'}, {'conjugated_form': '特殊・マス', 'conjugation_type': '連用形', 'original_form': 'ます', 'pos': '助動詞', 'prononciation': 'マシ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'まし', 'yomi': 'マシ'}, {'conjugated_form': '特殊・タ', 'conjugation_type': '基本形', 'original_form': 'た', 'pos': '助動詞', 'prononciation': 'タ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'た', 'yomi': 'タ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': 'BOS/EOS', 'prononciation': '*', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': '', 'yomi': '*'}]

    """
    _check_initialized()
    return _default_service.ma_parseNode(sentence)


def getWordInfo(geolod_id):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.getWordInfo('fuquyv')
    {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'e630bf128884455c4994e0ac5ca49b8d', 'geolod_id': 'fuquyv', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}
    """
    _check_initialized()
    return _default_service.getWordInfo(geolod_id)


def searchWord(key):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.searchWord('国会議事堂前')
    {'QUy2yP': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': '1b5cc77fc2c83713a6750642f373d01f', 'geolod_id': 'QUy2yP', 'hypernym': ['東京地下鉄', '9号線千代田線'], 'institution_type': '民営鉄道', 'latitude': '35.673543333333335', 'longitude': '139.74305333333334', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}, 'fuquyv': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'e630bf128884455c4994e0ac5ca49b8d', 'geolod_id': 'fuquyv', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}
    """
    _check_initialized()
    return _default_service.searchWord(key)


def getDictionary(id_or_identifier):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.getDictionary('geonlp:ksj-station-N02-2019')
    {"@context": "https://schema.org/", "@type": "Dataset", "alternateName": "", "creator": [{"@type": "Organization", "name": "株式会社情報試作室", "sameAs": "https://www.info-proto.com/"}], "dateModified": "2019-12-31T00:00:00+09:00", "description": "国土数値情報「鉄道データ（令和元年度）N02-19」（https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_3.html）から作成した、日本の鉄道駅（地下鉄を含む）の辞書です。hypernymには運営者名と路線名を記載しています。「都営」ではなく「東京都」のようになっていますので注意してください。自由フィールドとして、railway_typeに「鉄道区分」、institution_typeに「事業者種別」を含みます。", "distribution": [{"@type": "DataDownload", "contentUrl": "https://www.info-proto.com/static/ksj-station-N02-2019.csv", "encodingFormat": "text/csv"}], "identifier": ["geonlp:ksj-station-N02-2019"], "isBasedOn": {"@type": "CreativeWork", "name": "鉄道データ（令和元年度）N02-19", "url": "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_3.html"}, "keywords": ["GeoNLP", "地名辞書", "鉄道", "駅"], "license": "https://nlftp.mlit.go.jp/ksj/other/agreement.html", "name": "日本の鉄道駅（2019年）", "size": "10311", "spatialCoverage": {"@type": "Place", "geo": {"@type": "GeoShape", "box": "26.193265 127.652285 45.4161633333333 145.59723"}}, "temporalCoverage": "../..", "url": "https://www.info-proto.com/static/ksj-station-N02-2019.html"}
    """
    _check_initialized()
    return _default_service.getDictionary(id_or_identifier)


def getDictionaries():
    """
    インストール済み辞書のメタデータ一覧を返します。

    Returns
    -------
    list
        Metadata インスタンスのリスト。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> sorted([x.get_identifier() for x in api.getDictionaries()])
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02-2019']
    """
    _check_initialized()
    return _default_service.getDictionaries()


def getActiveDictionaries():
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> sorted([x.get_identifier() for x in api.getActiveDictionaries()])
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02-2019']
    """
    _check_initialized()
    return _default_service.getActiveDictionaries()


def setActiveDictionaries(idlist=None, pattern=None):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.setActiveDictionaries(pattern=r'geonlp:geoshape')
    >>> sorted([x.get_identifier() for x in api.getActiveDictionaries()])
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref']

    Notes
    -----
    idlist と pattern のどちらかは指定する必要があります。
    """
    _check_initialized()
    return _default_service.setActiveDictionaries(idlist, pattern)


def disactivateDictionaries(idlist=None, pattern=None):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.disactivateDictionaries(pattern=r'geonlp:geoshape')
    >>> [x.get_identifier() for x in api.getActiveDictionaries()]
    ['geonlp:ksj-station-N02-2019']
    >>> api.disactivateDictionaries(pattern=r'ksj-station')
    Traceback (most recent call last):
      ...
    RuntimeError: 全ての辞書が除外されます。

    Notes
    -----
    idlist と pattern を同時に指定した場合、どちらか一方の条件に
    一致する辞書は除外されます。
    """
    _check_initialized()
    return _default_service.disactivateDictionaries(idlist, pattern)


def activateDictionaries(idlist=None, pattern=None):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.disactivateDictionaries(pattern=r'ksj-station')
    >>> sorted([x.get_identifier() for x in api.getActiveDictionaries()])
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref']
    >>> api.activateDictionaries(pattern=r'ksj-station')
    >>> sorted([x.get_identifier() for x in api.getActiveDictionaries()])
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02-2019']

    Notes
    -----
    idlist と pattern を同時に指定した場合、どちらか一方の条件に
    一致する辞書は利用可能になります。
    """
    _check_initialized()
    return _default_service.activateDictionaries(idlist, pattern)


def getActiveClasses():
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.getActiveClasses()
    ['.*']
    """
    _check_initialized()
    return _default_service.getActiveClasses()


def setActiveClasses(patterns=None):
    """
    解析対象とする固有名クラスの正規表現リストを指定します。
    いずれかの正規表現に一致する固有名クラスは解析対象となります。

    '-' から始まる場合、その正規表現に一致する固有名クラスは対象外となります。

    Parameters
    ----------
    patterns : list, optional
        解析対象とする固有名クラス（str）のリスト。
        省略した場合 ['.*'] （全固有名クラス）を対象とします。

    Usage
    -----
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.getActiveClasses()
    ['.*']
    >>> api.searchWord('東京都')
    {'ALRYpP': {'address': '新宿区西新宿２－８－１', 'address_level': '1"', 'body': '東京', 'body_kana': 'トウキョウ', 'code': {'jisx0401': '13', 'lasdec': '130001'}, 'dictionary_id': 2, 'entry_id': '13', 'fullname': '東京都', 'geolod_id': 'ALRYpP', 'latitude': '35.6895', 'longitude': '139.69164', 'ne_class': '都道府県', 'phone': '03-5321-1111', 'suffix': ['都', ''], 'suffix_kana': ['ト', ''], 'dictionary_identifier': 'geonlp:geoshape-pref'}}
    >>> api.setActiveClasses(['.*', '-都道府県'])
    >>> api.searchWord('東京都')
    {}
    >>> api.setActiveClasses()
    >>> api.getActiveClasses()
    ['.*']
    """
    _check_initialized()
    return _default_service.setActiveClasses(patterns)


def clearDatabase():
    """
    地名語データベースに登録されている辞書をクリアします。
    データベース内の地名語も全て削除されます。

    この関数は、データベースを作り直す際に利用します。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.clearDatabase()
    >>> api.addDictionaryFromWeb('https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
    True
    >>> api.updateIndex()
    """
    _check_initialized()
    _default_service.clearDatabase()


def addDictionaryFromFile(jsonfile, csvfile):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.addDictionaryFromFile('base_data/geoshape-city.json', 'base_data/geoshape-city.csv')
    True
    >>> api.updateIndex()
    """
    _check_initialized()
    return _default_service.addDictionaryFromFile(jsonfile, csvfile)


def addDictionaryFromWeb(url, params=None, **kwargs):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.clearDatabase()
    >>> api.addDictionaryFromWeb('https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
    True
    >>> api.updateIndex()
    """
    _check_initialized()
    return _default_service.addDictionaryFromWeb(url, params, **kwargs)


def saveDictionaryFromWeb(jsonfile, csvfile, url, params=None, **kwargs):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.saveDictionaryFromWeb('geoshape.json', 'geoshape.csv', 'https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
    True
    >>> import os
    >>> os.remove('geoshape.json')
    >>> os.remove('geoshape.csv')
    """
    _check_initialized()
    return _default_service.saveDictionaryFromWeb(jsonfile, csvfile, url,
                                                  params, **kwargs)


def removeDictionary(identifier):
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
        指定した辞書が登録されていない場合は RuntimeError が発生します。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.removeDictionary('geonlp:geoshape-city')
    True
    >>> api.updateIndex()
    """
    _check_initialized()
    return _default_service.removeDictionary(identifier)


def updateIndex():
    """
    辞書のインデックスを更新して検索可能にします。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.clearDatabase()
    >>> api.addDictionaryFromWeb('https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/')
    True
    >>> api.updateIndex()
    """
    _check_initialized()
    _default_service.updateIndex()


def analyze(sentence, **kwargs):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.analyze('今日は国会議事堂前まで歩きました。')
    [[{"surface": "今日", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "今日", "pos": "名詞", "prononciation": "キョー", "subclass1": "副詞可能", "subclass2": "*", "subclass3": "*", "surface": "今日", "yomi": "キョウ"}, "geometry": null, "prop": null}], [{"surface": "は", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "は", "pos": "助詞", "prononciation": "ワ", "subclass1": "係助詞", "subclass2": "*", "subclass3": "*", "surface": "は", "yomi": "ハ"}, "geometry": null, "prop": null}], [{"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "fuquyv:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geometry": {"type": "Point", "coordinates": [139.74534166666666, 35.674845]}, "prop": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "e630bf128884455c4994e0ac5ca49b8d", "geolod_id": "fuquyv", "hypernym": ["東京地下鉄", "4号線丸ノ内線"], "institution_type": "民営鉄道", "latitude": "35.674845", "longitude": "139.74534166666666", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02-2019"}}, {"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "QUy2yP:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geometry": {"type": "Point", "coordinates": [139.74305333333334, 35.673543333333335]}, "prop": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "1b5cc77fc2c83713a6750642f373d01f", "geolod_id": "QUy2yP", "hypernym": ["東京地下鉄", "9号線千代田線"], "institution_type": "民営鉄道", "latitude": "35.673543333333335", "longitude": "139.74305333333334", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02-2019"}}], [{"surface": "まで", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "まで", "pos": "助詞", "prononciation": "マデ", "subclass1": "副助詞", "subclass2": "*", "subclass3": "*", "surface": "まで", "yomi": "マデ"}, "geometry": null, "prop": null}], [{"surface": "歩き", "node_type": "NORMAL", "morphemes": {"conjugated_form": "五段・カ行イ音便", "conjugation_type": "連用形", "original_form": "歩く", "pos": "動詞", "prononciation": "アルキ", "subclass1": "自立", "subclass2": "*", "subclass3": "*", "surface": "歩き", "yomi": "アルキ"}, "geometry": null, "prop": null}], [{"surface": "まし", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・マス", "conjugation_type": "連用形", "original_form": "ます", "pos": "助動詞", "prononciation": "マシ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "まし", "yomi": "マシ"}, "geometry": null, "prop": null}], [{"surface": "た", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・タ", "conjugation_type": "基本形", "original_form": "た", "pos": "助動詞", "prononciation": "タ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "た", "yomi": "タ"}, "geometry": null, "prop": null}], [{"surface": "。", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "。", "pos": "記号", "prononciation": "。", "subclass1": "句点", "subclass2": "*", "subclass3": "*", "surface": "。", "yomi": "。"}, "geometry": null, "prop": null}]]

    Notes
    -----
    ラティス表現では全ての地名語の候補を列挙して返します。
    """
    _check_initialized()
    return _default_service.analyze(sentence, **kwargs)


def geoparse(sentence, jageocoder=None, filters=None,
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> json.dumps({'type':'FeatureCollection', 'features':api.geoparse('今日は国会議事堂前まで歩きました。')}, ensure_ascii=False)
    '{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": null, "properties": {"surface": "今日", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "今日", "pos": "名詞", "prononciation": "キョー", "subclass1": "副詞可能", "subclass2": "*", "subclass3": "*", "surface": "今日", "yomi": "キョウ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "は", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "は", "pos": "助詞", "prononciation": "ワ", "subclass1": "係助詞", "subclass2": "*", "subclass3": "*", "surface": "は", "yomi": "ハ"}}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [139.74305333333334, 35.673543333333335]}, "properties": {"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "QUy2yP:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geoword_properties": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "1b5cc77fc2c83713a6750642f373d01f", "geolod_id": "QUy2yP", "hypernym": ["東京地下鉄", "9号線千代田線"], "institution_type": "民営鉄道", "latitude": "35.673543333333335", "longitude": "139.74305333333334", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02-2019"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "まで", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "まで", "pos": "助詞", "prononciation": "マデ", "subclass1": "副助詞", "subclass2": "*", "subclass3": "*", "surface": "まで", "yomi": "マデ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "歩き", "node_type": "NORMAL", "morphemes": {"conjugated_form": "五段・カ行イ音便", "conjugation_type": "連用形", "original_form": "歩く", "pos": "動詞", "prononciation": "アルキ", "subclass1": "自立", "subclass2": "*", "subclass3": "*", "surface": "歩き", "yomi": "アルキ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "まし", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・マス", "conjugation_type": "連用形", "original_form": "ます", "pos": "助動詞", "prononciation": "マシ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "まし", "yomi": "マシ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "た", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・タ", "conjugation_type": "基本形", "original_form": "た", "pos": "助動詞", "prononciation": "タ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "た", "yomi": "タ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "。", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "。", "pos": "記号", "prononciation": "。", "subclass1": "句点", "subclass2": "*", "subclass3": "*", "surface": "。", "yomi": "。"}}}]}'

    Notes
    -----
    このメソッドは解析結果から適切なフィルタを判断し、候補の絞り込みやランキングを行ないます。
    """
    _check_initialized()
    return _default_service.geoparse(sentence, jageocoder, filters,
                                     scoring_class, scoring_options)


def default_service():
    """
    Default Service オブジェクトを返します。

    通常はこのメソッドを利用する必要はありません。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> type(api.default_service())
    <class 'pygeonlp.api.service.Service'>
    """
    return _default_service


def setup_basic_database(db_dir=None, src_dir=None):
    """
    基本的な地名解析辞書を登録したデータベースを作成します。

    Parameters
    ----------
    db_dir : str, optional
        データベースディレクトリを指定します。
        ここにデータベースファイルを作成します。
        既にデータベースが存在する場合は追記します（つまり、
        既に登録済みの地名解析辞書のデータは失われません）。
        省略された場合には ``get_db_dir()`` で決定します。

    src_dir : str, optional
        地名解析辞書ファイルが配置されているディレクトリ。
        省略された場合には、 ``sys.prefix`` または ``site.USER_BASE`` の
        下に ``pygeonlp_basedata`` がないか探します。
        見つからない場合は ``RuntimeError`` を送出しますので、
        ディレクトリを指定してください。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.setup_basic_database()
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
        raise RuntimeError("地名解析辞書がインストールされたディレクトリが見つかりません。")

    if db_dir is None:
        db_dir = get_db_dir()

    os.makedirs(db_dir, 0o755, exist_ok=True)
    service = Service(db_dir=db_dir)

    updated = False
    if service.getDictionary('geonlp:geoshape-city') is None:
        service.addDictionaryFromFile(
            jsonfile=os.path.join(data_dir, 'geoshape-city.json'),
            csvfile=os.path.join(data_dir, 'geoshape-city.csv'))
        updated = True

    if service.getDictionary('geonlp:geoshape-pref') is None:
        service.addDictionaryFromFile(
            jsonfile=os.path.join(data_dir, 'geoshape-pref.json'),
            csvfile=os.path.join(data_dir, 'geoshape-pref.csv'))
        updated = True

    if service.getDictionary('geonlp:ksj-station-N02-2019') is None:
        service.addDictionaryFromFile(
            jsonfile=os.path.join(data_dir, 'ksj-station-N02-2019.json'),
            csvfile=os.path.join(data_dir, 'ksj-station-N02-2019.csv'))
        updated = True

    if updated:
        service.updateIndex()


def _check_initialized():
    """
    Default Service オブジェクトが ``init()`` で初期化されていることを確認するための
    プライベートメソッドです。

    この関数は API メソッド内でチェックのために呼びだすものなので、
    ユーザが呼びだす必要は基本的にありません。

    Raises
    ------
    ServiceError
        init() を呼ぶ前に API メソッドを利用しようとすると発生します。
    """
    if _default_service is None:
        raise ServiceError("APIが初期化されていません。")
