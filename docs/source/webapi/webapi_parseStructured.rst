.. _pygeonlp_webapi_parseStructured:

geonlp.parseStructured
======================

複数のセンテンスを geoparse します。

このメソッドは、リストのそれぞれのテキストを geoparse してから
結果を結合します。

先にテキストを結合して ``parse()`` を呼んだ場合と比較すると、
長すぎるテキストの分割を自動で行なうか、呼びだす側で
指定するかの違いがあります。

自動的に分割すると、意味的に連続したパラグラフの途中で
切れてしまうことがあり、地名解決の精度が低下します。
そのためテキストの意味的な区切り（文、段落など）が
分かっている場合は、1ブロックずつ ``parse()`` で処理するか、
``parseStructured()`` を利用してください。

**リクエストパラメータ**

*sentence_list* : list of str
  - 変換したいテキストのリスト
  - 長さの上限なし、件数の上限なし

*options* : dict, optional
  - :ref:`pygeonlp_webapi_parse_option` を参照

**レスポンス**

``features`` に GeoJSON Feature 形式の地名語、
非地名語、住所をリストとして含む
FeatureCollection 形式の GeoJSON を返します。


リクエストの例
++++++++++++++

.. literalinclude:: ../json/test_parseStructured_req.json
   :language: javascript

レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_parseStructured_res.json
  :language: javascript

