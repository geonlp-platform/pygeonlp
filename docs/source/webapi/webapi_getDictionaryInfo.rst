.. _pygeonlp_webapi_getDictionaryInfo:

geonlp.getDictionaryInfo
========================

指定された identifer を持つ地名解析辞書の JSONLD
メタデータをデータベースから取得します。

結果は JSONLD 文字列です。
JSONLD をデコードした JSON オブジェクトではない点に
注意してください。


**リクエストパラメータ**

*identifier* : str
  - 地名解析辞書の identifier

*options* : dict, optional
  - :ref:`pygeonlp_webapi_parse_option` を参照

**レスポンス**

辞書の jsonld メタデータ文字列を返します。
identifier と一致する辞書が存在しない場合には
null を返します。


リクエストの例
++++++++++++++

.. literalinclude:: ../json/test_getDictionaryInfo_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_getDictionaryInfo_res.json
  :language: javascript
