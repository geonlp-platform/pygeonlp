.. _link_jageocoder:

住所ジオコーダー連携
====================

住所辞書データのインストール
----------------------------

pygeonlp を住所ジオコーダー `jageocoder <https://t-sagara.github.io/jageocoder/>`_ と
連携することで、テキスト中の住所を地名語ではなく住所として認識できます。

jageocoder の住所辞書はサイズが大きいため、 pygeonlp をインストールしても
自動的にはインストールされません。
住所を抽出したい場合は以下の手順で住所辞書をインストールしてください。

- 利用する住所辞書データをダウンロードする

  `Jageocoder データファイル一覧 <https://www.info-proto.com/static/jageocoder/latest/>`_
  に最新の住所辞書データがあります。利用したい辞書データ（zipファイル）を
  ダウンロードしてください。

- 住所辞書をインストールする

  ``jageocoder install-dictionary`` コマンドでダウンロードした辞書データを
  インストールします。 ::

    $ jageocoder install-dictionary <ダウンロードしたzipファイルのパス>

- 動作確認する

  ``pygeonlp geoparse`` で住所を含むテキストを解析し、住所部分が
  抽出されることを確認します。 ::

    $ echo "東京都庁は新宿区西新宿２－８にあります。" | pygeonlp geoparse
    東京    名詞,固有名詞,地名語,0q60k0:東京駅,*,,東京,トウキョウ,トウキョウ        鉄道施設/鉄道駅,0q60k0,東京駅,139.766685,35.680965
    都庁    名詞,一般,*,*,*,*,都庁,トチョウ,トチョー
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    新宿区西新宿２－８      名詞,固有名詞,住所,街区・地番,*,*,東京都新宿区西新宿二丁目8番,ニハチ,ニハチ     住所,,東京都新宿区西新宿二丁目8番,139.6917724609375,35.68962860107422
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS


一時的に住所を解析しない
------------------------

辞書データがインストールされていれば、住所ジオコーダーは自動的に利用されます。
何らかの理由で住所を解析したくない時は、環境変数 ``JAGEOCODER_DB2_DIR`` に
``false`` など **住所辞書をインストールしたディレクトリ名以外**
をセットしてください。 ::

  $ export JAGEOCODER_DB2_DIR=false
  $ echo "東京都庁は新宿区西新宿２－８にあります。" | pygeonlp geoparse
  東京    名詞,固有名詞,地名語,yaOcgu:東京駅,*,,東京,トウキョウ,トウキョウ        鉄道施設/鉄道駅,yaOcgu,東京駅,139.76479999999998,35.681934999999996
  都庁    名詞,一般,*,*,*,*,都庁,トチョウ,トチョー
  は      助詞,係助詞,*,*,*,*,は,ハ,ワ
  新宿区  名詞,固有名詞,地名語,5q2IUM:新宿区,*,*,新宿区,, 市区町村,5q2IUM,新宿区,139.70346300,35.69389000
  西新宿  名詞,固有名詞,地名語,ZgyYyS:西新宿駅,*,,西新宿,,        鉄道施設/鉄道駅,ZgyYyS,西新宿駅,139.69256000000001,35.694514999999996
  ２      名詞,数,*,*,*,*,２,ニ,ニ
  －      記号,一般,*,*,*,*,*,,
  ８      名詞,数,*,*,*,*,８,ハチ,ハチ
  に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
  あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
  ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
  。      記号,句点,*,*,*,*,。,。,。
  EOS

環境変数を使わずに Python API で実行時に住所辞書を使わないよう指定するには、
:py:meth:`pygeonlp.api.init` を呼びだす時に ``jageocoder`` オプションに
False をセットしてください。

