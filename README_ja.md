# pygeonlp, A python module for geotagging Japanese texts

`pygeonlp` は、自然言語テキストを解析して地名を抽出する
ジオタギング (geo-tagging) またはジオパージング (geo-parsing) と呼ばれる処理を行なうオープンソースソフトウェアです。

## 使い方

`pygeonlp.api` をインポートし、地名語解析辞書を登録したデータベースが
置かれているディレクトリを指定して初期化します。

```python
import pygeonlp.api as geonlp_api
geonlp_api.init(dict_dir='mydic')
```

`geoparse("解析したい文章")` を実行します。

```python
result = geonlp_api.geoparse("国立情報学研究所は千代田区にあります。")
```

結果は単語ごとに品詞や空間属性を付与した dict オブジェクトのリストです。
各 dict オブジェクトを JSON エンコードすると [GeoJSON Feature Object](https://tools.ietf.org/html/rfc7946#section-3.2) を得られます。

```python
print(json.dumps(result, indent=2, ensure_ascii=False))
[
  {
    "type": "Feature",
    "geometry": null,
    "properties": {
      "surface": "国立",
      "node_type": "NORMAL",
      "morphemes": {
        "conjugated_form": "名詞-固有名詞-地名語",
        "conjugation_type": "*",
        "original_form": "国立",
        "pos": "名詞",
        "prononciation": "コクリツ",
        "subclass1": "固有名詞",
        "subclass2": "地名修飾語",
        "subclass3": "*",
        "surface": "国立",
        "yomi": "コクリツ"
      }
    }
  }, ... 
  {
    "type": "Feature",
    "geometry": {
      "type": "Point",
      "coordinates": [
        139.753634,
        35.694003
      ]
    },
    "properties": {
      "surface": "千代田区",
      "node_type": "GEOWORD",
      "morphemes": {
        "conjugated_form": "*",
        "conjugation_type": "*",
        "original_form": "千代田区",
        "pos": "名詞",
        "prononciation": "",
        "subclass1": "固有名詞",
        "subclass2": "地名語",
        "subclass3": "WWIY7G:千代田区",
        "surface": "千代田区",
        "yomi": ""
      },
      "geoword_properties": {
        "address": "東京都千代田区",
        "body": "千代田",
        "body_variants": "千代田",
        "code": {},
        "countyname": "",
        "countyname_variants": "",
        "dictionary_id": 1,
        "entry_id": "13101A1968",
        "geolod_id": "WWIY7G",
        "hypernym": [
          "東京都"
        ],
        "latitude": "35.69400300",
        "longitude": "139.75363400",
        "ne_class": "市区町村",
        "prefname": "東京都",
        "prefname_variants": "東京都",
        "source": "1/千代田区役所/千代田区九段南1-2-1/P34-14_13.xml",
        "suffix": [
          "区"
        ],
        "valid_from": "",
        "valid_to": "",
        "dictionary_identifier": "geonlp:geoshape-city"
      }
    }
  },
  {
    "type": "Feature",
    "geometry": null,
    "properties": {
      "surface": "に",
      "node_type": "NORMAL",
      "morphemes": {
        "conjugated_form": "*",
        "conjugation_type": "*",
        "original_form": "に",
        "pos": "助詞",
        "prononciation": "ニ",
        "subclass1": "格助詞",
        "subclass2": "一般",
        "subclass3": "*",
        "surface": "に",
        "yomi": "ニ"
      }
    }
  },...
]
```

## 事前に必要なもの

`pygeonlp` は日本語形態素解析に [MeCab](https://taku910.github.io/mecab/)
C++ ライブラリと UTF8 の辞書を必要とします。
また、 C++ 実装部分が [Boost C++](https://www.boost.org/) に依存します。

```sh
$ sudo apt install libmecab-dev mecab-ipadic-utf8 libboost-all-dev
```

## pygeonlp のインストール

pygeonlp パッケージは `pip` コマンドでインストールできます。
先に pip と setuptools を最新バージョンにアップグレードしてから実行することをお勧めします。

```sh
$ pip install --upgrade pip setuptools
$ pip install pygeonlp
```

##### GDAL のインストール（オプション）

pygeonlp は [GDAL](https://pypi.org/project/GDAL/) がインストールされている場合、
同じ名前の地名語が複数存在する場合の曖昧性解決に「空間的な距離」を利用することができ、
精度が向上します。また、空間フィルタを利用することができます。

```sh
$ sudo apt install libgdal-dev
$ pip install gdal
```

##### jageocoder のインストール（オプション）

pygeonlp は [jageocoder](https://pypi.org/project/jageocoder/) がインストールされている場合、住所ジオコーディングを利用することができます。

```sh
$ pip install jageocoder
$ mkdir db/
$ wget https://www.info-proto.com/static/jusho.zip
$ unzip jusho.zip -d db/
$ python
>>> import jageocoder
>>> jageocoder.init(dsn='sqlite:///db/address.db', trie_path='db/address.trie')
>>> jageocoder.create_trie_index()
```

## pygeonlp のアンインストール

`pip` コマンドでアンインストールできます。

```sh
$ pip uninstall pygeonlp
```

## 地名語解析辞書の登録

`base_data/` に含まれている基本的な地名語解析辞書（`*.json`, `*.csv`）を
`mydic/` の下のデータベースに登録するスクリプトを実行します。

```sh
$ python scripts/setup_dictionaries.py
```

このスクリプトで登録される辞書は 「日本の都道府県」 (`geonlp:geoshape-pref`)、 「歴史的行政区域データセットβ版地名辞書」 (`geonlp:geoshape-city`)、
「日本の鉄道駅（2019年）」 (`geonlp:ksj-station-N02-2019`) の3種類です。

## 地名語解析辞書の削除

地名語解析辞書をデータベースに登録すると、
指定したディレクトリに sqlite3 データベースの他いくつかのファイルを作成します。
削除したい場合はディレクトリごと消去してください。

```sh
$ rm -r mydic/
```

## ライセンス

[2条項 BSD ライセンス](https://licenses.opensource.jp/BSD-2-Clause/BSD-2-Clause.html)

## 謝辞

本ソフトウェアの一部には、独立行政法人科学技術振興機構の戦略的創造研究推進事業「さきがけ」の支援を受けた。

本ソフトウェアの一部には、大学共同利用機関法人情報・システム研究機構の支援を受けた。

This software is partially supported by PRESTO program of Japan Science and Technology Agency (JST).

This software is partially supported by Research Organization of Information and Systems (ROIS).