.. _install_pygeonlp:

インストール手順
================

動作確認済みOSでの手順
----------------------

動作確認済み OS の場合は対応する手順を参照してください。

- :ref:`install_pygeonlp_ubuntu`
- :ref:`install_pygeonlp_centos`
- :ref:`install_pygeonlp_macos`

上記以外のOSでの手順
--------------------

pygeonlp は日本語形態素解析に `MeCab <https://taku910.github.io/mecab/>`_ C++ ライブラリと UTF8 の辞書を利用します。
また、 C++ 実装部分が `Boost C++ <https://www.boost.org/>`_ に依存します。
この2つは必ずインストールする必要があります。

オプションとして、 `GDAL <https://pypi.org/project/GDAL/>`_ を
インストールすると、 :ref:`spatialfilter` を利用することができます。

それぞれの OS に合わせて、以下の順序でインストールしてください。
なお、 Windows には対応していません。

- Python 3.6.8 以降と pip をインストール
- MeCab C++ ライブラリと IPA 辞書をインストール
- Boost C++ ライブラリをインストール (1.76 で動作確認) 
- pygeonlp を ``pip install pygeonlp`` でインストール
- (オプション) `GDAL <https://pypi.org/project/GDAL/>`_ をインストール

.. _setup_pygeonlp:

インストール後の設定作業
------------------------

pygeonlp のインストールが完了した後、地名解析辞書を
:ref:`pygeonlp_terms_database` に登録する作業を行なう必要があります。

pygeonlp モジュールには基本的な地名解析辞書が付属していますが、
そのままでは地名解析処理には利用できません。
初回実行時に次の処理を実行して、付属の地名解析辞書から
データベースを作成してください。 ::

  $ python
  >>> import pygeonlp.api as api
  >>> api.setup_basic_database()

データベースは :ref:`pygeonlp_terms_db_dir` に作成されます。
このディレクトリの場所を指定する方法については :ref:`pygeonlp_terms_db_dir`
を、作成されるデータベースの詳細については :ref:`pygeonlp_terms_database` を
参照してください。

この処理で登録される基本辞書は以下の3種類です。

- 日本の都道府県 (``geonlp:geoshape-pref``)
- 歴史的行政区域データセットβ版地名辞書 (``geonlp:geoshape-city``)
- 日本の鉄道駅（2019年） (``geonlp:ksj-station-N02-2019``)


**ディレクトリが見つからない場合**

環境によって、付属の地名解析辞書が見つからず、「地名解析辞書が
インストールされたディレクトリが見つかりません。」というエラーが
発生する場合があります。

その場合は以下の手順でディレクトリを見つけ、
`setup_basic_database() <pygeonlp.api.html#pygeonlp.api.setup_basic_database>`_
の ``src_dir`` パラメータで指定してください。

- pip uninstall を実行してパッケージに含まれるファイルリストを確認します。
  ``Proceed (y/n)?`` には n と答えてください。 ::

    % pip uninstall pygeonlp
    Uninstalling pygeonlp-1.0.0:
      Would remove:
      ...
      /opt/homebrew/pygeonlp_basedata/geoshape-pref.csv
      ...
    Proceed (y/n)? n

- ``geoshape-pref.csv`` などが含まれているディレクトリをメモします。
  上の例では ``/opt/homebrew/pygeonlp_basedata/`` です。

- ``setup_basic_database()`` でこのディレクトリを指定します。 ::

    $ python
    >>> import pygeonlp.api as api
    >>> api.setup_basic_database(src_dir='/opt/homebrew/pygeonlp_basedata/')


pygeonlp のアンインストール
---------------------------

pygeonlp が不要になった場合は以下のコマンドでアンインストールできます。 ::

  $ pip uninstall pygeonlp

GDAL も不要な場合にはアンインストールしてください。 ::

  $ pip uninstall gdal


データベースの完全削除
----------------------

地名語解析辞書を登録すると、データベースディレクトリにファイルを作成します。
データベースディレクトリがどこに作成されるかは
:ref:`pygeonlp_terms_db_dir` を参照してください。

それ以外の場所は変更しませんので、全てのデータベースを削除したい場合は
データベースディレクトリごと消去してください。
