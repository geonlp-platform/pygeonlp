from io import StringIO
import json

import chardet
from lxml import etree
import requests


class MetadataError(RuntimeError):
    """
    メタデータの操作の際に例外が起こると、このクラスが発生します。
    """
    pass


class Metadata(object):
    """
    JSON-LD 形式メタデータの管理クラス。

    Attributes
    ----------
    jsonld : str
        メタデータ json-ld 文字列。
    """

    def __init__(self, jsonld=None):
        """
        Parameters
        ----------
        jsonld : str or dict
            json-ld 文字列、またはデコードした dict。
        """
        if isinstance(jsonld, dict):
            jsonld = json.dumps(jsonld, ensure_ascii=False)

        self.jsonld = jsonld

    def __repr__(self):
        return self.jsonld

    @classmethod
    def download(cls, url, params=None, **kwargs):
        """
        指定した URL からウェブページをダウンロードし、
        ヘッダに記載されている json-ld を辞書メタデータとして抽出します。

        Parameters
        ----------
        url : str
            json-ld を含むウェブページの URL。
        params : dict, optional
            requests.get に渡す params パラメータ。
        **kwargs : キーワードパラメータ, optional
            requests.get に渡す kwargs パラメータ。

        Returns
        -------
        Metadata
            抽出した json-ld 文字列をセットした Metadata インスタンス

        Raises
        ----------
        MetadataError
            ウェブページのダウンロードに失敗した場合。
            ウェブページから json-ld が見つけられない場合。
            ウェブページに複数の json-ld が含まれている場合。
        """
        r = requests.get(url, params, **kwargs)
        if r.status_code != 200:
            raise MetadataError(
                "指定されたページを取得できません。status code={}".format(
                    r.status_code))

        htmldata = r.content
        encoding = chardet.detect(htmldata)
        htmltext = htmldata.decode(encoding['encoding'])

        tree = etree.parse(StringIO(htmltext), etree.HTMLParser())
        p = tree.findall(".//script[@type='application/ld+json']")
        if len(p) == 0:
            raise MetadataError(
                "指定されたページから json-ldを見つけられません。")

        if len(p) > 1:
            raise MetadataError(
                "指定されたページには複数の json-ldが含まれています。")

        jsonld = p[0].text
        return cls(jsonld)

    @classmethod
    def load(cls, file):
        """
        指定したファイルに含まれる json-ld 文字列から
        Metadata インスタンスを作成します。

        Parameters
        ----------
        file : str
            json-ld 文字列を含むファイル名。

        Returns
        -------
        Metadata
            json-ld 文字列をセットした Metadata インスタンス。
        """
        with open(mode='r', file=file, encoding='utf-8') as f:
            jsonld = f.read()

        return cls(jsonld)

    @classmethod
    def loads(cls, jsonld):
        """
        指定した json-ld 文字列から Metadata インスタンスを作成します。

        Parameters
        ----------
        jsonld : str
            json-ld 文字列。

        Returns
        -------
        Metadata
            json-ld 文字列をセットした Metadata インスタンス。
        """
        return cls(jsonld)

    def get_name(self):
        """
        json-ld 文字列からデータセットの名前を抽出します。

        Returns
        -------
        str
            データセットの名前。

        Raises
        ----------
        MetadataError
            json-ld がセットされていない場合。
            json-ld から identifier が見つけられない場合。
        """
        if self.jsonld is None:
            raise MetadataError(
                "json-ld がセットされていません。")

        obj = json.loads(self.jsonld)
        try:
            name = obj['name']
            return name
        except (IndexError, TypeError):
            raise MetadataError(
                ("json-ld から name を見つけられません。"
                 "{}".format(self.jsonld)))

        raise MetadataError(
            ("json-ldから name を見つけられません。"
             "{}".format(self.jsonld)))
        return None

    def get_identifier(self):
        """
        json-ld 文字列から GeoNLP identifier を抽出します。

        GeoNLP identifier は 'geonlp:' で始まる必要があります。

        Returns
        -------
        str
            抽出した identifier 文字列。

        Raises
        ----------
        MetadataError
            json-ld がセットされていない場合。
            json-ld から identifier が見つけられない場合。
        """
        if self.jsonld is None:
            raise MetadataError(
                "json-ld がセットされていません。")

        obj = json.loads(self.jsonld)
        try:
            identifiers = obj['identifier']
            if isinstance(identifiers, str):
                identifiers = [identifiers]

            for identifier in identifiers:
                if identifier.startswith('geonlp:'):
                    return identifier

        except (IndexError, TypeError):
            raise MetadataError(
                ("json-ld から identifier を見つけられません。"
                 "{}".format(self.jsonld)))

        raise MetadataError(
            ("json-ldから identifier を見つけられません。"
             "{}".format(self.jsonld)))
        return None

    def get_content_url(self):
        """
        json-ld 文字列から、コンテンツ CSV をダウンロードする
        content_url を抽出します。



        Returns
        -------
        str
            抽出した content_url 文字列。

        Raises
        ----------
        MetadataError
            json-ld がセットされていない場合。
            json-ld から content_url が見つけられない場合。
        """
        content_url = None
        if self.jsonld is None:
            raise MetadataError(
                "json-ld がセットされていません。")

        obj = json.loads(self.jsonld)
        try:
            for dist in obj['distribution']:
                if '@type' not in dist or dist['@type'] != "DataDownload":
                    continue

                content_url = dist['contentUrl']
        except (IndexError, TypeError):
            raise MetadataError(
                ("json-ld から contentUrl を見つけられません。"
                 "{}".format(self.jsonld)))

        if content_url is None:
            raise MetadataError(
                ("json-ld から contentUrl を見つけられません。"
                    "{}".format(self.jsonld)))

        self.content_url = content_url
        return content_url

    def download_csv(self, content_url=None, params=None, **kwargs):
        """
        content_url から CSV をダウンロードします。

        Parameters
        ----------
        content_url : str, optional
            CSV をダウンロードする URL を指定します。
            省略された場合、 json-ld から content_url を抽出します。
        params : dict, optional
            requests.get に渡す params パラメータ。
        **kwargs : キーワードパラメータ, optional
            requests.get に渡す kwargs パラメータ。

        Returns
        -------
        str
            ダウンロードした CSV テキスト。

        Raises
        ----------
        MetadataError
            CSV のダウンロードに失敗した場合。
        """
        if content_url is None:
            content_url = self.get_content_url()

        r = requests.get(content_url, params, **kwargs)
        if r.status_code != 200:
            raise MetadataError(
                "CSV をダウンロードできません。 url={}".format(content_url))

        csvdata = r.content
        encoding = chardet.detect(csvdata)
        csvtext = csvdata.decode(encoding['encoding'])

        return csvtext
