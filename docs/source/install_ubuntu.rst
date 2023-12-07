:orphan:

.. _install_pygeonlp_ubuntu:

インストール手順 (Ubuntu)
=========================

ここでは Ubuntu に pygeonlp をインストールする手順の例を示します。
動作確認済みのバージョンは 20.04.6 LTS および 22.04.3 LTS です。

事前準備
--------

C++ の開発環境と MeCab および Boost を apt でインストールします。 ::

    $ sudo apt install build-essential libmecab-dev mecab-ipadic-utf8 libboost-all-dev

:py:class:`~pygeonlp.api.spatial_filter.SpatialFilter` を利用したい場合は
libgdal-dev もインストールします。 ::

    $ sudo apt install libgdal-dev

python, pip の準備
------------------

Ubuntu では OS デフォルトの Python3 を利用できます。
python3, pip3 を apt でインストールします。 ::

    $ sudo apt install python3 python3-pip

pygeonlp のインストール
-----------------------

pip3 コマンドで pygeonlp パッケージをインストールします。 ::

    $ pip3 install pygeonlp

pip や setuptools が古いとエラーが発生する場合があります。
その場合は pip と setuptools を最新バージョンにアップグレードしてから
実行してみてください。 ::

    $ pip3 install --upgrade pip setuptools

.. collapse:: (オプション)GDAL のインストール


    この項目はオプションです。

    :py:class:`SpatialFilter <pygeonlp.api.spatial_filter.SpatialFilter>`
    を利用するには `GDAL <https://gdal.org/index.html>`_ が必要です。

    まず以下のコマンドでインストールされている libgdal-dev のバージョンを確認します。 ::

        $ apt search libgdal-dev
        libgdal-dev/jammy,now 3.4.1+dfsg-1build4 amd64 [installed]
            Geospatial Data Abstraction Library - Development files

    上のように表示された場合は 3.4.1 です。
    また、**[installed]** と表示されている場合はインストール済みです。
    まだインストールされていない場合は apt でインストールしてください。

        $ sudo apt install libgdal-dev

    次に、 libgdal-dev と同じバージョンの
    `GDAL Python パッケージ <https://pypi.org/project/GDAL/>`_
    をインストールします。 ::

        $ pip3 install gdal==3.4.1

    ``==`` の後には libgdal-dev のバージョン番号を指定してください。
    GDAL が有効になっているかどうかは次の手順で確認してください。 ::

        $ python3
        >>> import osgeo

    GDAL が正しくインストールされていない場合は、
    ModuleNotFoundError になります。

|

以上でインストール完了です。 :ref:`test_pygeonlp` に進んでください。
