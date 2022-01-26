from logging import getLogger
import os
import warnings

from deprecated import deprecated
import jageocoder

from pygeonlp.api.dict_manager import DictManager
from pygeonlp.api.workflow import Workflow, WorkflowError

logger = getLogger(__name__)
_default_workflow = None
_default_manager = None


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
    **deprecated**

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
    warnings.warn(('get_jageocoder_db_dir() はver.1.2で廃止予定です。'
                   'jageocoder.get_db_dir() を利用してください。'),
                  DeprecationWarning)

    return jageocoder.get_db_dir()


def init(db_dir=None, **options):
    """
    API をデフォルトパラメータで初期化します。

    Parameters
    ----------
    db_dir : PathLike, optional
        データベースディレクトリ。
        省略した場合は ``api.init.get_db_dir()`` が返す値を利用します。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()

    Note
    ----
    実際には、この関数は初期化した Workflow オブジェクト ``_default_workflow``
    および DictManager オブジェクト ``_default_manager`` を作成し、
    利用可能な状態にします。
    ``pygeonlp.api`` の各関数は、これらのオブジェクトの
    メンバ関数を呼びだすヘルパー関数として実装されています。

    Workflow のパラメータを変更したい場合、 ``api.default_workflow()`` で
    Workflow オブジェクトを取得して ``set_parser()`` などを呼びだします。

    異なるパラメータで初期化した Workflow オブジェクトを生成し、
    直接そのメンバ関数を呼びだすことも可能です。
    """
    global _default_workflow, _default_manager
    if _default_workflow:
        del _default_workflow

    if _default_manager:
        del _default_manager

    _default_workflow = Workflow(db_dir=db_dir, **options)
    _default_manager = DictManager(db_dir=db_dir)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.service.Service" directly.')
