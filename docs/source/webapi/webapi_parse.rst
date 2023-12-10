.. _pygeonlp_webapi_parse:

geonlp.parse
============

テキストを geoparse します。

**リクエストパラメータ**

*sentence* : str
  - 変換したいテキスト
  - 長さの上限なし

*options* : dict, optional
  - :ref:`pygeonlp_webapi_parse_option` を参照

**レスポンス**

``features`` に GeoJSON Feature 形式の
地名語、非地名語、住所をリストとして含む
FeatureCollection 形式の GeoJSON を返します。


リクエストの例
++++++++++++++

.. literalinclude:: ../json/test_parse_req.json
   :language: javascript

レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_parse_res.json
  :language: javascript

