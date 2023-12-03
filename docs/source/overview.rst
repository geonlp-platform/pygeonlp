.. _overview:

概要
====

PyGeoNLP は Python 用のライブラリとして実装されています。
地名抽出機能が必要なアプリケーションやサービスに組み込んで
使うことができます。

.. code-block:: python
    :linenos:
    :caption: 実行例

    >>> import pygeonlp.api
    >>> import json
    >>> pygeonlp.api.init()
    >>> print(json.dumps(pygeonlp.api.geoparse("NIIは神保町駅から徒歩7分です。"), indent=2, ensure_ascii=False))
    [
    {
        "type": "Feature",
        "geometry": null,
        "properties": {
        "surface": "NII",
        "node_type": "NORMAL",
        "morphemes": {
            "conjugated_form": "*",
            "conjugation_type": "*",
            "original_form": "*",
            "pos": "名詞",
            "prononciation": "",
            "subclass1": "固有名詞",
            "subclass2": "組織",
            "subclass3": "*",
            "surface": "NII",
            "yomi": ""
        }
        }
    },
    {
        "type": "Feature",
        "geometry": null,
        "properties": {
        "surface": "は",
        "node_type": "NORMAL",
        "morphemes": {
            "conjugated_form": "*",
            "conjugation_type": "*",
            "original_form": "は",
            "pos": "助詞",
            "prononciation": "ワ",
            "subclass1": "係助詞",
            "subclass2": "*",
            "subclass3": "*",
            "surface": "は",
            "yomi": "ハ"
        }
        }
    },
    {
        "type": "Feature",
        "geometry": {
        "type": "Point",
        "coordinates": [
            139.757845,
            35.6960275
        ]
        },
        "properties": {
        "surface": "神保町駅",
        "node_type": "GEOWORD",
        "morphemes": {
            "conjugated_form": "*",
            "conjugation_type": "*",
            "original_form": "神保町駅",
            "pos": "名詞",
            "prononciation": "",
            "subclass1": "固有名詞",
            "subclass2": "地名語",
            "subclass3": "uN6ecI:神保町駅",
            "surface": "神保町駅",
            "yomi": ""
        },
        "geoword_properties": {
            "body": "神保町",
            "dictionary_id": 3,
            "entry_id": "5WS6qh",
            "geolod_id": "uN6ecI",
            "hypernym": [
            "東京都",
            "10号線新宿線"
            ],
            "institution_type": "公営鉄道",
            "latitude": "35.6960275",
            "longitude": "139.757845",
            "ne_class": "鉄道施設/鉄道駅",
            "railway_class": "普通鉄道",
            "suffix": [
            "駅",
            ""
            ],
            "dictionary_identifier": "geonlp:ksj-station-N02"
        }
        }
    },
    {
        "type": "Feature",
        "geometry": null,
        "properties": {
        "surface": "から",
        "node_type": "NORMAL",
        "morphemes": {
            "conjugated_form": "*",
            "conjugation_type": "*",
            "original_form": "から",
            "pos": "助詞",
            "prononciation": "カラ",
            "subclass1": "格助詞",
            "subclass2": "一般",
            "subclass3": "*",
            "surface": "から",
            "yomi": "カラ"
        }
        }
    },
    {
        "type": "Feature",
        "geometry": null,
        "properties": {
        "surface": "徒歩",
        "node_type": "NORMAL",
        "morphemes": {
            "conjugated_form": "*",
            "conjugation_type": "*",
            "original_form": "徒歩",
            "pos": "名詞",
            "prononciation": "トホ",
            "subclass1": "一般",
            "subclass2": "*",
            "subclass3": "*",
            "surface": "徒歩",
            "yomi": "トホ"
        }
        }
    },
    {
        "type": "Feature",
        "geometry": null,
        "properties": {
        "surface": "7",
        "node_type": "NORMAL",
        "morphemes": {
            "conjugated_form": "*",
            "conjugation_type": "*",
            "original_form": "*",
            "pos": "名詞",
            "prononciation": "",
            "subclass1": "数",
            "subclass2": "*",
            "subclass3": "*",
            "surface": "7",
            "yomi": ""
        }
        }
    },
    {
        "type": "Feature",
        "geometry": null,
        "properties": {
        "surface": "分",
        "node_type": "NORMAL",
        "morphemes": {
            "conjugated_form": "*",
            "conjugation_type": "*",
            "original_form": "分",
            "pos": "名詞",
            "prononciation": "フン",
            "subclass1": "接尾",
            "subclass2": "助数詞",
            "subclass3": "*",
            "surface": "分",
            "yomi": "フン"
        }
        }
    },
    {
        "type": "Feature",
        "geometry": null,
        "properties": {
        "surface": "です",
        "node_type": "NORMAL",
        "morphemes": {
            "conjugated_form": "特殊・デス",
            "conjugation_type": "基本形",
            "original_form": "です",
            "pos": "助動詞",
            "prononciation": "デス",
            "subclass1": "*",
            "subclass2": "*",
            "subclass3": "*",
            "surface": "です",
            "yomi": "デス"
        }
        }
    },
    {
        "type": "Feature",
        "geometry": null,
        "properties": {
        "surface": "。",
        "node_type": "NORMAL",
        "morphemes": {
            "conjugated_form": "*",
            "conjugation_type": "*",
            "original_form": "。",
            "pos": "記号",
            "prononciation": "。",
            "subclass1": "句点",
            "subclass2": "*",
            "subclass3": "*",
            "surface": "。",
            "yomi": "。"
        }
        }
    }
    ]


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
