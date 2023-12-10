.. _pygeonlp_webapi_search:

geonlp.search
=============

地名語の情報をデータベースから検索します。

**リクエストパラメータ**

*key* : str
  - 検索したい語の表記または読み

*options* : dict, optional
  - :ref:`pygeonlp_webapi_parse_option` を参照

**レスポンス**

geolod_id をキー、地名語の情報を値に持つ JSON 
オブジェクトを返します。


リクエストの例
++++++++++++++

.. literalinclude:: ../json/test_search_req.json
   :language: javascript

レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_search_res.json
  :language: javascript