def ma_parse(sentence):
    """
    センテンスを形態素解析した結果を MeCab 互換の文字列として返します。
    *deprecated* この関数は低水準 API なので、廃止予定です。

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
    >>> print(api.ma_parse('今日は国会議事堂前まで歩きました。'))
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
    _check_initialized()
    return _default_workflow.parser.service.ma_parse(sentence)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.service.Service" directly.')
def ma_parseNode(sentence):
    """
    センテンスを形態素解析した結果を MeCab 互換のノード配列として返します。
    *deprecated* この関数は低水準 API なので、廃止予定です。

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
    [{'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': 'BOS/EOS', 'prononciation': '*', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': '', 'yomi': '*'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '今日', 'pos': '名詞', 'prononciation': 'キョー', 'subclass1': '副詞可能', 'subclass2': '*', 'subclass3': '*', 'surface': '今日', 'yomi': 'キョウ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '国会議事堂前', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'Bn4q6d:国会議事堂前駅/cE8W4w:国会議事堂前駅', 'surface': '国会議事堂前', 'yomi': ''}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'まで', 'pos': '助詞', 'prononciation': 'マデ', 'subclass1': '副助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'まで', 'yomi': 'マデ'}, {'conjugated_form': '五段・カ行イ音便', 'conjugation_type': '連用形', 'original_form': '歩く', 'pos': '動詞', 'prononciation': 'アルキ', 'subclass1': '自立', 'subclass2': '*', 'subclass3': '*', 'surface': '歩き', 'yomi': 'アルキ'}, {'conjugated_form': '特殊・マス', 'conjugation_type': '連用形', 'original_form': 'ます', 'pos': '助動詞', 'prononciation': 'マシ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'まし', 'yomi': 'マシ'}, {'conjugated_form': '特殊・タ', 'conjugation_type': '基本形', 'original_form': 'た', 'pos': '助動詞', 'prononciation': 'タ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'た', 'yomi': 'タ'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}, {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': 'BOS/EOS', 'prononciation': '*', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': '', 'yomi': '*'}]

    """
    _check_initialized()
    return _default_workflow.parser.service.ma_parseNode(sentence)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.service.Service" directly.')
def getWordInfo(geolod_id):
    """
    指定した geolod_id を持つ語の情報を返します。
    id が辞書に存在しない場合は None を返します。
    *deprecated* この関数は低水準 API なので、廃止予定です。

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
    >>> api.getWordInfo('Bn4q6d')
    {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'LrGGxY', 'geolod_id': 'Bn4q6d', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02'}
    """
    _check_initialized()
    return _default_workflow.parser.service.getWordInfo(geolod_id)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.service.Service" directly.')
def searchWord(key):
    """
    指定した表記または読みを持つ語の情報を返します。
    一致する語が辞書に存在しない場合は None を返します。
    *deprecated* この関数は低水準 API なので、廃止予定です。

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
    {'Bn4q6d': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'LrGGxY', 'geolod_id': 'Bn4q6d', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02'}, 'cE8W4w': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': '4NFELa', 'geolod_id': 'cE8W4w', 'hypernym': ['東京地下鉄', '9号線千代田線'], 'institution_type': '民営鉄道', 'latitude': '35.673543333333335', 'longitude': '139.74305333333334', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02'}}
    """
    _check_initialized()
    return _default_workflow.parser.service.searchWord(key)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.service.Service" directly.')
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
    >>> api.getDictionary('geonlp:ksj-station-N02')
    {"@context": "https://schema.org/", "@type": "Dataset", "alternateName": "", "creator": [{"@type": "Organization", "name": "株式会社情報試作室", "sameAs": "https://www.info-proto.com/"}], "dateModified": "2021-08-27T17:18:18+09:00", "description": "国土数値情報「鉄道データ（N02）」から作成した、日本の鉄道駅（地下鉄を含む）の辞書です。hypernym には運営者名と路線名を記載しています。「都営」ではなく「東京都」のようになっていますので注意してください。自由フィールドとして、railway_classに「鉄道区分」、institution_typeに「事業者種別」を含みます。", "distribution": [{"@type": "DataDownload", "contentUrl": "https://www.info-proto.com/static/ksj-station-N02.csv", "encodingFormat": "text/csv"}], "identifier": ["geonlp:ksj-station-N02"], "isBasedOn": {"@type": "CreativeWork", "name": "国土数値情報 鉄道データ", "url": "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_2.html"}, "keywords": ["GeoNLP", "地名辞書"], "license": "https://creativecommons.org/licenses/by/4.0/", "name": "国土数値情報 鉄道データ（駅）", "size": "10191", "spatialCoverage": {"@type": "Place", "geo": {"@type": "GeoShape", "box": "26.193265 127.652285 45.41616333333333 145.59723"}}, "temporalCoverage": "../..", "url": "https://www.info-proto.com/static/ksj-station-N02.html"}
    """
    _check_initialized()
    return _default_manager.getDictionary(id_or_identifier)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.dict_manager.DictManager" directly.')
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
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02']
    """
    _check_initialized()
    return _default_manager.getDictionaries()


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.dict_manager.DictManager" directly.')
def clearDatabase():
    """
    地名語データベースに登録されている辞書をクリアします。
    データベース内の地名語も全て削除されます。

    この関数は、データベースを作り直す際に利用します。
    """
    _check_initialized()
    _default_manager.clearDatabase()


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.dict_manager.DictManager" directly.')
def addDictionaryFromFile(jsonfile, csvfile):
    """
    指定したパスにある辞書メタデータ（JSONファイル）と
    地名解析辞書（CSVファイル）をデータベースに登録します。

    既に同じ identifier を持つ辞書データがデータベースに登録されている場合、
    削除してから新しい辞書データを登録します。

    登録した辞書を利用可能にするには、 ``setActivateDictionaries()``
    または ``activateDictionaires()`` で有効化する必要があります。

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
    """
    _check_initialized()
    return _default_manager.addDictionaryFromFile(jsonfile, csvfile)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.dict_manager.DictManager" directly.')
def addDictionaryFromWeb(url, params=None, **kwargs):
    """
    指定した URL にあるページに含まれる辞書メタデータ（JSON-LD）を取得し、
    メタデータに記載されている URL から地名解析辞書（CSVファイル）を取得し、
    データベースに登録します。

    既に同じ identifier を持つ辞書データがデータベースに登録されている場合、
    削除してから新しい辞書データを登録します。

    登録した辞書を利用可能にするには、 ``setActivateDictionaries()``
    または ``activateDictionaires()`` で有効化する必要があります。

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
    """
    _check_initialized()
    return _default_manager.addDictionaryFromWeb(url, params, **kwargs)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.dict_manager.DictManager" directly.')
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
    return _default_manager.saveDictionaryFromWeb(jsonfile, csvfile, url,
                                                  params, **kwargs)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.dict_manager.DictManager" directly.')
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
    """
    _check_initialized()
    return _default_manager.removeDictionary(identifier)


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.dict_manager.DictManager" directly.')
def updateIndex():
    """
    辞書のインデックスを更新して検索可能にします。
    """
    _check_initialized()
    _default_manager.updateIndex()


@deprecated(
    version='1.2.0',
    reason='This is a low level API. Call class methods of "pygeonlp.api.dict_manager.DictManager" directly.')
def setup_basic_database(db_dir=None, src_dir=None):
    """
    基本的な地名解析辞書を登録したデータベースを作成します。

    Parameters
    ----------
    db_dir: PathLike, optional
        データベースディレクトリを指定します。ここにデータベースファイルを作成します。
        既にデータベースが存在する場合は追記します（つまり、既に登録済みの地名解析辞書の
        データは失われません）。

        省略された場合には ``get_db_dir()`` で決定します。
    src_dir: PathLike, optional
        地名解析辞書ファイルが配置されているディレクトリを指定します。
        省略された場合には、 ``sys.prefix`` または ``site.USER_BASE`` の下に
        ``pygeonlp_basedata`` がないか探します。
        見つからない場合は ``RuntimeError`` を送出しますので、
        ディレクトリを指定してください。
    """
    manager = DictManager(db_dir=db_dir)
    manager.setupBasicDatabase(src_dir=src_dir)
    del manager


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
    [[{"surface": "今日", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "今日", "pos": "名詞", "prononciation": "キョー", "subclass1": "副詞可能", "subclass2": "*", "subclass3": "*", "surface": "今日", "yomi": "キョウ"}, "geometry": null, "prop": null}], [{"surface": "は", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "は", "pos": "助詞", "prononciation": "ワ", "subclass1": "係助詞", "subclass2": "*", "subclass3": "*", "surface": "は", "yomi": "ハ"}, "geometry": null, "prop": null}], [{"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "Bn4q6d:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geometry": {"type": "Point", "coordinates": [139.74534166666666, 35.674845]}, "prop": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "LrGGxY", "geolod_id": "Bn4q6d", "hypernym": ["東京地下鉄", "4号線丸ノ内線"], "institution_type": "民営鉄道", "latitude": "35.674845", "longitude": "139.74534166666666", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02"}}, {"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "cE8W4w:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geometry": {"type": "Point", "coordinates": [139.74305333333334, 35.673543333333335]}, "prop": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "4NFELa", "geolod_id": "cE8W4w", "hypernym": ["東京地下鉄", "9号線千代田線"], "institution_type": "民営鉄道", "latitude": "35.673543333333335", "longitude": "139.74305333333334", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02"}}], [{"surface": "まで", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "まで", "pos": "助詞", "prononciation": "マデ", "subclass1": "副助詞", "subclass2": "*", "subclass3": "*", "surface": "まで", "yomi": "マデ"}, "geometry": null, "prop": null}], [{"surface": "歩き", "node_type": "NORMAL", "morphemes": {"conjugated_form": "五段・カ行イ音便", "conjugation_type": "連用形", "original_form": "歩く", "pos": "動詞", "prononciation": "アルキ", "subclass1": "自立", "subclass2": "*", "subclass3": "*", "surface": "歩き", "yomi": "アルキ"}, "geometry": null, "prop": null}], [{"surface": "まし", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・マス", "conjugation_type": "連用形", "original_form": "ます", "pos": "助動詞", "prononciation": "マシ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "まし", "yomi": "マシ"}, "geometry": null, "prop": null}], [{"surface": "た", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・タ", "conjugation_type": "基本形", "original_form": "た", "pos": "助動詞", "prononciation": "タ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "た", "yomi": "タ"}, "geometry": null, "prop": null}], [{"surface": "。", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "。", "pos": "記号", "prononciation": "。", "subclass1": "句点", "subclass2": "*", "subclass3": "*", "surface": "。", "yomi": "。"}, "geometry": null, "prop": null}]]

    Note
    ----
    ラティス表現では全ての地名語の候補を列挙して返します。
    """
    _check_initialized()
    return _default_workflow.parser.analyze(sentence, **kwargs)


def geoparse(sentence):
    """
    Default Workflow を利用して文を解析した結果を、
    GeoJSON Feature 形式に変換可能な dict のリストとして返します。

    Parameters
    ----------
    sentence : str
        解析する文字列。

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
    '{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": null, "properties": {"surface": "今日", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "今日", "pos": "名詞", "prononciation": "キョー", "subclass1": "副詞可能", "subclass2": "*", "subclass3": "*", "surface": "今日", "yomi": "キョウ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "は", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "は", "pos": "助詞", "prononciation": "ワ", "subclass1": "係助詞", "subclass2": "*", "subclass3": "*", "surface": "は", "yomi": "ハ"}}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [139.74305333333334, 35.673543333333335]}, "properties": {"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "cE8W4w:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geoword_properties": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "4NFELa", "geolod_id": "cE8W4w", "hypernym": ["東京地下鉄", "9号線千代田線"], "institution_type": "民営鉄道", "latitude": "35.673543333333335", "longitude": "139.74305333333334", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "まで", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "まで", "pos": "助詞", "prononciation": "マデ", "subclass1": "副助詞", "subclass2": "*", "subclass3": "*", "surface": "まで", "yomi": "マデ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "歩き", "node_type": "NORMAL", "morphemes": {"conjugated_form": "五段・カ行イ音便", "conjugation_type": "連用形", "original_form": "歩く", "pos": "動詞", "prononciation": "アルキ", "subclass1": "自立", "subclass2": "*", "subclass3": "*", "surface": "歩き", "yomi": "アルキ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "まし", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・マス", "conjugation_type": "連用形", "original_form": "ます", "pos": "助動詞", "prononciation": "マシ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "まし", "yomi": "マシ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "た", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・タ", "conjugation_type": "基本形", "original_form": "た", "pos": "助動詞", "prononciation": "タ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "た", "yomi": "タ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "。", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "。", "pos": "記号", "prononciation": "。", "subclass1": "句点", "subclass2": "*", "subclass3": "*", "surface": "。", "yomi": "。"}}}]}'

    Note
    ----
    このメソッドは、文字列の解析、フィルタによる絞り込み、
    ランキングなどの一連の処理を行ないます。
    """
    _check_initialized()
    return _default_workflow.geoparse(sentence)


def default_workflow():
    """
    Default Workflow オブジェクトを返します。

    通常はこのメソッドを利用する必要はありません。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> type(api.default_workflow())
    <class 'pygeonlp.api.workflow.Workflow'>
    """
    return _default_workflow


def _check_initialized():
    """
    Default Workflow オブジェクトが ``init()`` で初期化されていることを確認するための
    プライベートメソッドです。

    この関数は API メソッド内でチェックのために呼びだすものなので、
    ユーザが呼びだす必要は基本的にありません。

    Raises
    ------
    ServiceError
        init() を呼ぶ前に API メソッドを利用しようとすると発生します。
    """
    if _default_workflow is None:
        raise WorkflowError("APIが初期化されていません。")


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
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02']
    """
    _check_initialized()
    return _default_workflow.getActiveDictionaries()


