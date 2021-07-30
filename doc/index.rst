.. _pygeonlp:

PyGeoNLP リファレンス
=====================

PyGeoNLP は、普通の日本語テキスト（自然文）から、地名の部分を抽出する
geotagger や geoparser と呼ばれるツールの一つです。

Python 用のライブラリとして実装されていますので、地名抽出機能が必要な
アプリケーションやサービスに組み込んで使うことができます。 ::

  >>> import pygeonlp.api
  >>> pygeonlp.api.init()
  >>> print(pygeonlp.api.geoparse("NIIは神保町駅から徒歩7分です。"))

特徴
----

PyGeoNLP には以下のような特徴があります。

- ウェブサービスではないので、オフラインでも利用可能です
- 辞書を作って登録すれば独自の地名も抽出できます
- 住所ジオコーダーと連携すれば住所も抽出できます

処理の内容
----------
PyGeoNLP は、まず自然文を MeCab で解析し、単語のリストを作ります。

次に、連続する単語を組み合わせてみて、地名解析辞書に登録されていれば
地名語として抽出します。たとえば「神保町」＋「駅」は地名解析辞書の
「神保町駅」と一致するので、地名語として一語にまとめます。

もし抽出した地名語に綴りが同じものが複数存在する場合には、
フィルタを利用して絞り込んだり、他の地名語との関係を見て
スコアを付けランキングするなどの地名解決処理を行ないます。

最後に、結果を GeoJSON に変換可能なフォーマットに変換して返します。

目次
----

.. toctree::
   :maxdepth: 2

   install.rst
   quick_start.rst
   link_neologd.rst
   link_jageocoder.rst
   tuning.rst
   webapi_doc/index.rst
   terms.rst
   json/index.rst
   pygeonlp.api.rst
