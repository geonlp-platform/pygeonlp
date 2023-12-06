.. _dict_management_pygeonlp:

地名解析辞書の管理
==================

ここではインストールされている地名解析辞書を管理する方法を説明します。


.. _list_installed_dictionaries:

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


.. _install_dictionary:

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


.. _uninstall_dictionary:

辞書をアンインストール
----------------------

インストール済みの地名解析辞書は、 ``pygeonlp remove-dictionary`` に
辞書の識別子を指定すると個別にアンインストールできます。 ::

    $ pygeonlp remove-dictionary geonlp:post-office

あるいは ``pygeonlp clear-dictionaires`` で全ての辞書を削除してから、
必要な辞書をインストールしなおす方法もあります。 ::

    $ pygeonlp clear-dictionaries
    $ pygeonlp setup
