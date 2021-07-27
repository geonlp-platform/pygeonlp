.. _tune_analysis:

解析方法のチューニング
======================

解析結果に含まれる地名語が想定と異なる場合、解析方法をチューニングする
必要があります。

想定した地名語が得られないのは、そもそもその地名語がデータベースに
登録されていない場合と、表記が同じ別の地名語が採用されている
（＝地名解決処理が失敗している）場合の二通りがあります。

地名語がデータベースに登録されていない場合は、その地名語が含まれている
地名解析辞書を作成するかウェブから取得し、
`addDictionaryFromFile() <pygeonlp.api.html#pygeonlp.api.addDictionaryFromFile>`_
および
`addDictionaryFromWeb() <pygeonlp.api.html#pygeonlp.api.addDictionaryFromWeb>`_
を使ってデータベースに登録してください。

ここでは地名解決処理が失敗してしまう場合に、処理精度を改善する方法を説明します。

解析対象とする地名解析辞書・固有名クラスの指定
----------------------------------------------

市区町村名だけを抽出したいのに駅名が抽出されてしまうといった場合、
`disactivateDictionaries() <pygeonlp.api.html#pygeonlp.api.disactivateDictionaries>`_
を実行することで、一時的に特定の地名解析辞書を利用しないように
設定することができます。

例：「和歌山市」のつもりが「和歌山市駅」が抽出されてしまう。 ::

  >>> import pygeonlp.api as api
  >>> api.init()
  >>> api.geoparse('和歌山市は晴れ')
  [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [135.16538500000001, 34.23604]}, 'properties': {'surface': '和歌山市', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '和歌山市', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'OciY0C:和歌山市駅', 'surface': '和歌山市', 'yomi': ''}, 'geoword_properties': {'body': '和歌山市', 'dictionary_id': 3, 'entry_id': 'adeb575da6e2879b67c9b76d269333e6', 'geolod_id': 'OciY0C', 'hypernym': ['南海電気鉄道', '和歌山港線'], 'institution_type': '民営鉄道', 'latitude': '34.23604', 'longitude': '135.16538500000001', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}}, ... ]

次のコードでは、辞書の identifier に ``station`` を含むものを
一時的に利用しないように指定します。
その結果 ``geonlp:ksj-station-N02-2019`` が利用できなくなるので、和歌山市駅が候補から除外されます。

  >>> import pygeonlp.api as api
  >>> api.init()
  >>> api.disactivateDictionaries(pattern=r'station')
  >>> api.geoparse('和歌山市は晴れ。')
  [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [135.170808, 34.230514]}, 'properties': {'surface': '和歌山市', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '和歌山市', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'lQccqK:和歌山市', 'surface': '和歌山市', 'yomi': ''}, 'geoword_properties': {'address': '和歌山県和歌山市', 'body': '和歌山', 'body_variants': '和歌山', 'code': {}, 'countyname': '', 'countyname_variants': '', 'dictionary_id': 1, 'entry_id': '30201A1968', 'geolod_id': 'lQccqK', 'hypernym': ['和歌山県'], 'latitude': '34.23051400', 'longitude': '135.17080800', 'ne_class': '市区町村', 'prefname': '和歌山県', 'prefname_variants': '和歌山県', 'source': '1/和歌山市役所/和歌山市七番丁23/P34-14_30.xml', 'suffix': ['市'], 'valid_from': '1889-04-01', 'valid_to': '', 'dictionary_identifier': 'geonlp:geoshape-city'}}}, ... ]

辞書ごと対象から除外する代わりに、
`setActiveClasses() <pygeonlp.api.html#pygeonlp.api.setActiveClasses>`_
で対象とする固有名クラスを指定することで、クラス単位で抽出対象を
限定することもできます。

