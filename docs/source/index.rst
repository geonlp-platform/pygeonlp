.. _pygeonlp:

PyGeoNLP リファレンス
=====================

PyGeoNLP は、普通の日本語テキスト（自然文）から、地名の部分を抽出する
geotagger や geoparser と呼ばれるツールの一つです。

.. code-block:: bash

    % echo "目黒駅は品川区にあります。" | pygeonlp geoparse
    目黒駅  名詞,固有名詞,地名語,Xy26iV:目黒駅,*,*,目黒駅,, 鉄道施設/鉄道駅,Xy26iV, 目黒駅,139.71566,35.632485
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    品川区  名詞,固有名詞,地名語,kEAYBl:品川区,*,*,品川区,, 市区町村,kEAYBl,品川区,139.73025000,35.60906600
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS


目次
----

.. toctree::
    :numbered:
    :maxdepth: 2

    overview.rst
    install.rst
    cli.rst
    quick_start.rst
    link_neologd.rst
    link_jageocoder.rst
    tuning.rst
    advanced.rst
    terms.rst
    json/index.rst
    api/pygeonlp.api.rst
