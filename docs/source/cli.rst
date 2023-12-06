.. _cli_pygeonlp:

コマンドラインインタフェース
============================

Pygeonlp の機能をコマンドラインから利用する方法を説明します。
Pygeonlp コマンドは ``pygeonlp`` の後ろに実行したい機能を指定し、
さらにパラメータが続きます。

コマンドラインではジオパーズ処理の他、地名解析辞書の管理を行うことができます。


.. _cli_geoparse:

ジオパーズ処理
--------------

対話的に一行ずつテキストを入力し、ジオパーズした結果を出力します。 ::

    $ pygeonlp geoparse
    NIIは神保町にあります。
    NII     名詞,固有名詞,組織,*,*,*,*,,
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    神保町  名詞,固有名詞,地名語,uN6ecI:神保町駅,*,*,神保町,,       鉄道施設/鉄道駅,uN6ecI,神保町駅,139.757845,35.6960275
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS

終了するには ``Ctrl+D`` を押して EOF を送信してください。

ファイルからパイプで接続して実行することもできます。 ::

    $ cat sample.txt | pygeonlp geoparse > result.txt

出力フォーマットは MeCab に似ています。 ::

    行 ::= 表層形 \t 形態素情報 \t 地理的情報
    形態素情報 ::= 品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音
    地理的情報 ::= 固有名クラス,geolod_id,地名語,経度,緯度

表層形と形態素情報は MeCab の標準出力フォーマットと同じです。
地名語または住所を抽出した場合、GeoNLP 固有の属性である地理的情報が付与されます。

