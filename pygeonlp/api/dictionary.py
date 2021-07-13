import chardet
import os
import tempfile

from pygeonlp.api.metadata import Metadata


class DictionaryError(RuntimeError):
    """
    辞書データの操作の際に例外が起こると、このクラスが発生します。
    """
    pass


class Dictionary(object):
    """
    GeoNLP 辞書の管理クラス
    辞書メタデータとCSVデータに対する操作を行ないます。

    通常、開発者がこのクラスを直接操作する必要はありません。

    Attributes
    ----------
    metadata : Metadata
        メタデータのインスタンス
    csvtext : str
        CSV テキスト
    """

    def __init__(self, metadata, csvtext):
        """
        与えられたパラメータでクラス変数を初期化します。

        Parameters
        ----------
        metadata : Metadata
            メタデータのインスタンス
        csvtext : str
            CSV テキスト
        """
        self.metadata = metadata
        self.csvtext = csvtext

    @classmethod
    def download(cls, url, params=None, **kwargs):
        """
        指定された URL からウェブページをダウンロードし、
        ヘッダに記載されている json-ld を辞書メタデータとして抽出します。
        また、メタデータに書かれているデータダウンロード URL にアクセスして CSV データを取得します。
        取得したメタデータと CSV データを保持する Dictionary インスタンスを作成します。

        Parameters
        ----------
        url : str
            json-ld を含むウェブページの URL
        params : dict, optional
            requests.get に渡す params パラメータ
        **kwargs
            requests.get に渡す kwargs パラメータ

        Returns
        -------
        Dictionary
            作成した Dictionary インスタンス。
        """
        metadata = Metadata.download(url, params, **kwargs)
        csvtext = metadata.download_csv(params=params, **kwargs)

        return cls(metadata, csvtext)

    @classmethod
    def load(cls, jsonfile, csvfile):
        """
        指定したパスにある辞書メタデータ（JSONファイル）と
        地名解析辞書（CSVファイル）を読み込み Dictionary インスタンスを作成します。

        Parameters
        ----------
        jsonfile : str
            辞書メタデータファイルのパス
        csvfile : str
            地名解析辞書ファイルのパス

        Returns
        -------
        Dictionary
            作成した Dictionary インスタンス。
        """
        if not isinstance(jsonfile, str) or not isinstance(csvfile, str):
            raise TypeError("jsonfile と csvfile は str で指定してください。")

        if not os.path.exists(jsonfile):
            raise FileNotFoundError(f"jsonfile({jsonfile}) が見つかりません。")

        if not os.path.exists(csvfile):
            raise FileNotFoundError(f"csvfile({csvfile}) が見つかりません。")

        with open(jsonfile, 'r', encoding='utf-8') as f:
            jsonld = f.read()

        with open(csvfile, 'rb') as f:
            csvdata = f.read()
            encoding = chardet.detect(csvdata)
            csvtext = csvdata.decode(encoding['encoding'])

        metadata = Metadata.loads(jsonld)

        return cls(metadata, csvtext)

    def get_identifier(self):
        """
        この辞書の identifier を返します。

        Returns
        -------
        str
            辞書 identifier 文字列。
        """
        if self.metadata is None:
            raise DictionaryError("metadata がセットされていません。")

        return self.metadata.get_identifier()

    def get_name(self):
        """
        この辞書の名前を返します。

        Returns
        -------
        str
            辞書の名前。
        """
        if self.metadata is None:
            raise DictionaryError("metadata がセットされていません。")

        return self.metadata.get_name()

    def save(self, jsonfile, csvfile):
        """
        この辞書が保持している json-ld と CSV データをファイルに保存します。

        Parameters
        ----------
        jsonfile : str
            json-ld を保存するファイル名
        csvfile : str
            CSV データを保存するファイル名

        Returns
        -------
        bool
            常に True が返ります。
            失敗した場合は例外が発生します。
        """
        if self.metadata is None:
            raise DictionaryError("metadata がセットされていません。")

        if self.csvtext is None:
            raise DictionaryError("csvtext がセットされていません。")

        with open(jsonfile, 'w', encoding='utf-8') as fp:
            fp.write(self.metadata.jsonld)

        with open(csvfile, 'w', encoding='utf-8', newline="\r\n") as fp:
            fp.write(self.csvtext)

        return True

    def add(self, capi_ma):
        """
        システムに辞書を登録します。

        Parameters
        ----------
        capi_ma : ``capi.MA``
            辞書を管理する MA オブジェクト。
            init() で初期化済みである必要があります。

        Returns
        -------
        bool
            常に True が返ります。
            失敗した場合は例外が発生します。
        """
        if self.metadata is None:
            raise DictionaryError("metadata がセットされていません。")

        if self.csvtext is None:
            raise DictionaryError("csvtext がセットされていません。")

        fp_json, fn_json = tempfile.mkstemp()
        with open(fn_json, 'w', encoding='utf-8') as fp:
            fp.write(self.metadata.jsonld)

        fp_csv, fn_csv = tempfile.mkstemp()
        with open(fn_csv, 'w', encoding='utf-8', newline="\r\n") as fp:
            fp.write(self.csvtext)

        ret = capi_ma.addDictionary(fn_json, fn_csv)
        os.remove(fn_json)
        os.remove(fn_csv)

        return ret
