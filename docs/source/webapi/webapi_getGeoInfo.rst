.. _pygeonlp_webapi_getGeoInfo:

geonlp.getGeoInfo
=================

指定した geolod_id を持つ語の情報を返します。
id がデータベースに存在しない場合は null を返します。

**リクエストパラメータ**

*key* : list of str
  - 検索する語の geolod_id のリスト

*options* : dict, optional
  - :ref:`pygeonlp_webapi_parse_option` を参照

**レスポンス**

geolod_id をキー、地名語の情報を値に持つ JSON 
オブジェクトを返します。


リクエストの例
++++++++++++++

.. literalinclude:: ../json/test_getGeoInfo_idlist_req.json
   :language: javascript

レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_getGeoInfo_idlist_res.json
   :language: javascript