``--json`` オプションを指定すると、 Python API と同じ、より詳細な情報を
含む GeoJSON のリスト形式で出力します。 ::

    $ echo "NIIは神保町にあります。" | pygeonlp geoparse --json
    [{"type": "Feature", "geometry": null, "properties": {"surface": "NII", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "*", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "組織", "subclass3": "*", "surface": "NII", "yomi": ""}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "は", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "は", "pos": "助詞", "prononciation": "ワ", "subclass1": "係助詞", "subclass2": "*", "subclass3": "*", "surface": "は", "yomi": "ハ"}}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [139.757845, 35.6960275]}, "properties": {"surface": "神保町", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "神保町", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "uN6ecI:神保町駅", "surface": "神保町", "yomi": ""}, "geoword_properties": {"body": "神保町", "dictionary_id": 3, "entry_id": "5WS6qh", "geolod_id": "uN6ecI", "hypernym": ["東京都", "10号線新宿線"], "institution_type": "公営鉄道", "latitude": "35.6960275", "longitude": "139.757845", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "に", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "に", "pos": "助詞", "prononciation": "ニ", "subclass1": "格助詞", "subclass2": "一般", "subclass3": "*", "surface": "に", "yomi": "ニ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "あり", "node_type": "NORMAL", "morphemes": {"conjugated_form": "五段・ラ行", "conjugation_type": "連用形", "original_form": "ある", "pos": "動詞", "prononciation": "アリ", "subclass1": "自立", "subclass2": "*", "subclass3": "*", "surface": "あり", "yomi": "アリ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "ます", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・マス", "conjugation_type": "基本形", "original_form": "ます", "pos": "助動詞", "prononciation": "マス", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "ます", "yomi": "マス"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "。", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "。", "pos": "記号", "prononciation": "。", "subclass1": "句点", "subclass2": "*", "subclass3": "*", "surface": "。", "yomi": "。"}}}]


.. _cli_setup:

基本辞書セットをインストール
----------------------------

``pygeonlp setup`` で pygeonlp に同梱されている基本辞書セットを
インストールします。 ::

    $ pygeonlp setup

このコマンドは基本辞書がアンインストールされていればインストールしなおします。


.. _cli_clear_dictionaries:

全ての辞書をアンインストール
----------------------------

``pygeonlp clear-dictionaries`` を実行すると、インストールされている
全ての辞書をアンインストールします。 ::

    $ pygeonlp clear-dictionaries


.. _cli_list_dictionaries:

インストール済み辞書を一覧表示
------------------------------

``pygeonlp list-dictionaries`` でインストール済みの地名解析辞書の一覧を表示します。 ::

    $ pygeonlp list-dictionaries
    geonlp:geoshape-city : 歴史的行政区域データセットβ版地名辞書
    - https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/
    歴史的行政区域データセットβ版で構築した地名辞書です。1920年から2020年までの国土 数値情報「行政区域データ」に出現する市区町村をリスト化し、独自の固有IDを付与して公開しています。データセット構築の詳しい手法については、「歴史的行政区域データセットβ版」のウェブサイトをご覧ください。
    ...

先頭の ``geonlp:geoshape-city`` がこの辞書の識別子です。
その後ろの「歴史的行政区域データセットβ版地名辞書」が辞書の名称です。
2行目の URL で辞書が公開されています。
3行目が辞書の概要説明です。

.. _cli_show_dictionary:

辞書の詳細情報を表示
--------------------

一覧には概要しか表示されませんので、ライセンスや更新日時などを
確認したい場合には ``pygeonlp show-dictionary`` で個別に辞書の
詳細情報を表示してください。 ::

    $ pygeonlp show-dictionary geonlp:geoshape-city
    {
    "@context": "https://schema.org/",
    "@type": "Dataset",
    "alternateName": "",
    "creator": [
        {
        "@type": "Organization",
        "name": "ROIS-DS人文学オープンデータ共同利用センター",
        "sameAs": "http://codh.rois.ac.jp/"
        }
    ],
    "dateModified": "2021-01-04T22:03:51+09:00",
    "description": "歴史的行政区域データセットβ版で構築した地名辞書です。1920年か ら2020年までの国土数値情報「行政区域データ」に出現する市区町村をリスト化し、独自の固有IDを付与して公開しています。データセット構築の詳しい手法については、「歴史的行政区域データセットβ版」のウェブサイトをご覧ください。",
    "distribution": [
        {
        "@type": "DataDownload",
        "contentUrl": "http://agora.ex.nii.ac.jp/GeoNLP/dict/geoshape-city.csv",
        "encodingFormat": "text/csv"
        }
    ],
    "identifier": [
        "geonlp:geoshape-city"
    ],
    "isBasedOn": {
        "@type": "CreativeWork",
        "name": "歴史的行政区域データセットβ版",
        "url": "https://geoshape.ex.nii.ac.jp/city/"
    },
    "keywords": [
        "GeoNLP",
        "地名辞書"
    ],
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "name": "歴史的行政区域データセットβ版地名辞書",
    "size": "16421",
    "spatialCoverage": {
        "@type": "Place",
        "geo": {
        "@type": "GeoShape",
        "box": "24.06092 123.004496 45.5566280626738 148.772556996888"
        }
    },
    "temporalCoverage": "../..",
    "url": "https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/"
    }


.. _cli_add_dictionary:

追加辞書をインストール
----------------------

基本辞書セット以外の地名解析辞書をインストールしたい場合、
まず辞書が公開されているページの URL が必要です。

`Google Dataset Search <https://datasetsearch.research.google.com/>`_
でキーワードに **geonlp** を指定すると簡単に見つけることができます。
たとえば「geonlp 郵便局」で検索すると
`国土数値情報：郵便局データ <https://geonlp.ex.nii.ac.jp/dictionary/ksj-post-office/>`_
が見つかると思います。

この辞書をインストールするには ``pygeonlp add-dictionary`` に
URL を指定します。 ::

    $ pygeonlp add-dictionary https://geonlp.ex.nii.ac.jp/dictionary/ksj-post-office/


.. _cli_remove_dictionary:

辞書をアンインストール
----------------------

インストール済みの地名解析辞書は、 ``pygeonlp remove-dictionary`` に
辞書の識別子を指定すると個別にアンインストールできます。 ::

    $ pygeonlp remove-dictionary geonlp:post-office
