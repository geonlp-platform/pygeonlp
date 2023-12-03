.. _link_jageocoder:

住所ジオコーダー連携
====================

pygeonlp を住所ジオコーダー `jageocoder <https://pypi.org/project/jageocoder/>`_ と
連携することで、テキスト中の住所を地名語ではなく住所として認識できます。

jageocoder は pygeonlp をインストールすると自動的にインストールされますが、
住所辞書を設定しないと機能しません。
初回および pygeonlp をバージョンアップした場合は以下の手順で
jageocoder 用辞書データのダウンロードとインストールを行なってください。 ::

  $ python -m jageocoder install-dictionary

辞書データがインストールされていれば、住所ジオコーダーは自動的に利用されます。
何らかの理由で住所を解析したくない時は、 `init()` を呼びだす時に
``jageocoder`` オプションに False をセットしてください。

  pygeonlp v1.1 までは ``jageocoder`` オプションは `geoparse()` の
  パラメータでしたが、 v1.2 で `init()` のパラメータに変更になりました。

.. code-block :: plaintext

  >>> import pygeonlp.api as api
  >>> api.init(jageocoder=False)
  >>> api.geoparse('NIIは千代田区一ツ橋2-1-2にあります。')
  [{'type': 'Feature', 'geometry': None, 'properties': {'surface': 'NII', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '組織', 'subclass3': '*', 'surface': 'NII', 'yomi': ''}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'は', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}}}, {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.758148, 35.692332]}, 'properties': {'surface': '千代田区一ツ橋2-1-', 'node_type': 'ADDRESS', 'morphemes': [{'surface': '千代田区', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '千代田区', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'WWIY7G:千代田区', 'surface': '千代田区', 'yomi': ''}, 'geometry': {'type': 'Point', 'coordinates': [139.753634, 35.694003]}, 'prop': {'address': '東京都千代田区', 'body': '千代田', 'body_variants': '千代田', 'code': {}, 'countyname': '', 'countyname_variants': '', 'dictionary_id': 1, 'entry_id': '13101A1968', 'geolod_id': 'WWIY7G', 'hypernym': ['東京都'], 'latitude': '35.69400300', 'longitude': '139.75363400', 'ne_class': '市区町村', 'prefname': '東京都', 'prefname_variants': '東京都', 'source': '1/千代田区役所/千代田区九段南1-2-1/P34-14_13.xml', 'suffix': ['区'], 'valid_from': '', 'valid_to': '', 'dictionary_identifier': 'geonlp:geoshape-city'}}, {'surface': '一ツ橋', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '一ツ橋', 'pos': '名詞', 'prononciation': 'ヒトツバシ', 'subclass1': '固有名詞', 'subclass2': '地域', 'subclass3': '一般', 'surface': '一ツ橋', 'yomi': 'ヒトツバシ'}, 'geometry': None, 'prop': None}, {'surface': '2', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '数', 'subclass2': '*', 'subclass3': '*', 'surface': '2', 'yomi': ''}, 'geometry': None, 'prop': None}, {'surface': '-', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': 'サ変接続', 'subclass2': '*', 'subclass3': '*', 'surface': '-', 'yomi': ''}, 'geometry': None, 'prop': None}, {'surface': '1', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '数', 'subclass2': '*', 'subclass3': '*', 'surface': '1', 'yomi': ''}, 'geometry': None, 'prop': None}, {'surface': '-', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': 'サ変接続', 'subclass2': '*', 'subclass3': '*', 'surface': '-', 'yomi': ''}, 'geometry': None, 'prop': None}], 'address_properties': {'id': 11460296, 'name': '1番', 'x': 139.758148, 'y': 35.692332, 'level': 7, 'note': None, 'fullname': ['東京都', '千代田区', '一ツ橋', '二丁目', '1番']}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '2', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '数', 'subclass2': '*', 'subclass3': '*', 'surface': '2', 'yomi': ''}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'に', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'に', 'pos': '助詞', 'prononciation': 'ニ', 'subclass1': '格助詞', 'subclass2': '一般', 'subclass3': '*', 'surface': 'に', 'yomi': 'ニ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'あり', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '五段・ラ行', 'conjugation_type': '連用形', 'original_form': 'ある', 'pos': '動詞', 'prononciation': 'アリ', 'subclass1': '自立', 'subclass2': '*', 'subclass3': '*', 'surface': 'あり', 'yomi': 'アリ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'ます', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '特殊・マス', 'conjugation_type': '基本形', 'original_form': 'ます', 'pos': '助動詞', 'prononciation': 'マス', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'ます', 'yomi': 'マス'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '。', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}}}]

このサンプルコードは以下の処理を行ないます。

1. `pygeonlp.api パッケージ <pygeonlp.api.html>`_ を import します。
2. `api.init() <pygeonlp.api.html#pygeonlp.api.init>`_ を呼んで pygeonlp.api を利用可能にします。

   ``jageocoder`` パラメータが省略された場合、または None か True が指定されていると、
   地名語を抽出した後で住所文字列の可能性がある部分をジオコーダーで
   確認し、住所として解析できれば住所ノードとして返します。

   上の例では False を指定しているため、住所の解析を行ないません。

3. `api.geoparse() <pygeonlp.api.html#pygeonlp.api.geoparse>`_ を 実行します。

住所ノードは ``node_type`` が ADDRESS になります。
また、住所ノードは地名語ノードと同じように、 JSON エンコードすれば
GeoJSON Feature オブジェクトになります。

住所辞書がインストールされていない時に ``jageocoder=True`` を指定すると、
ParseError 例外が発生します。住所解析が必須の場合には True を、
どちらでも構わない場合は ``jageocoder`` パラメータを省略してください。

処理中に切り替えたい場合
------------------------

処理中にジオコーダーの利用をオン・オフしたい場合は、
次のように切り替えることができます。

**住所解析を行ないたい場合** ::
  >>> api.default_workflow().parser.set_jageocoder(True)

**住所解析を行ないたくない場合** ::
  >>> api.default_workflow().parser.set_jageocoder(False)
