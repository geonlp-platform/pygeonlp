.. _pygeonlp_webapi_option_set_class:

set-class オプション
====================

解析対象とする固有名クラスを指定します。

固有名クラスは正規表現文字列のリストで指定してください。
また、除外したいクラスは先頭に ``-`` を指定してください。

:ref:`pygeonlp_webapi_option_set_class`,
:ref:`pygeonlp_webapi_option_remove_class`,
:ref:`pygeonlp_webapi_option_add_class` 
が同時に指定されている場合、
まず ``set-class``, 次に ``remove-class``, 最後に
``add-class`` が評価されます。

``set-class`` を指定しない場合、対象クラスは ``[r'.*']`` 
になります。つまりデータベース内の全ての地名語が対象です。

クラス名の評価は指定された順番に行なわれます。
つまり「鉄道施設は除く、ただし駅は利用する」という場合は
``[r'.*', r'-鉄道施設/.*', r'.*駅$']``
のように指定します。

**パラメータ**

*set-class* : list of str

  - 正規表現として解釈し、*パターンに一致する*
    固有名クラスを持つ地名語を解析対象とします


リクエストの例
++++++++++++++

全ての固有名クラスから ``鉄道施設/.*`` に一致するものを
除外したクラスを検索対象とします。
駅名は検索されなくなります。

.. literalinclude:: ../json/test_parse_set_class_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_parse_set_class_res.json
  :language: javascript
