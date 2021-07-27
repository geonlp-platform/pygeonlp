.. _pygeonlp_terms:

pygeonlp の用語
===============

ここでは pygeonlp で利用する用語を定義します。

.. _pygeonlp_terms_geoword:

地名語
------

GeoNLP 共通の :ref:`geonlp_terms_geoword` を参照してください。

pygeonlp では、地名語は :ref:`geonlp_terms_dictionary` から
`api.addDictionaryFromFile() <pygeonlp.api.html#pygeonlp.api.addDictionaryFromFile>`_
または
`api.addDictionaryFromWeb() <pygeonlp.api.html#pygeonlp.api.addDictionaryFromWeb>`_ 
で読み込み、 :ref:`pygeonlp_terms_database` に登録すると、
地名解析に利用できるようになります。


.. _pygeonlp_terms_dictionary:

地名解析辞書
------------

GeoNLP 共通の :ref:`geonlp_terms_dictionary` を参照してください。

pygeonlp では、地名解析辞書は CSV 形式のファイルとして扱います。

.. _pygeonlp_terms_database:

データベース
------------

pygeonlp では地名抽出を効率よく行なうため、地名語をデータベースに
登録して管理しています。データベースには以下のファイルが含まれています。

- ``geodic.sq3``

  地名解析辞書から読み込んだ地名語のリストを格納する SQLite3 
  データベースファイルです。

- ``wordlist.sq3``

  地名語のリストから作成した、表記と :ref:`geonlp_terms_geolod_id` の
  関係を記録した SQLite3 データベースファイルです。

- ``geo_name_fullname.drt``

  テキスト中の地名語を効率よく抽出するには Common Prefix Search 処理を
  高速に行なう必要があります。 pygeonlp では
  `Darts <http://chasen.org/~taku/software/darts/>`_ を利用しており、
  登録されている全ての地名語表記から作成した Darts 辞書ファイルを
  ``geo_name_fullname.drt`` というファイル名で保存しています。

`pygeonlp.api.updateIndex() <pygeonlp.api.html#pygeonlp.api.updateIndex>`_
API は ``geodic.sq3`` から ``wordlist.sq3`` と ``geo_name_fullname.drt`` を作る処理を行ないます。


.. _pygeonlp_terms_db_dir:

データベースディレクトリ
------------------------

:ref:`pygeonlp_terms_database` を配置するディレクトリを指します。

データベースを複数用意したい場合、データベース内のファイル名は固定なので、
ディレクトリを変更する必要があります（データベースはディレクトリごと
コピーすれば複製できます）。

データベースディレクトリは次の順序で決定されます。

- API の ``db_dir`` パラメータで指定されたディレクトリ
- 環境変数 ``GEONLP_DB_DIR`` がセットされている場合はその値
- 環境変数 ``HOME`` がセットされている場合は ``$HOME/geonlp/db/``

上記のいずれも当てはまらない場合は ``RuntimeError`` になります。

Docker や仮想環境で、コードを変更せずにデータベースディレクトリを
変更したい場合には、環境変数 ``HOME`` または ``GEONLP_DB_DIR`` を
セットするのが便利です。

一つの環境の中で、処理によって利用するデータベースを切り替えたいという
場合には、 ``api.init()`` を呼ぶ時に ``db_dir`` パラメータを省略せずに
指定してください。 ::

  python
  >>> import pygeonlp.api as api
  >>> api.init(db_dir='/usr/local/share/lib/geonlp/db')
  >>> ... (共通データベースを利用した処理) ...
  >>> api.init(db_dir='/home/me/geonlp/testdb')
  >>> ... (テスト用データベースを利用した処理) ...

``db_dir`` が指定できる API は、 
`pygeonlp.api.init() <pygeonlp/pygeonlp.api.html#pygeonlp.api.init>`_ 
と
`pygeonlp.api.setup_basic_database() <pygeonlp.api.html#pygeonlp.api.setup_basic_database>`_ 
の2つのモジュール APIと、
クラス API `pygeonlp.api.service.Service() <pygeonlp.api.service.html#pygeonlp.api.service.Service>`_
の合計 3 つです。


.. _pygeonlp_terms_lattice_format:

ラティス表現
------------

ラティス表現は、地名解析処理の途中で利用する内部データ表現です。

テキストを形態素に分解し、それぞれの形態素に対して1個以上の候補
`Node <pygeonlp.api.node.html#pygeonlp.api.node.Node>`_ 
オブジェクトが含まれる二重リスト構造です。

