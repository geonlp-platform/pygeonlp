.. _pygeonlp_webapi_option_set_dic:

set-dic オプション
====================

利用する地名解析辞書を指定します。

指定しない場合はデータベースに登録されている
全ての地名解析辞書が利用されます。

**パラメータ**

*set-dic* : str, list of str

  - 文字列が指定された場合、正規表現として解釈し、
    *パターンを含む* identifier を持つ
    辞書を利用します

  - 文字列のリストが指定された場合、
    利用する辞書 identifier のリストと解釈し、
    リストに含まれる identifier 持つ辞書を利用します


リクエストの例
++++++++++++++

identifier に 'geoshape' を含む辞書 (
geonlp:geoshape-city, geonlp:geoshape-pref ) を
利用するように指定します。駅名は検索されなくなります。

.. literalinclude:: ../json/test_parse_set_dic_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_parse_set_dic_res.json
  :language: javascript
