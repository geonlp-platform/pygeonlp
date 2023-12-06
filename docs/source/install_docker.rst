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

作成した Dockerfile があるフォルダでイメージを作成します。 ::

    % docker build -t pygeonlp .


コンテナを生成して実行
----------------------

作成したイメージからコンテナを作成して bash コマンドを実行します。 ::

    % docker run -it pygeonlp bash
    root@75243c7b8ddd:/#

python3 を対話モードで起動し、 pygeonlp が動作することを確認してください。 ::

    % python3
    Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import pygeonlp.api
    >>> pygeonlp.api.init()
    >>> pygeonlp.api.geoparse('目黒駅は品川区')
    [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.71566, 35.632485]}, 'properties': {'surface': '目黒駅', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '目黒駅', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'Xy26iV:目黒駅', 'surface': '目黒駅', 'yomi': ''}, 'geoword_properties': {'body': '目黒', 'dictionary_id': 3, 'entry_id': 'GvksxA', 'geolod_id': 'Xy26iV', 'hypernym': ['東京都', '6号線三田線'], 'institution_type': '公営鉄 道', 'latitude': '35.632485', 'longitude': '139.71566', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'は', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}}}, {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.73025, 35.609066]}, 'properties': {'surface': '品川区', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '品川区', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'kEAYBl:品川区', 'surface': '品川区', 'yomi': ''}, 'geoword_properties': {'address': '東京都品川区', 'body': '品川', 'body_variants': '品川', 'code': {}, 'countyname': '', 'countyname_variants': '', 'dictionary_id': 1, 'entry_id': '13109A1968', 'geolod_id': 'kEAYBl', 'hypernym': ['東京都'], 'latitude': '35.60906600', 'longitude': '139.73025000', 'ne_class': '市区町村', 'prefname': '東京都', 'prefname_variants': '東京都', 'source': '1/品 川区役所/品川区広町2-1-36/P34-14_13.xml', 'suffix': ['区'], 'valid_from': '', 'valid_to': '', 'dictionary_identifier': 'geonlp:geoshape-city'}}}]

osgeo/gdal イメージを拡張しているので、
:py:class:`SpatialFilter <pygeonlp.api.spatial_filter.SpatialFilter>`
も利用できます。

|

以上でインストール完了です。
