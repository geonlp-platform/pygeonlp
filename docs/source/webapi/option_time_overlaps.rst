.. _pygeonlp_webapi_option_time_overlaps:

time-overlaps オプション
========================

``TimeOverlapsFilter`` を作成し、 :ref:`pygeonlp_webapi_parse`
および :ref:`pygeonlp_webapi_parseStructured` の結果に対して
このフィルタを適用します。

パラメータで指定された時点または期間に存在した地名語
以外は地名語ではない固有名詞に置き換えられます。

このオプションは
:ref:`pygeonlp_webapi_option_time_exists`
と同じです。

**パラメータ**

*time-overlaps* : str, list of str, dict

  - str の場合、一時点を表す日付または日時と解釈します。
    
  - list の場合、要素が1つならば一時点を、2つならば期間を
    表す日付または日時と解釈します。

  - dict の場合、 ``date_from`` の値が期間の開始時点を、
    ``date_to`` の値が期間の終了時点を表す日付または日時と
    解釈します。 ``date_to`` は省略可能です。


リクエストの例
++++++++++++++

2000年1月1日から2001年2月1日の間に存在した地名語だけを抽出します。
「田無市」「保谷市」はこの期間内に合併して「西東京市」になったので、
「田無市」「保谷市」「西東京市」は地名語として解釈されます。

.. literalinclude:: ../json/test_time_overlaps_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_time_overlaps_res.json
  :language: javascript
