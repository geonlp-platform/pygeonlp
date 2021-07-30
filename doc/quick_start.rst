Quickstart
================

ここでは pygeonlp の簡単な使い方を紹介します。
まだ pygeonlp をインストールしていない場合は、
:ref:`install_pygeonlp` に従ってインストールしてください。

最小限のサンプル
----------------

pygeonlp を使って自然文テキストから地名を抽出する最小コードは
次のようになります。

.. code-block:: python3

  import pygeonlp.api
  pygeonlp.api.init()
  print(pygeonlp.api.geoparse("NIIは神保町駅から徒歩7分です。"))

このコードは次の処理を行ないます。

1. `pygeonlp.api パッケージ <pygeonlp.api.html>`_ を読み込みます。
2. `init() <pygeonlp.api.html#pygeonlp.api.init>`_ を呼んで API が利用可能な状態に初期化します。
3. `geoparse() <pygeonlp.api.html#pygeonlp.api.geoparse>`_ メソッドを呼んで、テキストを解析します。

実行結果
--------

上のコードを実行すると、次のような結果が表示されます。

.. code-block:: python3

  [{'type': 'Feature', 'geometry': None, 'properties': {'surface': 'NII', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '組織', 'subclass3': '*', 'surface': 'NII', 'yomi': ''}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'は', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}}}, {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.757845, 35.6960275]}, 'properties': {'surface': '神保町駅', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '神保町駅', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': '82wiE0:神保町駅', 'surface': '神保町駅', 'yomi': ''}, 'geoword_properties': {'body': '神保町', 'dictionary_id': 3, 'entry_id': '2891e10e9314a0b378fac6aace6d2a7f', 'geolod_id': '82wiE0', 'hypernym': ['東京都', '10号線新宿線'], 'institution_type': '公営鉄道', 'latitude': '35.6960275', 'longitude': '139.757845', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'から', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'から', 'pos': '助詞', 'prononciation': 'カラ', 'subclass1': '格助詞', 'subclass2': '一般', 'subclass3': '*', 'surface': 'から', 'yomi': 'カラ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '徒歩', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '徒歩', 'pos': '名詞', 'prononciation': 'トホ', 'subclass1': '一般', 'subclass2': '*', 'subclass3': '*', 'surface': '徒歩', 'yomi': 'トホ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '7', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '数', 'subclass2': '*', 'subclass3': '*', 'surface': '7', 'yomi': ''}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '分', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '分', 'pos': '名詞', 'prononciation': 'フン', 'subclass1': '接尾', 'subclass2': '助数詞', 'subclass3': '*', 'surface': '分', 'yomi': 'フン'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'です', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '特殊・デス', 'conjugation_type': '基本形', 'original_form': 'です', 'pos': '助動詞', 'prononciation': 'デス', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'です', 'yomi': 'デス'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '。', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}}}]

このままでは見にくいので、 JSON で整形表示するように少し修正します。

.. code-block:: python3

  import json
  import pygeonlp.api
  pygeonlp.api.init()
  parsed = pygeonlp.api.geoparse("NIIは神保町駅から徒歩7分です。")
  print(json.dumps(parsed, indent=2, ensure_ascii=False))

実行結果は次のようになります。テキストが単語に分割され、
それぞれの単語の品詞情報などが付与されているのが分かると思います。

.. code-block:: javascript

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
          "subclass3": "82wiE0:神保町駅",
          "surface": "神保町駅",
          "yomi": ""
        },
        "geoword_properties": {
          "body": "神保町",
          "dictionary_id": 3,
          "entry_id": "2891e10e9314a0b378fac6aace6d2a7f",
          "geolod_id": "82wiE0",
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
          "dictionary_identifier": "geonlp:ksj-station-N02-2019"
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

地名語ノード
------------

テキストを単語に分割するのは形態素解析器、または POS Tagger と呼ばれる
ツールに共通の機能です。 pygeonlp は、分割した単語
（またはその組み合わせ）から
地名解析辞書に登録されている地名語を見つけ、経緯度などを付け加える機能を
持っている点が特徴です。

解析結果のうち、 node_type が GEOWORD となっている部分が地名語です。

.. code-block:: javascript

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
        "subclass3": "82wiE0:神保町駅",
        "surface": "神保町駅",
        "yomi": ""
      },
      "geoword_properties": {
        "body": "神保町",
        "dictionary_id": 3,
        "entry_id": "2891e10e9314a0b378fac6aace6d2a7f",
        "geolod_id": "82wiE0",
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
        "dictionary_identifier": "geonlp:ksj-station-N02-2019"
      }
    }
  }

この地名語部分は `GeoJSON <https://geojson.org/>`_ の Feature 形式に
なっていますので、この出力結果をテキストファイルに保存して
GIS アプリケーションで開けば、地図上にプロットすることができます。

簡単にテストしたければ `GeoJSONLint <https://geojsonlint.com/>`_ に
コピーした GeoJSON を貼り付ければ、神保町駅にマーカーが
プロットされることを確認できます。

より高度な使い方
----------------

基本的な pygeonlp の使い方は以上です。

より進んだ使い方を知りたい方は、関連する説明へお進みください。

- `NEologd <https://github.com/neologd/mecab-ipadic-neologd/>`_
  と連携して固有表現の抽出精度を上げたい

  - :ref:`link_neologd` へ

- 抽出したい地名が辞書に載っていないので、独自の地名解析辞書を作りたい

  - :ref:`dic_developers_index` へ

- 住所文字列を住所として解析したい

  - :ref:`link_jageocoder` へ

- 別の場所にある同じ名前の地名が抽出されてしまうのでチューニングしたい

  - :ref:`tune_analysis` へ