例： api.analyze("アメリカ大使館：港区赤坂1-10-5") の結果として
得られるラティス表現の構造のイメージ ::

  [
    [ アメリカ大使館 ],
    [ ： ],
    [ 港区（市区町村・東京都）, 港区（市区町村・名古屋市）, 港区（市区町村・大阪市） ],
    [ 赤坂（駅・上毛電気鉄道／上毛線）, 赤坂（駅・東京メトロ／千代田線）, 
      赤坂（駅・富士急行／大月線）, 赤坂（駅・福岡市営地下鉄／空港線）],
    [ 1 ],
    [ - ],
    [ 10 ],
    [ - ],
    [ 5 ]
  ]

解析結果は 9 個の形態素からなり、3 番目の「港区」の形態素には
3 個の候補が、4 番目の「赤坂」の形態素には 4 個の候補があります。

**簡易表示**

ラティス表現は `api.devtool.pp_lattice() <pygeonlp.api.devtool.html#pygeonlp.api.devtool.pp_lattice>`_ を利用して
簡易表示することができます。以降の例ではこの簡易表示を利用します。 ::

  >>> import pygeonlp.api as api
  >>> from pygeonlp.api.devtool import pp_lattice
  >>> api.init()
  >>> lattice = api.analyze('アメリカ大使館：港区赤坂1-10-5')
  >>> pp_lattice(lattice)
  #0:'アメリカ大使館'
    アメリカ大使館(NORMAL)
  #1:'：'
    ：(NORMAL)
  #2:'港区'
    港区(GEOWORD:['東京都'])
    港区(GEOWORD:['愛知県', '名古屋市'])
    港区(GEOWORD:['大阪府', '大阪市'])
  #3:'赤坂'
    赤坂(GEOWORD:['上毛電気鉄道', '上毛線'])
    赤坂(GEOWORD:['東京地下鉄', '9号線千代田線'])
    赤坂(GEOWORD:['富士急行', '大月線'])
    赤坂(GEOWORD:['福岡市', '1号線(空港線)'])
  #4:'1'
    1(NORMAL)
  #5:'-'
    -(NORMAL)
  #6:'10'
    10(NORMAL)
  #7:'-'
    -(NORMAL)
  #8:'5'
    5(NORMAL)


**住所を含む場合**

住所解析を行なうと、住所候補を構成する形態素に含まれる
「住所以外の候補」は削除され、住所ノードに統合されます。

例： api.analyze("アメリカ大使館：港区赤坂1-10-5", jageocoder=jageocoder) ::

  #0:'アメリカ大使館'
    アメリカ大使館(NORMAL)
  #1:'：'
    ：(NORMAL)
  #2:'港区赤坂1-10-'
    港区赤坂1-10-(ADDRESS:東京都/港区/赤坂/一丁目/10番)[6]
  #3:'5'
    5(NORMAL)

住所以外の候補も残したい場合は ``keep_nodes=True`` を指定します。
この場合、住所に該当する先頭の形態素に住所ノードが追加されます。

例： api.analyze("アメリカ大使館：港区赤坂1-10-5", jageocoder=jageocoder, keep_nodes=True) ::

  #0:'アメリカ大使館'
    アメリカ大使館(NORMAL)
  #1:'：'
    ：(NORMAL)
  #2:'港区'
    港区(GEOWORD:['東京都'])
    港区(GEOWORD:['愛知県', '名古屋市'])
    港区(GEOWORD:['大阪府', '大阪市'])
    港区赤坂1-10-(ADDRESS:東京都/港区/赤坂/一丁目/10番)[6]
  #3:'赤坂'
    赤坂(GEOWORD:['上毛電気鉄道', '上毛線'])
    赤坂(GEOWORD:['東京地下鉄', '9号線千代田線'])
    赤坂(GEOWORD:['富士急行', '大月線'])
    赤坂(GEOWORD:['福岡市', '1号線(空港線)'])
  #4:'1'
    1(NORMAL)
  #5:'-'
    -(NORMAL)
  #6:'10'
    10(NORMAL)
  #7:'-'
    -(NORMAL)
  #8:'5'
    5(NORMAL)


.. _pygeonlp_terms_path_format:

パス表現
--------

パス表現は、地名解析処理で、最後のスコアリングと結果の出力の際に利用する
内部データ表現です。

テキストを形態素に分解し、それぞれの形態素に対する候補から
1つずつ選択した `Node <pygeonlp.api.node.html#pygeonlp.api.node.Node>`_ 
オブジェクトのリスト構造です。

