.. _pygeonlp_webapi_addressGeocoding:

geonlp.addressGeocoding
=======================

住所ジオコーディング処理を行ないます。

**リクエストパラメータ**

*address* : str
  - 住所文字列

**レスポンス**

住所ジオコーディングの結果を JSON で返します。


リクエストの例
++++++++++++++

.. literalinclude:: ../json/test_addressGeocoding_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_addressGeocoding_res.json
  :language: javascript