.. code-block:: python

  >>> import pygeonlp.api as api
  >>> api.init(jageocoder=False)
  >>> api.geoparse('NIIは千代田区一ツ橋2-1-2にあります。')
  [{'type': 'Feature', 'geometry': None, 'properties': {'surface': 'NII', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '組織', 'subclass3': '*', 'surface': 'NII', 'yomi': ''}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'は', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'は', 'pos': '助詞', 'prononciation': 'ワ', 'subclass1': '係助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'は', 'yomi': 'ハ'}}}, {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.758148, 35.692332]}, 'properties': {'surface': '千代田区一ツ橋2-1-', 'node_type': 'ADDRESS', 'morphemes': [{'surface': '千代田区', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '千代田区', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'WWIY7G:千代田区', 'surface': '千代田区', 'yomi': ''}, 'geometry': {'type': 'Point', 'coordinates': [139.753634, 35.694003]}, 'prop': {'address': '東京都千代田区', 'body': '千代田', 'body_variants': '千代田', 'code': {}, 'countyname': '', 'countyname_variants': '', 'dictionary_id': 1, 'entry_id': '13101A1968', 'geolod_id': 'WWIY7G', 'hypernym': ['東京都'], 'latitude': '35.69400300', 'longitude': '139.75363400', 'ne_class': '市区町村', 'prefname': '東京都', 'prefname_variants': '東京都', 'source': '1/千代田区役所/千代田区九段南1-2-1/P34-14_13.xml', 'suffix': ['区'], 'valid_from': '', 'valid_to': '', 'dictionary_identifier': 'geonlp:geoshape-city'}}, {'surface': '一ツ橋', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '一ツ橋', 'pos': '名詞', 'prononciation': 'ヒトツバシ', 'subclass1': '固有名詞', 'subclass2': '地域', 'subclass3': '一般', 'surface': '一ツ橋', 'yomi': 'ヒトツバシ'}, 'geometry': None, 'prop': None}, {'surface': '2', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '数', 'subclass2': '*', 'subclass3': '*', 'surface': '2', 'yomi': ''}, 'geometry': None, 'prop': None}, {'surface': '-', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': 'サ変接続', 'subclass2': '*', 'subclass3': '*', 'surface': '-', 'yomi': ''}, 'geometry': None, 'prop': None}, {'surface': '1', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '数', 'subclass2': '*', 'subclass3': '*', 'surface': '1', 'yomi': ''}, 'geometry': None, 'prop': None}, {'surface': '-', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': 'サ変接続', 'subclass2': '*', 'subclass3': '*', 'surface': '-', 'yomi': ''}, 'geometry': None, 'prop': None}], 'address_properties': {'id': 11460296, 'name': '1番', 'x': 139.758148, 'y': 35.692332, 'level': 7, 'note': None, 'fullname': ['東京都', '千代田区', '一ツ橋', '二丁目', '1番']}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '2', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '*', 'pos': '名詞', 'prononciation': '', 'subclass1': '数', 'subclass2': '*', 'subclass3': '*', 'surface': '2', 'yomi': ''}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'に', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'に', 'pos': '助詞', 'prononciation': 'ニ', 'subclass1': '格助詞', 'subclass2': '一般', 'subclass3': '*', 'surface': 'に', 'yomi': 'ニ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'あり', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '五段・ラ行', 'conjugation_type': '連用形', 'original_form': 'ある', 'pos': '動詞', 'prononciation': 'アリ', 'subclass1': '自立', 'subclass2': '*', 'subclass3': '*', 'surface': 'あり', 'yomi': 'アリ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'ます', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '特殊・マス', 'conjugation_type': '基本形', 'original_form': 'ます', 'pos': '助動詞', 'prononciation': 'マス', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'ます', 'yomi': 'マス'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '。', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}}}]

このサンプルコードは以下の処理を行ないます。

1. :py:mod:`pygeonlp.api` モジュールを import します。
2. :py:meth:`pygeonlp.api.init` を呼んでデフォルトワークフローを初期化します。
3. :py:meth:`pygeonlp.api.geoparse` を実行します。

住所ノードは ``node_type`` が ADDRESS になります。
また、住所ノードは地名語ノードと同じように、 JSON エンコードすれば
GeoJSON Feature オブジェクトになります。

住所辞書がインストールされていない時に ``jageocoder=True`` を指定すると、
ParseError 例外が発生します。住所解析が必須の場合には True を、
どちらでも構わない場合は ``jageocoder`` パラメータを省略してください。

処理中に切り替えたい場合
------------------------

処理中にジオコーダーの利用をオン・オフしたい場合は、
次のように :py:class:`pygeonlp.api.parser.Parser` クラスの
:py:meth:`~pygeonlp.api.parser.Parser.set_jageocoder`
を直接呼び出して明示的に切り替えることもできます。

**住所解析を行ないたい場合** ::
  >>> api.default_workflow().parser.set_jageocoder(True)

**住所解析を行ないたくない場合** ::
  >>> api.default_workflow().parser.set_jageocoder(False)
