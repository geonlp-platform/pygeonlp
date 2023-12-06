.. _json_representation:

JSON表現
========

pygeonlp では、 `JSON <https://www.json.org/>`_ を利用して
`地名語 <https://geonlp.ex.nii.ac.jp/doc/documents/terms.html#geonlp-terms-geoword>`_ や
`住所 <https://geonlp.ex.nii.ac.jp/doc/documents/terms.html#geonlp-terms-address>`_
の情報を表現します。

ここではこれらの情報の JSON 表現について説明します。

.. _json_geoword:

地名語のJSON表現
----------------

地名語のJSON表記例を示します。 `GeoJSON <http://www.geojson.org/>`_ に準拠しています。

- properties.node\_type は `GEOWORD`
- properties.morphemes に MeCab の処理結果を格納
- properties.geoword\_properties に地名解析辞書の情報を格納

.. literalinclude:: geoword_jinbocho.json
   :language: json

.. _json_address:

住所のJSON表現
--------------

住所のJSON表記例を示します。 `GeoJSON <http://www.geojson.org/>`_ に準拠しています。

- properties.node\_type は `ADDRESS`
- properties.morphemes に住所文字列を構成するそれぞれの単語の情報を格納
- properties.address\_properties にジオコーダーの解析結果を格納

.. literalinclude:: address.json
   :language: json


.. _json_dictionary:

地名解析辞書メタデータのJSON表現
--------------------------------

地名解析辞書メタデータのJSON表記例を示します。

- 都道府県辞書の例

.. literalinclude:: dictionary_pref.json
   :language: json

- 市区町村辞書の例

.. literalinclude:: dictionary_city.json
   :language: json


