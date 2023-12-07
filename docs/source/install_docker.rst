:orphan:

.. _install_pygeonlp_docker:

インストール手順 (Docker)
=========================

ここでは Docker 環境 に pygeonlp をインストールする手順を示します。

事前準備
--------

OS に合わせて
`Docker Desktop <https://www.docker.com/products/docker-desktop/>`_
または
`Docker Server <https://docs.docker.com/engine/install/>`_ 
をインストールしてください。

Docker Desktop for Windows, Docker Desktop for Mac (macOS),
Docker Server for Ubuntu で動作確認済みです。


Dockerfile を作成
-----------------

空のフォルダを作成し、その中にテキストエディタで
以下の内容を含む Dockerfile を作成します。

.. code-block:: docker

    FROM osgeo/gdal:ubuntu-full-3.6.3
    # This image is built on "Ubuntu 22.04.2 LTS"

    ENV JAGEOCODER_DB2_DIR /opt/db2

    # Install the required Python packages.
    RUN apt-get update && apt-get install -y \
        libmecab-dev \
        mecab-ipadic-utf8 \
        libboost-all-dev \
        libsqlite3-dev \
        curl \
        python3 \
        python3-dev \
        python3-pip
    RUN python3 -m pip install pygeonlp && python3 -m pygeonlp.api setup


Docker イメージを作成
---------------------

作成した Dockerfile があるフォルダで
`docker build <https://docs.docker.jp/engine/reference/commandline/build.html>`_
を実行し、イメージを作成します。 **-t** は作成したイメージに
名前タグを付けるオプションです。 ::

    % docker build -t pygeonlp_image .


コンテナを生成して実行
----------------------

`docker run <https://docs.docker.jp/engine/reference/run.html>`_
を実行し、作成したイメージからコンテナを作成して bash を実行します。
**--name** は作成したコンテナに名前を付けるオプションです。
**-it** はコンテナに仮想端末を割り当てます。 ::

    % docker run --name pygeonlp -it pygeonlp_image bash
    root@75243c7b8ddd:/#

動作確認のため **pygeonlp geoparse** を実行し、
地名を含む日本語テキストを入力してみてください。 ::

    root@75243c7b8ddd:/# pygeonlp geoparse
    渋谷じゃなくて新宿に行こう。
    渋谷    名詞,固有名詞,地名語,RCU4nF:渋谷駅,*,,渋谷,,    鉄道施設/鉄道駅,RCU4nF,渋谷駅,139.70258433333333,35.659098666666665
    じゃ    助詞,副助詞,*,*,*,*,じゃ,ジャ,ジャ
    なく    助動詞,*,*,*,連用テ接続,特殊・ナイ,ない,ナク,ナク
    て      助詞,接続助詞,*,*,*,*,て,テ,テ
    新宿    名詞,固有名詞,地名語,8A8y00:新宿駅,*,,新宿,,    鉄道施設/鉄道駅,8A8y00,新宿駅,139.70059,35.69244
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    行こ    動詞,自立,*,*,未然ウ接続,五段・カ行促音便,行く,イコ,イコ
    う      助動詞,*,*,*,基本形,不変化型,う,ウ,ウ
    。      記号,句点,*,*,*,*,。,。,。
    EOS

**Ctrl+D** を押して EOF を送信するとシェルプロンプトに戻ります。
**exit** でコンテナを終了します。 ::

    root@75243c7b8ddd:/# exit

もう一度このコンテナを実行したい場合は
`docker start <https://docs.docker.jp/engine/reference/commandline/start.html>`_
で起動します。 ::

    % docker start -a -i pygeonlp
    root@75243c7b8ddd:/#

以上でインストール完了です。


コンテナとイメージの削除
------------------------

コンテナが不要になった場合は
`docker rm <https://docs.docker.jp/engine/reference/commandline/rm.html>`_
コマンドで削除します。 ::

    % docker rm pygeonlp

イメージが不要になった場合は
`docker rmi <https://docs.docker.jp/engine/reference/commandline/rmi.html>`_
コマンドで削除します。 ::

    % docker rmi pygeonlp_image


パイプ処理
----------

pygeonlp コンテナをパイプとして利用したい場合は、次のように
**docker run** に **--rm** オプションを付けて実行し、
処理が終わったコンテナを自動的に削除するようにします。 ::

    % echo "目黒駅は品川区にあります。" | docker run --rm -i pygeonlp_image pygeonlp geoparse > result.txt
    % cat result.txt
    目黒駅  名詞,固有名詞,地名語,Xy26iV:目黒駅,*,*,目黒駅,, 鉄道施設/鉄道駅,Xy26iV,目黒駅,139.71566,35.632485
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    品川区  名詞,固有名詞,地名語,kEAYBl:品川区,*,*,品川区,, 市区町村,kEAYBl,品川区,139.73025000,35.60906600
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS


拡張機能対応
------------

上記の Dockerfile は最小限の機能を持つイメージを作成します。
実際に利用する際は追加の :ref:`cli_add_dictionary` したり、
:ref:`link_jageocoder` や :ref:`link_neologd` が必要になる場合があります。

これらの機能を含めたイメージを作成するための
Dockerfile のサンプルを示しますので、必要に応じてカスタマイズして
ご利用ください。

.. literalinclude:: ../../Dockerfile
    :language: docker