次のコードでは全ての固有名クラス(``r'.*'``)から鉄道施設を除外(``r'-鉄道施設/.*'``)した
クラスを抽出対象にすることで、和歌山市駅を候補から除外します。 ::

  >>> import pygeonlp.api as api
  >>> api.init()
  >>> api.setActiveClasses(patterns=[r'.*', r'-鉄道施設/.*'])
  >>> api.geoparse('和歌山市は晴れ。')
  [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [135.170808, 34.230514]}, 'properties': {'surface': '和歌山市', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '和歌山市', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'lQccqK:和歌山市', 'surface': '和歌山市', 'yomi': ''}, 'geoword_properties': {'address': '和歌山県和歌山市', 'body': '和歌山', 'body_variants': '和歌山', 'code': {}, 'countyname': '', 'countyname_variants': '', 'dictionary_id': 1, 'entry_id': '30201A1968', 'geolod_id': 'lQccqK', 'hypernym': ['和歌山県'], 'latitude': '34.23051400', 'longitude': '135.17080800', 'ne_class': '市区町村', 'prefname': '和歌山県', 'prefname_variants': '和歌山県', 'source': '1/和歌山市役所/和歌山市七番丁23/P34-14_30.xml', 'suffix': ['市'], 'valid_from': '1889-04-01', 'valid_to': '', 'dictionary_identifier': 'geonlp:geoshape-city'}}}, ... ]


地名語抽出ルールの変更
----------------------

地名語抽出ルールは `init() <pygeonlp.api.html#pygeonlp.api.init>`_ 
実行時のオプションパラメータの一つで、形態素解析レベルの処理ルールを
細かく設定します。一度設定したルールは再び init() を呼ぶまで変更できません。
地名語抽出ルールについては init() のメモの欄を参照してください。

地名語抽出ルールはほとんどの場合は変更する必要がありませんが、
``excluded_word`` オプションは単純で、場合によっては効果的です。
このオプションは、指定した地名語を地名語として抽出しないようにします。

例： 「甲子園」は全国高校野球大会の意味なのに駅名として抽出されてしまう。 ::

  >>> import pygeonlp.api as api
  >>> api.init()
  >>> api.geoparse('甲子園に行こう')
  [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [135.363275, 34.723960000000005]}, 'properties': {'surface': '甲子園', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '', 'conjugation_type': '*', 'original_form': '甲子園', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'M4C8N9:甲子園駅', 'surface': '甲子園', 'yomi': ''}, 'geoword_properties': {'body': '甲子園', 'dictionary_id': 3, 'entry_id': '2670a9643e77eebd8397a3236ff90514', 'geolod_id': 'M4C8N9', 'hypernym': ['阪神電気鉄道', '本線'], 'institution_type': '民営鉄道', 'latitude': '34.723960000000005', 'longitude': '135.363275', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}},  ... ]

次のコードでは ``excluded_word`` に「甲子園」を指定して、地名語ではなく
固有名詞として抽出します。

  >>> import pygeonlp.api as api
  >>> api.init(geoword_rules={'excluded_word':['甲子園']})
  >>> api.geoparse('甲子園に行こう')
  [{'type': 'Feature', 'geometry': None, 'properties': {'surface': '甲子園', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '甲子園', 'pos': '名詞', 'prononciation': 'コーシエン', 'subclass1': '固有名詞', 'subclass2': '地域', 'subclass3': '一般', 'surface': '甲子園', 'yomi': 'コウシエン'}}}, ... ]


フィルタの利用
--------------

対象としているテキストの時間的範囲や空間的範囲が限定されている場合
（たとえば東京都内であることが分かっている場合など）は、抽出された地名語候補に
`フィルタ <pygeonlp.api.filter.html#module-pygeonlp.api.filter>`_
を適用して範囲外の候補を除去することができます。

