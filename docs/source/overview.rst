.. _overview:

概要
====

PyGeoNLP は自然言語テキストから地名を抽出し、地理的な属性を
割り当てる GeoParser の Python ライブラリです。
コマンドラインから :ref:`cli_geoparse` を呼び出してテキストを解析したり、
地名抽出機能が必要なアプリケーションやサービスに組み込んで
Python API を利用することができます。

.. code-block:: python
    :linenos:
    :caption: Python API 使用例

    >>> import pygeonlp.api
    >>> print(pygeonlp.api.geoparse("NIIは神保町駅から徒歩7分です。"))
    [{'type': 'Feature', 'geometry': None, 'properties': {'surface': 'NII', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '組織', 'subclass3': '*', 'surface': 'NII', 'yomi': ''}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'は', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}}}, {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.757845, 35.6960275]}, 'properties': {'surface': '神保町駅', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '神保町駅', 'pos': '名 詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'uN6ecI:神保町駅', 'surface': '神保町駅', 'yomi': ''}, 'geoword_properties': {'body': '神保町', 'dictionary_id': 3, 'entry_id': '5WS6qh', 'geolod_id': 'uN6ecI', 'hypernym': ['東京都', '10号線新宿線'], 'institution_type': '公営鉄道', 'latitude': '35.6960275', 'longitude': '139.757845', 'ne_class': '鉄道施設/鉄道 駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'から', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'から', 'pos': '助詞', 'prononciation': 'カラ', 'subclass1': '格助詞', 'subclass2': '一般', 'subclass3': '*', 'surface': 'から', 'yomi': 'カラ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '徒歩', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '徒歩', 'pos': '名詞', 'prononciation': 'トホ', 'subclass1': '一般', 'subclass2': '*', 'subclass3': '*', 'surface': '徒歩', 'yomi': 'トホ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '7', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '数', 'subclass2': '*', 'subclass3': '*', 'surface': '7', 'yomi': ''}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '分', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '分', 'pos': '名詞', 'prononciation': 'フン', 'subclass1': '接尾', 'subclass2': '助数詞', 'subclass3': '*', 'surface': '分', 'yomi': 'フ ン'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'です', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '特殊・デス', 'conjugation_type': '基本形', 'original_form': 'です', 'pos': '助動詞', 'prononciation': 'デス', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'です', 'yomi': 'デス'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '。', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': ' 。'}}}]


特徴
----

PyGeoNLP には以下のような特徴があります。

- ウェブサービスではないので、オフラインでも利用可能です
- 辞書を作って登録すれば独自の地名も抽出できます
- 住所ジオコーダーと連携すれば住所も抽出できます

処理の内容
----------
PyGeoNLP は、まず自然文を `MeCab <https://taku910.github.io/mecab/>`_
で解析し、単語のリストを作ります。

次に、連続する単語を組み合わせてみて、 :ref:`pygeonlp_terms_dictionary`
に登録されていれば :ref:`pygeonlp_terms_geoword` として抽出します。
たとえば「神保町」＋「駅」は地名解析辞書の「神保町駅」と一致するので、
地名語として一語にまとめます。

もし抽出した地名語に綴りが同じものが複数存在する場合には、
フィルタを利用して絞り込んだり、他の地名語との関係を見て
スコアを付けランキングするなどの地名解決処理を行ないます。
