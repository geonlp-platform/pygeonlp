.. _pygeonlp_webapi_option_add_dic:

add-dic オプション
====================

利用する地名解析辞書を追加します。

:ref:`pygeonlp_webapi_option_set_dic` や
:ref:`pygeonlp_webapi_option_remove_dic` と併用した場合、
まず ``set-dic`` と ``remove-dic`` を評価して
利用する辞書を決定し、そこに ``add-dic`` で
指定された辞書を追加します。

``set-dic`` も ``remove-dic`` も指定されていない場合、
データベースに登録されている全ての辞書を利用するので、
``add-dic`` の指定は意味がありません。

**パラメータ**

*add-dic* : str, list of str

  - 文字列が指定された場合、正規表現として解釈し、
    *パターンを含む* identifier を持つ
    辞書を利用対象に追加します

  - 文字列のリストが指定された場合、
    利用する辞書 identifier のリストと解釈し、
    リストに含まれる identifier 持つ辞書を
    利用対象に追加します


リクエストの例
++++++++++++++

まず ``remove-dic`` で全ての辞書を除外し、次に ``add-dic`` で
identifier に 'city' を含む辞書 ( geonlp:geoshape-city )
を利用する辞書として追加します。
市区町村名しか検索されなくなります。

.. literalinclude:: ../json/test_parse_add_dic_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_parse_add_dic_res.json
  :language: javascript
