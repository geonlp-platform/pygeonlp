.. _pygeonlp_webapi_option_remove_dic:

remove-dic オプション
=====================

利用しない地名解析辞書を指定します。

:ref:`pygeonlp_webapi_option_set_dic` と併用した場合、
まず ``set-dic`` を評価して利用する辞書を決定し、
そこから ``remove-dic`` で指定された辞書を除外します。

``set-dic`` が指定されていない場合、データベースに
登録されている全ての辞書から ``remove-dic`` で
指定された辞書を除外します。

**パラメータ**

*remove-dic* : str, list of str

  - 文字列が指定された場合、正規表現として解釈し、
    *パターンを含む* identifier を持つ
    辞書を除外します

  - 文字列のリストが指定された場合、
    利用する辞書 identifier のリストと解釈し、
    リストに含まれる identifier 持つ辞書を除外します


リクエストの例
++++++++++++++

identifier に 'station' を含む辞書 (
geonlp:ksj-station-N02-2019 ) を利用しないように指定します。
駅名は検索されなくなります。

.. literalinclude:: ../json/test_parse_remove_dic_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_parse_remove_dic_res.json
  :language: javascript
