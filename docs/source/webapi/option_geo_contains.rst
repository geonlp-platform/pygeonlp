.. _pygeonlp_webapi_option_geo_contains:

geo-contains オプション
=======================

``GeoContainsFilter`` を作成し、 :ref:`pygeonlp_webapi_parse`
および :ref:`pygeonlp_webapi_parseStructured` の結果に対して
このフィルタを適用します。

パラメータで指定された GeoJSON が表す領域に含まれる地名語
以外は地名語ではない固有名詞に置き換えられます。

**パラメータ**

*geo-contains* : str, dict

  - str の場合、まず GeoJSON 文字列として解釈します。
    JSON 文字列では無い場合は GeoJSON を返す URL と解釈し、
    HTTP で問い合わせを行ないます。
    
  - dict の場合、 GeoJSON をデコードしたオブジェクトと
    解釈します。 FeatureCollection, Feature, および
    geometry に対応します。


リクエストの例
++++++++++++++

東京周辺を含むポリゴンを空間領域として指定し、
その領域に含まれる地名語だけを抽出します。
「府中」は東京都の府中駅に解決されます。

.. literalinclude:: ../json/test_parse_geo_contains_req.json
   :language: javascript


レスポンスの例
++++++++++++++

.. literalinclude:: ../json/test_parse_geo_contains_res.json
  :language: javascript