例：東京の「府中駅」のつもりが京都府の天橋立近くの「府中駅」になってしまう。 ::

  >>> import pygeonlp.api as api
  >>> api.init()
  >>> api.geoparse('府中に行きます')
  [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [135.195275, 35.583365]}, 'properties': {'surface': '府中', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '', 'conjugation_type': '*', 'original_form': '府中', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'Auq8Kv:府中駅', 'surface': '府中', 'yomi': ''}, 'geoword_properties': {'body': '府中', 'dictionary_id': 3, 'entry_id': 'ecabefc60f23d0442029793c6eab81d0', 'geolod_id': 'Auq8Kv', 'hypernym': ['丹後海陸交通', '天橋立鋼索鉄道'], 'institution_type': '民営鉄道', 'latitude': '35.583365', 'longitude': '135.195275', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '鋼索鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'に', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'に', 'pos': '助詞', 'prononciation': 'ニ', 'subclass1': '格助詞', 'subclass2': '一般', 'subclass3': '*', 'surface': 'に', 'yomi': 'ニ'}}}, ... ]

次のコードでは、東京都付近の四角形内に空間範囲を限定する
`GeoContainsFilter <pygeonlp.api.spatial_filter.html#pygeonlp.api.spatial_filter.GeoContainsFilter>`_
を適用することで、その外側にある京都府の府中駅を候補から除外し、
東京都の府中駅を抽出します。 ::

  >>> import pygeonlp.api as api
  >>> from pygeonlp.api.spatial_filter import GeoContainsFilter
  >>> api.init()
  >>> gcfilter = GeoContainsFilter({"type":"Polygon","coordinates":[[[139.43,35.54],[139.91,35.54],[139.91,35.83],[139.43,35.83],[139.43,35.54]]]})
  >>> api.geoparse('府中に行きます', filters=[gcfilter])
  [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.4801, 35.67219]}, 'properties': {'surface': '府中', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '', 'conjugation_type': '*', 'original_form': '府中', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'JQSUIi:府中駅', 'surface': '府中', 'yomi': ''}, 'geoword_properties': {'body': '府中', 'dictionary_id': 3, 'entry_id': 'd7596c3444b3632f5236ae9e3168bab9', 'geolod_id': 'JQSUIi', 'hypernym': ['京王電鉄', '京王線'], 'institution_type': '民営鉄道', 'latitude': '35.67219', 'longitude': '139.4801', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'に', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'に', 'pos': '助詞', 'prononciation': 'ニ', 'subclass1': '格助詞', 'subclass2': '一般', 'subclass3': '*', 'surface': 'に', 'yomi': 'ニ'}}}, ... ]

フィルタはいくつでも指定できますが、複数のフィルタを指定した場合には
全てのフィルタを通過する地名語だけが残ります（AND条件）。

.. _tuning_scoring :

スコアリング方法のカスタマイズ
------------------------------

上述の方法は、特定の条件に合わせて個別に対応する方法です。

個別対応ではなく、組み込みの地名語選択ロジックの代わりに
独自のロジックで地名語を選択したい場合には、

- パスに対するスコアを計算する関数 ``path_score()``
- ノード間の関係によるスコアを計算する関数 ``node_relation_score()``

を持つスコアリングクラス 
`pygeonlp.api.scoring.ScoringClass <pygeonlp.api.scoring.html#pygeonlp.api.scoring.ScoringClass>`_
からサブクラスを派生し、
`geoparse() <pygeonlp.api.html#pygeonlp.api.geoparse>`_ の
オプションパラメータ ``scoring_class`` でクラス名を指定してください。
スコアリングクラスの実装については ``pygeonlp.api.scoring.ScoringClass`` が
サンプル実装となっていますので参考にしてください。

スコアを計算する関数に拡張パラメータを渡したい場合は、 ``geoparse()`` の
オプションパラメータ ``scoring_options`` に任意の型の値を指定します。
この値はスコアリングクラスのメンバ変数 ``options`` に格納されますので、
ノード間のスコアを計算する関数 `node_relation_score() <pygeonlp.api.scoring.html#pygeonlp.api.scoring.ScoringClass.node_relation_score>`_
およびパスのスコアを計算する関数 `path_score() <pygeonlp.api.scoring.html#pygeonlp.api.scoring.ScoringClass.path_score>`_
の中で ``self.options`` を参照して利用してください。

