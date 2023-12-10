.. _pygeonlp_webapi_getDictionaries:

geonlp.getDictionaries
======================

データベースに登録されている地名解析辞書の
identifier のリストを返します。

**リクエストパラメータ**

*options* : dict, optional
  - :ref:`pygeonlp_webapi_parse_option` を参照

**レスポンス**

辞書 identifier のリストを返します。


リクエストの例
++++++++++++++

.. literalinclude:: ../json/test_getDictionaries_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_getDictionaries_res.json
  :language: javascript
