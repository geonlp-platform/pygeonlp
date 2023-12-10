.. _pygeonlp_webapi:

ウェブサービス機能
==================

JavaScript で構築されたウェブアプリケーションのフロントエンドや、
Python 以外の言語で開発したアプリケーションから、
地名語辞書を検索したりテキストのジオパージング処理を行ないたい場合があります。
そんなときは pygeonlp の解析・検索機能をウェブサービスとして提供する
バックエンドサーバを構築すれば、通信によってアプリケーション側から利用できます。

.. toctree::
   :maxdepth: 2

   install.rst
   run_server.rst
   run_docker.rst

WebAPI の使い方
---------------

pygeonlp.webapi は `JSON-RPC 2.0 <http://json-rpc.org/>`_ 
を利用します。

サービスのエンドポイント ``/api`` に JSON 
リクエストメッセージを POST し、
JSON レスポンスを受け取ります。 ::

  $ curl -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0", "method": "geonlp.parse", \
    "params": {"sentence": "NIIは神保町駅から徒歩7分です。"}, "id": "test_parse"}' \
    http://localhost:5000/api

上の例は、ジオパーズ 処理を行う :ref:`pygeonlp_webapi_parse` メソッドを呼び出し、
パラメータとして送信した文字列を解析した結果を受け取ります。
各メソッドで利用できるパラメータやレスポンスの内容については、
:ref:`pygeonlp_webapi_methods` から対応するメソッドの説明を参照してください。

.. note::

   WebAPI およびオプションは状態を保持しません。
   つまり、直前にどのようなリクエストを実行したかに関わらず、
   同じリクエストを送れば同じレスポンスが返ります。

   ただしサーバ側のバージョンやデータベースが変更された場合は、
   結果が変わることがあります。

.. _pygeonlp_webapi_methods:

WebAPI 一覧
-----------

以下の WebAPI メソッドが利用できます。

.. toctree::
   :maxdepth: 1

   webapi_parse.rst
   webapi_parseStructured.rst
   webapi_search.rst
   webapi_getGeoInfo.rst
   webapi_getDictionaries.rst
   webapi_getDictionaryInfo.rst
   webapi_addressGeocoding.rst
   webapi_version.rst


.. _pygeonlp_webapi_parse_option:

Parse オプション
----------------

:ref:`pygeonlp_webapi_parse` および :ref:`pygeonlp_webapi_parseStructured` は
ジオパーズ処理を細かく制御するためのオプションを指定することができます。
たとえば利用する地名語の地名解析辞書や固有名クラスを制限したり、
結果に対して適用するフィルタを指定できます。

以下の Parse オプションが利用できます。

.. toctree::
   :maxdepth: 1

   option_geocoding.rst
   option_set_dic.rst
   option_remove_dic.rst
   option_add_dic.rst
   option_set_class.rst
   option_remove_class.rst
   option_add_class.rst
   option_geo_contains.rst
   option_geo_disjoint.rst
   option_time_exists.rst
   option_time_before.rst
   option_time_after.rst
   option_time_overlaps.rst
   option_time_covers.rst