`pygeonlp.api.linker.LinkedResults <pygeonlp.api.linker.html#pygeonlp.api.linker.LinkedResults>`_
ジェネレータクラスを利用すると、ラティス表現からパス表現の候補を
一つずつ取得することができます。

例： next(LinkedResults(api.analyze('アメリカ大使館：港区赤坂1-10-5'))) 
の結果として得られるパス表現の構造のイメージ ::

  [
    アメリカ大使館,
    ：,
    港区（市区町村・東京都）,
    赤坂（駅・上毛電気鉄道／上毛線）,
    1,
    -,
    10,
    -,
    5
  ]

このセンテンスを解析すると「港区」の候補が 3 個、「赤坂」の候補が
4 個存在するため、 3×4 = 12 個のパス表現が得られます。

**簡易表示**

パス表現は `api.devtool.pp_path() <pygeonlp.api.devtool.html#pygeonlp.api.devtool.pp_path>`_ を利用して
簡易表示することができます。以降の例ではこの簡易表示を利用します。 ::

  >>> import pygeonlp.api as api
  >>> from pygeonlp.api.linker import LinkedResults
  >>> from pygeonlp.api.devtool import pp_path
  >>> api.init()
  >>> lattice = api.analyze('アメリカ大使館：港区赤坂1-10-5')
  >>> pp_path(next(LinkedResults(lattice)))
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['東京都'])
    #3:赤坂(GEOWORD:['上毛電気鉄道', '上毛線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]

**住所を含む場合**

住所ノードを含むラティス表現からパス表現を生成する場合、
住所ノードが複数の形態素にまたがるため、次のノードを正しく
選択する必要があります。

LinkedResults はこの処理を自動的に行ないます。 ::

  >>> import jageocoder
  >>> jageocoder.init()
  >>> import pygeonlp.api as api
  >>> from pygeonlp.api.linker import LinkedResults
  >>> from pygeonlp.api.devtool import pp_lattice, pp_path
  >>> api.init()
  >>> lattice = api.analyze('アメリカ大使館：港区赤坂1-10-5', jageocoder=jageocoder, keep_nodes=True)
  >>> for path in LinkedResults(lattice):
  ...   pp_path(path)
  ...
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['東京都'])
    #3:赤坂(GEOWORD:['上毛電気鉄道', '上毛線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['東京都'])
    #3:赤坂(GEOWORD:['東京地下鉄', '9号線千代田線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['東京都'])
    #3:赤坂(GEOWORD:['富士急行', '大月線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['東京都'])
    #3:赤坂(GEOWORD:['福岡市', '1号線(空港線)'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['愛知県', '名古屋市'])
    #3:赤坂(GEOWORD:['上毛電気鉄道', '上毛線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['愛知県', '名古屋市'])
    #3:赤坂(GEOWORD:['東京地下鉄', '9号線千代田線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['愛知県', '名古屋市'])
    #3:赤坂(GEOWORD:['富士急行', '大月線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['愛知県', '名古屋市'])
    #3:赤坂(GEOWORD:['福岡市', '1号線(空港線)'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['大阪府', '大阪市'])
    #3:赤坂(GEOWORD:['上毛電気鉄道', '上毛線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['大阪府', '大阪市'])
    #3:赤坂(GEOWORD:['東京地下鉄', '9号線千代田線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['大阪府', '大阪市'])
    #3:赤坂(GEOWORD:['富士急行', '大月線'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区(GEOWORD:['大阪府', '大阪市'])
    #3:赤坂(GEOWORD:['福岡市', '1号線(空港線)'])
    #4:1(NORMAL)
    #5:-(NORMAL)
    #6:10(NORMAL)
    #7:-(NORMAL)
    #8:5(NORMAL)
  ]
  [
    #0:アメリカ大使館(NORMAL)
    #1:：(NORMAL)
    #2:港区赤坂1-10-(ADDRESS:東京都/港区/赤坂/一丁目/10番)[6]
    #3:5(NORMAL)
  ]

pygeonlp の地名解決処理では、パス表現ごとのスコアを
`pygeonlp.api.scoring.ScoringClass.path_score() <pygeonlp.api.scoring.html#pygeonlp.api.scoring.ScoringClass.path_score>`_
で計算し、降順にソートして結果を返します。

パス表現のスコア計算方法をカスタマイズしたい場合は 
:ref:`tuning_scoring` を参照してください。