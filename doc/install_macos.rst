.. _install_pygeonlp_macos:

インストール手順 (MacOS 11)
===========================

ここでは MacOS に pygeonlp をインストールする手順の例を示します。
動作確認済みのバージョンは 11.3.1 です。

事前に必要なもの
----------------

pygeonlp は日本語形態素解析に `MeCab <https://taku910.github.io/mecab/>`_ C++ ライブラリと UTF8 の辞書を利用します。
また、 C++ 実装部分が `Boost C++ <https://www.boost.org/>`_ に依存します。

MacOS の場合には `Homebrew <https://brew.sh/index_ja>`_ を利用します。

**Homebrew のインストール**

既に Homebrew をインストール・設定済みの場合はこの手順は不要です。

まず Homebrew 公式サイトの手順通りにインストールします。 ::

  % /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

画面に ``Next steps: Add Homebrew to your PATH...`` と表示されるので、
表示されたとおりに実行します。

.. code-block :: sh

  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
  eval "$(/opt/homebrew/bin/brew shellenv)"

これで brew を利用する準備が完了しました。

**MeCab と Boost のインストール**

brew コマンドで MeCab と Boost をインストールします。 ::

  % brew install mecab mecab-ipadic boost

python, pip の準備
------------------

MacOS 標準の Python3 は 3.8.5 で pygeonlp に対応していますが、
システムディレクトリ /Library/python の下にパッケージ群が
インストールされますので、お勧めしません。

ここでは Homebrew の python3 を利用する方法を説明します。

他のモジュールとの依存関係などで問題が起こる可能性があるので、
なるべく ``pyenv``, ``venv`` 等を利用して Python 3.8 以降の
環境を用意することをお勧めします。

**Homebrew の python3 を利用する場合**

まだ python3 をインストールしていない場合はインストールしてください。 ::

  % brew install python3
  % rehash
  % which python3
  /opt/homebrew/bin/python3
  % python3 --version
  Python 3.9.5

python3 をインストールすると pip3 も利用できます。

以降の説明の ``python`` を ``python3`` に、 ``pip`` を ``pip3`` に
読み換えてください。

**Pyenv を利用する場合**

Pyenv, Pipenv を利用する場合も Homebrew でインスト-ルできます。 ::

  % brew install pyenv pipenv
  % pyenv install --list  # 利用可能な python のリスト
  % pyenv install 3.9.5   # 3.8 または 3.9 で最新を推奨
  % pipenv --python=3.9.5

Python のパッケージは pyenv 環境内にインストールされます。

pygeonlp のインストール
-----------------------
pygeonlp パッケージは pip コマンドでインストールできますが、
パッケージ内の C++ 拡張モジュールをコンパイルするため、
Homebrew のヘッダファイルとライブラリの場所を環境変数で
指定する必要があります。

また、 Homebrew の boost が ``-std=c++14`` オプションを付けて
ビルドされているので、このオプションも指定する必要があります。 ::

  % CFLAGS="-I$HOMEBREW_PREFIX/include -std=c++14" LDFLAGS="-L$HOMEBREW_PREFIX/lib" pip install pygeonlp

インストールはこれで完了です。

**image not found エラー対応**

python を実行して pygeonlp.api パッケージをインポートする際に
libgcc が見つからないというエラーが発生する場合があります。 ::

  % python
  >>> import pygeonlp.api
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    ...
  ImportError: dlopen(/opt/homebrew/lib/python3.9/site-packages/lxml/etree.cpython-39-darwin.so, 2): Library not loaded: /opt/homebrew/opt/gcc/lib/gcc/11/libgcc_s.1.1.dylib
  Referenced from: /opt/homebrew/lib/python3.9/site-packages/lxml/etree.cpython-39-darwin.so
  Reason: image not found

このエラーは gcc をインストールすることで解決します。 ::

  % brew install gcc


**GDAL のインストール**

この項目はオプションです。

pygeonlp は `GDAL <https://pypi.org/project/GDAL/>`_ をインストールすると、
:ref:`spatialfilter` を利用することができます。

MacOS の場合は、 brew コマンドで gdal 3.3 をインストールします。
同時に brew python 用の gdal パッケージもインストールされます。 ::

  % brew install gdal

Pyenv 環境を利用している場合は、その環境の python 用に
pip で gdal パッケージをインストールしてください。 ::

  % pip install gdal==3.3

GDAL が有効になっているかどうかは次の手順で確認してください。 ::

  $ python
  >>> from pygeonlp.api.spatial_filter import GeoContainsFilter
  >>> gcfilter = GeoContainsFilter({"type":"Polygon","coordinates":[[[139.43,35.54],[139.91,35.54],[139.91,35.83],[139.43,35.83],[139.43,35.54]]]})

GDAL がインストールされていない場合は from の行で、
正常に動作していない場合は gcfilter の行で例外が発生します。