def setActiveDictionaries(idlist=None, pattern=None):
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
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.setActiveDictionaries(pattern=r'geonlp:geoshape')
    >>> sorted([x.get_identifier() for x in api.getActiveDictionaries()])
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref']

    Note
    ----
    idlist と pattern のどちらかは指定する必要があります。
    """
    _check_initialized()
    return _default_workflow.setActiveDictionaries(idlist, pattern)


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

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> sorted(api.disactivateDictionaries(pattern=r'geonlp:geoshape'))
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref']
    >>> [x.get_identifier() for x in api.getActiveDictionaries()]
    ['geonlp:ksj-station-N02']
    >>> api.disactivateDictionaries(pattern=r'ksj-station')
    ['geonlp:ksj-station-N02']
    >>> [x.get_identifier() for x in api.getActiveDictionaries()]
    []

    Note
    ----
    idlist と pattern を同時に指定した場合、どちらか一方の条件に
    一致する辞書は除外されます。
    """
    _check_initialized()
    return _default_workflow.disactivateDictionaries(idlist, pattern)


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
    >>> sorted(api.disactivateDictionaries(pattern=r'.*'))
    ['geonlp:geoshape-city', 'geonlp:geoshape-pref', 'geonlp:ksj-station-N02']
    >>> sorted([x.get_identifier() for x in api.getActiveDictionaries()])
    []
    >>> api.activateDictionaries(pattern=r'ksj-station')
    ['geonlp:ksj-station-N02']
    >>> sorted([x.get_identifier() for x in api.getActiveDictionaries()])
    ['geonlp:ksj-station-N02']

    Note
    ----
    idlist と pattern を同時に指定した場合、どちらか一方の条件に
    一致する辞書は利用可能になります。
    """
    _check_initialized()
    return _default_workflow.activateDictionaries(idlist, pattern)


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
    return _default_workflow.getActiveClasses()


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

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> api.init()
    >>> api.getActiveClasses()
    ['.*']
    >>> api.searchWord('東京都')
    {'QknGsa': {...'dictionary_identifier': 'geonlp:geoshape-pref'}}
    >>> api.setActiveClasses(['.*', '-都道府県'])
    >>> api.searchWord('東京都')
    {}
    >>> api.setActiveClasses()
    >>> api.getActiveClasses()
    ['.*']
    """
    _check_initialized()
    return _default_workflow.setActiveClasses(patterns)