一例として、指定した固有名クラスの数をスコアとして返す単純なスコアリングクラスを
定義し、そのスコアリングクラスを利用して geoparse の結果を表示するコードを示します。

.. code-block:: python

  import pygeonlp.api as api
  from pygeonlp.api.linker import RankedResults
  from pygeonlp.api.scoring import ScoringClass

  api.init()


  class MyScoringClass(ScoringClass):

      def path_score(self, path):
          """
          パスの中に指定した文字列で始まる固有名クラスの地名語が
          存在する数をスコアとして返すスコアリングメソッド。

          Parameters
          ----------
          path : list of Node
              解析結果候補のパス表現。
          self.options : str
              カウントする固有名クラスの先頭文字列

          Returns
          -------
          int
              target_class にマッチする固有名クラスを持つ地名語数。
          """
          if not isinstance(self.options, str):
              raise RuntimeError(
                  "オプションパラメータは文字列で指定してください。")

          target_class = self.options
          score = 0
          geowords = RankedResults.collect_geowords(path)
          for geoword in geowords:
              if geoword.prop['ne_class'].startswith(target_class):
                  score += 1

          return score


  if __name__ == '__main__':
      print("'鉄道施設' が多い候補を優先した場合。")
      print(api.geoparse(
          '和歌山市は晴れ。',
          scoring_class=MyScoringClass, scoring_options='鉄道施設', ))
      print("'市区町村' が多い候補を優先した場合。")
      print(api.geoparse(
          '和歌山市は晴れ。',
          scoring_class=MyScoringClass, scoring_options='市区町村'))

実行結果は次のようになります。 ::

  $ python myscore.py
  '鉄道施設' が多い候補を優先した場合。
  [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [135.16538500000001, 34.23604]}, 'properties': {'surface': '和歌山市', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '和歌山市', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'OciY0C:和歌山市駅', 'surface': '和歌山市', 'yomi': ''}, 'geoword_properties': {'body': '和歌山市', 'dictionary_id': 3, 'entry_id': 'adeb575da6e2879b67c9b76d269333e6', 'geolod_id': 'OciY0C', 'hypernym': ['南海電気鉄道', '和歌山港線'], 'institution_type': '民営鉄道', 'latitude': '34.23604', 'longitude': '135.16538500000001', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'は', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '晴れ', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '晴れ', 'pos': '名詞', 'prononciation': 'ハレ', 'subclass1': '一般', 'subclass2': '*', 'subclass3': '*', 'surface': '晴れ', 'yomi': 'ハレ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '。', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}}}]
  '市区町村' が多い候補を優先した場合。
  [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [135.170808, 34.230514]}, 'properties': {'surface': '和歌山市', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '和歌山市', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'lQccqK:和歌山市', 'surface': '和歌山市', 'yomi': ''}, 'geoword_properties': {'address': '和歌山県和歌山市', 'body': '和歌山', 'body_variants': '和歌山', 'code': {}, 'countyname': '', 'countyname_variants': '', 'dictionary_id': 1, 'entry_id': '30201A1968', 'geolod_id': 'lQccqK', 'hypernym': ['和歌山県'], 'latitude': '34.23051400', 'longitude': '135.17080800', 'ne_class': '市区町村', 'prefname': '和歌山県', 'prefname_variants': '和歌山県', 'source': '1/和歌山市役所/和歌山市七番丁23/P34-14_30.xml', 'suffix': ['市'], 'valid_from': '1889-04-01', 'valid_to': '', 'dictionary_identifier': 'geonlp:geoshape-city'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'は', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '晴れ', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '晴れ', 'pos': '名詞', 'prononciation': 'ハレ', 'subclass1': '一般', 'subclass2': '*', 'subclass3': '*', 'surface': '晴れ', 'yomi': 'ハレ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '。', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}}}]
