:orphan:

.. _install_pygeonlp_macosx:

インストール手順 (MacOS X)
==========================

ここでは MacOS X に pygeonlp をインストールする手順の例を示します。
動作確認済みのバージョンは 14.1.1 です。

事前準備
--------

C++ の開発環境を用意します。 MacOS X の場合には
Command line tools for Xcode および `Homebrew <https://brew.sh/ja/>`_ を利用します。

Command line tools は
`Apple のデベロッパーサイト <https://developer.apple.com/jp/xcode/resources/>`_
の「その他のダウンロード」リンクの先からダウンロードできます。

.. collapse:: Homebrew のインストール手順

    既に Homebrew をインストール・設定済みの場合はこの手順は不要です。

    まず Homebrew 公式サイトの手順通りにインストールします。 ::

        % /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    画面に ``Next steps: Add Homebrew to your PATH...`` と表示されるので、
    表示されたとおりに実行します。

    .. code-block :: sh

    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"

    これで brew を利用する準備が完了しました。

Homebrew を利用して MeCab および Boost をインストールします。 ::

    % brew install mecab mecab-ipadic boost

python, pip の準備
------------------

MacOS では OS デフォルトの Python3, pip3 を利用できます。

pygeonlp のインストール
-----------------------

pip3 コマンドで pygeonlp パッケージをインストールします。 ::

    $ pip3 install pygeonlp

pip や setuptools が古いとエラーが発生する場合があります。
その場合は pip と setuptools を最新バージョンにアップグレードしてから
実行してみてください。 ::

    $ pip3 install --upgrade pip setuptools

.. collapse:: image not found エラーの場合

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


.. collapse:: (オプション)GDAL のインストール

    この項目はオプションです。

    :py:class:`SpatialFilter <pygeonlp.api.spatial_filter.SpatialFilter>`
    を利用するには `GDAL <https://gdal.org/index.html>`_ が必要です。

    まず以下のコマンドでインストールされている GDAL のバージョンを確認します。 ::

        % brew info gdal
        ==> gdal: stable 3.8.1 (bottled), HEAD
        Geospatial Data Abstraction Library
        https://www.gdal.org/
        Conflicts with:
        avce00 (because both install a cpl_conv.h header)
        cpl (because both install cpl_error.h)
        Not installed
        From: https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/g/gdal.rb
        License: MIT
        ...

    1行目にバージョンが、7行目にインストール状況が表示されます。
    上の例ではバージョンは 3.8.1 で、インストール状況は `Not installed` ですので
    brew コマンドでインストールします。

        % brew install gdal

    次に、 gdal と同じバージョンの
    `GDAL Python パッケージ <https://pypi.org/project/GDAL/>`_
    をインストールします。 ::
    
        % pip3 install gdal==3.8.1

    GDAL が有効になっているかどうかは次の手順で確認してください。 ::

        $ python3
        >>> import osgeo

    GDAL が正しくインストールされていない場合は、
    ModuleNotFoundError になります。

|

以上でインストール完了です。 :ref:`test_pygeonlp` に進んでください。