.. _install_pygeonlp_ubuntu:

インストール手順 (Ubuntu 18)
============================

ここでは Ubuntu に pygeonlp をインストールする手順の例を示します。
動作確認済みのバージョンは 18.04.5 LTS です。

事前に必要なもの
----------------

pygeonlp は日本語形態素解析に `MeCab <https://taku910.github.io/mecab/>`_ C++ ライブラリと UTF8 の辞書を利用します。
また、 C++ 実装部分が `Boost C++ <https://www.boost.org/>`_ に依存します。

Ubuntu 18 の場合には以下のコマンドでインストールできます。 ::

  $ sudo apt install libmecab-dev mecab-ipadic-utf8 libboost-all-dev

python, pip の準備
------------------

Ubuntu 18 の python3 は 3.6.9 のため、 pygeonlp に対応しています。

他のモジュールとの依存関係などで問題が起こる可能性があるので、
なるべく ``pyenv``, ``venv`` 等を利用して Python 3.8 以降の
環境を用意することをお勧めします。

**OS デフォルトの python を利用する場合**

まだ pip3 をインストールしていない場合はインストールしてください。 ::

  $ sudo apt install python3-pip

以降の説明の ``python`` を ``python3`` に、 ``pip`` を ``pip3`` に
読み換えてください。

パッケージをシステムレベルでインストールするには、 sudo が必要です。 ::

  $ sudo pip3 install <package>

ユーザレベルでインストールするには、 --user オプションを付けてください。 ::

  $ pip3 install <package> --user

**Pyenv を利用する場合**

pyenv のインストール方法は `pyenv github <https://github.com/pyenv/pyenv#basic-github-checkout>`_ の ``Basic GitHub Checkout`` の手順に
従ってください。

パッケージは pyenv 環境内にインストールされます。

pygeonlp のインストール
-----------------------

pygeonlp パッケージは pip でインストールできます。 ::

  $ pip install pygeonlp

pip や setuptools が古いとエラーが発生する場合があります。
その場合は pip と setuptools を最新バージョンにアップグレードしてから
実行してみてください。 ::

  $ pip install --upgrade pip setuptools

**GDAL のインストール**

この項目はオプションです。

pygeonlp は `GDAL <https://pypi.org/project/GDAL/>`_ をインストールすると、
:ref:`spatialfilter` を利用することができます。

Ubuntu 18 の場合は以下の手順で libgdal と Python 用 gdal パッケージを
インストールしてください。 ::

  $ sudo apt install libgdal-dev
  $ pip install gdal

ただし libgdal と gdal パッケージのバージョンが一致している必要があります。
たとえば ::

  $ apt search libgdal-dev
  libgdal-dev/bionic,now 2.4.2+dfsg-1~bionic0 amd64

のように libgdal 2.4.2 がインストールされている場合は、 gdal も 2.4.2 を
インストールしてください。 ::

  $ pip install gdal==2.4.2

GDAL が有効になっているかどうかは次の手順で確認してください。 ::

  $ python
  >>> from pygeonlp.api.spatial_filter import GeoContainsFilter
  >>> gcfilter = GeoContainsFilter({"type":"Polygon","coordinates":[[[139.43,35.54],[139.91,35.54],[139.91,35.83],[139.43,35.83],[139.43,35.54]]]})

GDAL がインストールされていない場合は from の行で、
正常に動作していない場合は gcfilter の行で例外が発生します。
