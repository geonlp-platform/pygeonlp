.. _install_pygeonlp_centos:

インストール手順 (CentOS 7)
===========================

ここでは CentOS に pygeonlp をインストールする手順の例を示します。
動作確認済みのバージョンは 7.9.2009 です。

事前に必要なもの
----------------

pygeonlp は日本語形態素解析に `MeCab <https://taku910.github.io/mecab/>`_ C++ ライブラリと UTF8 の辞書を利用します。
また、 C++ 実装部分が `Boost C++ <https://www.boost.org/>`_ に依存します。

CentOS 7 の場合には以下のコマンドでインストールできます。

Mecab が公式リポジトリに含まれていないため、groonga リポジトリを追加しています。
手動でコンパイル・インストールしてももちろん構いません。 ::

  $ sudo yum install --nogpgcheck -y https://packages.groonga.org/centos/groonga-release-latest.noarch.rpm
  $ sudo yum install mecab mecab-ipadic mecab-devel

Boost は公式リポジトリのものを利用します。 ::

  $ sudo yum install boost-devel

python, pip の準備
------------------

CentOS 7 の python3 は 3.6.8 のため、 pygeonlp に対応しています。

他のモジュールとの依存関係などで問題が起こる可能性があるので、
なるべく ``pyenv``, ``venv`` 等を利用して Python 3.8 以降の
環境を用意することをお勧めします。

**OS デフォルトの python を利用する場合**

まだ pip3 をインストールしていない場合はインストールしてください。
pygeonlp は C++ による拡張モジュールを含むため、開発環境も必要です。 ::

  $ sudo yum install python3 python3-devel python3-pip

パッケージをシステムレベルでインストールするには、 sudo が必要です。 ::

  $ sudo pip install <package>

sudo を付けない場合、自動的にユーザレベルでインストールされます。 ::

  $ pip install <package>
  Defaulting to user installation because normal site-packages is not writeable
  ...

**Pyenv を利用する場合**

pyenv のインストール方法は `pyenv github <https://github.com/pyenv/pyenv#basic-github-checkout>`_ の ``Basic GitHub Checkout`` の手順に
従ってください。

パッケージは pyenv 環境内にインストールされます。


pygeonlp のインストール
-----------------------

pygeonlp パッケージは pip コマンドでインストールできます。 ::

  $ pip install pygeonlp

pip や setuptools が古いとエラーが発生する場合があります。
その場合は pip と setuptools を最新バージョンにアップグレードしてから
実行してみてください。 ::

  $ pip install --upgrade pip setuptools

**GDAL のインストール**

この項目はオプションです。

pygeonlp は `GDAL <https://pypi.org/project/GDAL/>`_ をインストールすると、
:ref:`spatialfilter` を利用することができます。

CentOS 7 の場合は、 gdal 2.x 以上をパッケージインストールできる
リポジトリが見当たらないため、手動でコンパイルすることを推奨します（
`参考手順 <https://gist.github.com/alanorth/9681766ed4c737adfb48a4ef549a8503>`_
）。

非推奨ですが、コンパイルを行なわない方法として、 `anaconda <https://www.anaconda.com/>`_ で動作を確認しています。

まず pyenv をインストールしてください。次に、 pyenv 環境下で anaconda を
インストールします。 ::

  $ pyenv install --list | grep anaconda
  $ pyenv install anaconda3-2021.05   # 最新のものにしてください
  $ pyenv global anaconda3-2021.05
  $ conda update --all

次に pygeonlp を利用する conda 環境 myenv を作成します（名前は
myenv 以外でも構いません）。
anaconda の gdal が python 3.8.2 用なので、それに合わせます
(インストール可能な gdal は ``conda search gdal`` で探せます）。 ::

  $ conda create --name=myenv python=3.8.2
  $ conda activate myenv

この環境に pygeonlp をインストールしてから gdal をインストールします。
先に gdal をインストールすると、一緒にインストールされる boost が
公式リポジトリの boost-devel よりも優先されてしまい、
pygeonlp のコンパイルが失敗します。 ::

  $ pip install pygeonlp
  $ conda install gdal

次回以降は ``conda activate myenv`` で pygeonlp を利用できます。

GDAL が有効になっているかどうかは次の手順で確認してください。 ::

  $ python
  >>> from pygeonlp.api.spatial_filter import GeoContainsFilter
  >>> gcfilter = GeoContainsFilter({"type":"Polygon","coordinates":[[[139.43,35.54],[139.91,35.54],[139.91,35.83],[139.43,35.83],[139.43,35.54]]]})

GDAL がインストールされていない場合は from の行で、
正常に動作していない場合は gcfilter の行で例外が発生します。
