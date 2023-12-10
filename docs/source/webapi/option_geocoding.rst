.. _pygeonlp_webapi_option_geocoding:

geocoding オプション
====================

住所ジオコーディングを利用するかどうかを指定します。

:ref:`pygeonlp_webapi_parse`, :ref:`pygeonlp_webapi_parseStructured` を実行する場合に、
このオプションに true がセットされていると
テキスト中の住所文字列を住所として解析します。

**パラメータ**

*geocoding* : bool, optional
  - true の場合、住所ジオコーディングを行ないます
  - false または省略されると住所ジオコーディングは行ないません


リクエストの例
++++++++++++++

住所ジオコーディングを利用します。

.. literalinclude:: ../json/test_parse_geocoding_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_parse_geocoding_res.json
  :language: javascript
