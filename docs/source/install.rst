.. _install_pygeonlp:

インストール手順
================

動作確認済み環境
----------------

pygeonlp は以下の環境で動作確認済みです。

- x86_64 アーキテクチャ / Ubuntu 22.04.3 LTS
- aarm64 アーキテクチャ / MacOS X Sonoma 14.1.1
- Windows Subsystem for Linux / Ubuntu 20.04.6 LTS
- x86_64, aarm64 アーキテクチャ / Docker desktop, Docker engine

環境ごとのインストール手順は、リンク先を参照してください。

- :ref:`install_pygeonlp_ubuntu`
- :ref:`install_pygeonlp_macosx`
- :ref:`install_pygeonlp_docker`
- :ref:`install_pygeonlp_other`


.. _test_pygeonlp:

動作確認
--------

インストールが完了したら動作確認を行います。
**pygeonlp geoparse** コマンドを実行してください。 ::

    $ pygeonlp geoparse
    /home/foo/geonlp/db に基本辞書セットをインストールしますか? (y/n):

初回実行時は上のように基本辞書セットをインストールするかどうか
確認するメッセージが表示されますので、 "y" を入力してください。

.. collapse:: 基本辞書セットとは

    標準でインストールされる基本辞書は以下の3種類です。

    - 日本の都道府県 (**geonlp:geoshape-pref**)
    - 歴史的行政区域データセットβ版地名辞書 (**geonlp:geoshape-city**)
    - 日本の鉄道駅（2019年） (**geonlp:ksj-station-N02-2019**)


.. collapse:: インストール先を変更したい場合

    pygeonlp はデフォルトで環境変数 **HOME** の下の **geonlp/db** に
    辞書をインストールしたデータベースを作成します。
    インストール先を変更したい場合は setup のパラメータに
    インストール先ディレクトリを指定してください。  ::

        $ pygeonlp setup --db-dir=/home/foo/share/geonlp/db

    または、環境変数 **GEONLP_DB_DIR** をセットしておくと、
    そのディレクトリを参照します。

        $ export GEONLP_DB_DIR=/home/foo/share/geonlp/db
        $ pygeonlp setup


.. collapse:: 「ディレクトリが見つからない」というエラーの場合

    環境によって、付属の地名解析辞書が見つからず、「地名解析辞書が
    インストールされたディレクトリが見つかりません。」というエラーが
    発生する場合があります。

    その場合は以下の手順でディレクトリを見つけ、
    **setup** のパラメータで指定してください。

    - pip uninstall を実行してパッケージに含まれるファイルリストを確認します。
      **Proceed (y/n)?** には n と答えてください。 ::

        % pip uninstall pygeonlp
        Uninstalling pygeonlp-1.0.0:
        Would remove:
        ...
        /opt/homebrew/pygeonlp_basedata/geoshape-pref.csv
        ...
        Proceed (y/n)? n

    - **geoshape-pref.csv** などが含まれているディレクトリをメモします。
      上の例では **/opt/homebrew/pygeonlp_basedata/** です。

    - **setup** のパラメータとしてこのディレクトリを指定します。 ::

        $ pygeonlp setup /opt/homebrew/pygeonlp_basedata

|

辞書のインストールが終わると、テキストの入力待ちになります。
地名を含む日本語のテキストを入力すると解析結果が表示されます。
終了したい場合は Ctrl+D で EOF コードを送信してください。 ::

    $ pygeonlp geoparse
    /home/foo/geonlp/db に基本辞書セットをインストールしますか? (y/n):
    完了しました。
    目黒駅は品川区上大崎にあります。
    目黒駅  名詞,固有名詞,地名語,Xy26iV:目黒駅,*,*,目黒駅,, 鉄道施設/鉄道駅,Xy26iV, 目黒駅,139.71566,35.632485
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    品川区  名詞,固有名詞,地名語,kEAYBl:品川区,*,*,品川区,, 市区町村,kEAYBl,品川区,139.73025000,35.60906600
    上大崎  名詞,固有名詞,地域,一般,*,*,上大崎,カミオオサキ,カミオーサキ
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS
    品川駅は港区高輪にあります。
    品川駅  名詞,固有名詞,地名語,jUUOco:品川駅,*,*,品川駅,, 鉄道施設/鉄道駅,jUUOco, 品川駅,139.738535,35.628135
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    港区    名詞,固有名詞,地名語,2CWYZ5:港区,*,*,港区,,     市区町村,2CWYZ5,港区,139.75159900,35.65807100
    高輪    名詞,固有名詞,地域,一般,*,*,高輪,タカナワ,タカナワ
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS


.. _uninstall_pygeonlp:

pygeonlp のアンインストール
---------------------------

pygeonlp が不要になった場合は以下のコマンドでアンインストールできます。 ::

    $ pip uninstall pygeonlp

GDAL も不要な場合にはアンインストールしてください。 ::

    $ pip uninstall gdal

.. _purge_database_pygeonlp:

データベースの完全削除
----------------------

地名語解析辞書をインストールすると、データベースディレクトリにいくつかの
ファイルを作成します。データベースディレクトリがどこに作成されるかは
:ref:`pygeonlp_terms_db_dir` を参照してください。

それ以外の場所は変更しませんので、全てのデータベースを削除したい場合は
データベースディレクトリごと消去してください。 ::

    (デフォルトの場合)
    $ rm -r ~/geonlp
    (環境変数 GEONLP_DB_DIR をセットした場合)
    $ rm -r `echo $GEONLP_DB_DIR`
