:orphan:

.. _install_pygeonlp_other:

インストール手順 (その他)
=========================

ここではその他の環境 に pygeonlp をインストールする手順の
ガイドラインを示します。環境によっては動作しない可能性もあります。

事前準備
--------

動作確認済み環境以外でインストールする場合の手順を説明します。

それぞれの OS に合わせて、以下の順序でインストールしてください。
なお、 Windows には対応していないので `WSL を利用
<https://learn.microsoft.com/ja-jp/windows/wsl/install>`_ して
Ubuntu でご利用ください。

- C++ 開発環境 (GNU C++ や make コマンド等)
- 日本語形態素解析器 `MeCab <https://taku910.github.io/mecab/>`_
    C++ ライブラリと IPA 辞書
- `Boost C++ <https://www.boost.org/>`_ ライブラリ (1.76 で動作確認) 

python, pip の準備
------------------

Python 3.6.8 以降と pip をインストールしてください。
Python 3.11 までは動作確認済みです。

pygeonlp のインストール
-----------------------

pip コマンドで pygeonlp パッケージをインストールします。 ::

    $ pip install pygeonlp

pip や setuptools が古いとエラーが発生する場合があります。
その場合は pip と setuptools を最新バージョンにアップグレードしてから
実行してみてください。 ::

    $ pip install --upgrade pip setuptools

.. collapse:: (オプション)GDAL のインストール

    この項目はオプションです。

    :py:class:`SpatialFilter <pygeonlp.api.spatial_filter.SpatialFilter>`
    を利用するには `GDAL <https://gdal.org/index.html>`_ が必要です。
    公式サイトの手順に従ってインストールしてください。

    GDAL を Python から呼び出すための
    `GDAL Python パッケージ <https://pypi.org/project/GDAL/>`_
    も環境に合わせてインストールしてください。

    GDAL が有効になっているかどうかは次の手順で確認してください。 ::

        $ python
        >>> import osgeo

    GDAL と Python パッケージが正しくインストールされていない場合は、
    ModuleNotFoundError になります。

|

以上でインストール完了です。 :ref:`test_pygeonlp` に進んでください。
