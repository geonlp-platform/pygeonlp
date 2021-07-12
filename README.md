# pygeonlp, A python module for geotagging Japanese texts

`pygeonlp` is an open source software for geotagging/geoparsing 
Japanese natural language text to extract place names.

## How To Use

Import `pygeonlp.api` and initialize it by specifying the directory
where the place-name database is placed.

```python
>>> import pygeonlp.api as api
>>> api.init(db_dir='mydic')
```

Then, run `geoparse("text to parse")` .

```python
>>> result = api.geoparse("国立情報学研究所は千代田区にあります。")
```

The result is a list of dict objects, with POS/Spatial attributes
assigned to each word.

A [GeoJSON](https://tools.ietf.org/html/rfc7946#section-3.2)
representation is obtained by JSON-encoding each dict object.

```python
>>> import json
>>> print(json.dumps(result, indent=2, ensure_ascii=False))
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

## Pre-requirements

`pygeonlp` requires [MeCab](https://taku910.github.io/mecab/) C++ library and UTF8 dictionary for Japanese morphological analysis.

Also, the C++ implementation part depends on [Boost C++](https://www.boost.org/).

```sh
$ sudo apt install libmecab-dev mecab-ipadic-utf8 libboost-all-dev
```

## Install

The pygeonlp package can be installed with the `pip` command.
It is recommended that you upgrade pip and setuptools to
the latest versions before running it.

```sh
$ pip install --upgrade pip setuptools
$ pip install pygeonlp
```

The database needs to be prepared the first time.

**Prepare the database**

Execute the command to register the basic place name word analysis dictionaries
(`*.json`, `*.csv`) in this package into the database under `mydic/`.

```
>>> import pygeonlp.api as api
>>> api.setup_basic_database(db_dir='mydic/')
```

This command registers three dictionaries:

- "Prefectures of Japan" (`geonlp:geoshape-pref`),

- "Historical Administrative Area Data Set Beta Dictionary of Place Names" (`geonlp:geoshape-city`)

- "Railroad Stations in Japan (2019)" (`geonlp:ksj-station-N02-2019`)


### Install GDAL library (Optional)

If the [GDAL](https://pypi.org/project/GDAL/) library is installed,
`pygeonlp` can use "spatial distance" for disambiguation
when there are multiple place names with the same name, thus improving accuracy.
You can also use spatial filters.

```sh
$ sudo apt install libgdal-dev
$ pip install gdal
```

### Install jageocoder (Optional)

`pygeonlp` can use address-geocoding if
the [jageocoder](https://pypi.org/project/jageocoder/) is installed.

See the jageocoder documentation for installation instructions.

### Run tests (Optional)

Run the unit tests with `python setup.py test` command.


## Uninstall

Use `pip` command to uninstall.

```sh
$ pip uninstall pygeonlp
```

## Delete the database

When you register a place-name word analysis dictionary to the database,
it will create a sqlite3 database and some other files in the specified directory.

If you want to delete them, just delete the whole directory.

```sh
$ rm -r mydic/
```

## License

[The 2-Clause BSD License](https://licenses.opensource.jp/BSD-2-Clause/BSD-2-Clause.html)

## Acknowledgements

This software is supported by DIAS (Data Integration and Analysis System) and
ROIS-DS CODH (Center for Open Data in the Humanities).

It was also supported by JST (Japan Science and Technology Agency) PRESTO program.
