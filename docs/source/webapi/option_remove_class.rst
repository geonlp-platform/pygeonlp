.. _pygeonlp_webapi_option_remove_class:

remove-class オプション
=======================

解析対象とする固有名クラスを除外します。

固有名クラスは正規表現文字列のリストで指定してください。
また、クラス名の先頭に ``-`` を指定すると、そのクラスは
除外ではなく追加されます。

:ref:`pygeonlp_webapi_option_set_class`,
:ref:`pygeonlp_webapi_option_remove_class`,
:ref:`pygeonlp_webapi_option_add_class` 
が同時に指定されている場合、
まず ``set-class``, 次に ``remove-class``, 最後に
``add-class`` が評価されます。

``set-class`` が指定されていない場合は ``[r'.*']`` 
から除外します。

クラス名の評価は指定された順番に行なわれます。
つまり「鉄道施設は除く、ただし鉄道駅は利用する」という場合は
``[r'鉄道施設/.*', r'-.*駅$']`` のように指定します。


**パラメータ**

*add-class* : list of str

  - 正規表現として解釈し、*パターンに一致する*
    固有名クラスを持つ地名語を解析対象に追加します


リクエストの例
++++++++++++++

まず全ての固有名クラスを検索対象から除外し、
次に ``市区町村`` に一致するものを検索対象に追加します。
市区町村名しか検索されなくなります。

.. literalinclude:: ../json/test_parse_remove_class_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_parse_remove_class_res.json
  :language: javascript
