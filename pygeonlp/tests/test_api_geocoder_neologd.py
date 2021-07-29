import json
import logging
import os
import unittest

import jageocoder

import pygeonlp.api as api
from pygeonlp.api.node import Node


logger = logging.getLogger(__name__)

"""
jageocoder と NEologd を同時に利用する場合のテスト。
環境変数 NEOLOGD_DIC_DIR に NEologd のシステム辞書ディレクトリを
設定しておく必要があります。

このモジュールのテストを行なうには、次のコマンドを実行してください。

python -m unittest -v pygeonlp.tests.test_api_geocoder_neologd
"""


class TestModuleMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Check 'NEOLOGD_DIC_DIR'
        cls.neologd_dic_dir = os.environ.get('NEOLOGD_DIC_DIR', None)
        if cls.neologd_dic_dir is None:
            return

        # Create test database
        testdir = os.path.abspath(os.path.join(os.getcwd(), 'apitest'))
        os.environ['GEONLP_DB_DIR'] = testdir
        os.makedirs(testdir, 0o755, exist_ok=True)
        api.setup_basic_database(db_dir=testdir)
        api.init(db_dir=testdir, system_dic_dir=cls.neologd_dic_dir)

        # Initialize jageocoder
        jageocoder_db_dir = jageocoder.get_db_dir(mode='r')
        if jageocoder_db_dir:
            cls.parser = api.parser.Parser(jageocoder=True)
        else:
            cls.parser = None

    def setUp(self):
        if self.neologd_dic_dir is None:
            self.skipTest('環境変数 NEOLOGD_DIC_DIR が設定されていません。')

        self.parser = self.__class__.parser
        if self.parser is None:
            self.skipTest('住所辞書がインストールされていません。')

    def test_geoparse_with_address(self):
        """
        住所が正しく解析できることを確認する。
        """
        lattice = self.parser.analyze_sentence('千代田区一ツ橋2-1-2')
        lattice_address = self.parser.add_address_candidates(lattice)

        self.assertIsInstance(lattice_address, list)
        self.assertEqual(len(lattice_address), 2)
        self.assertEqual(len(lattice_address[0]), 1)
        self.assertIsInstance(lattice_address[0][0], Node)
        self.assertEqual(lattice_address[0][0].surface, '千代田区一ツ橋2-1')

        # 内部の形態素を確認
        answer = ['千代田区一ツ橋', '2', '-1']
        inner_morphemes = lattice_address[0][0].morphemes
        self.assertEqual(len(inner_morphemes), len(answer))
        for i, node in enumerate(inner_morphemes):
            self.assertIsInstance(node, Node)
            self.assertEqual(node.surface, answer[i])

    def test_geoparse_with_address_no_cutoff(self):
        """
        住所の解析の際に後方の語を途中で切断しないことを確認する。
        """
        lattice = self.parser.analyze_sentence('喜多方市三島町')
        lattice_address = self.parser.add_address_candidates(lattice)
        self.assertIsInstance(lattice_address, list)
        self.assertEqual(len(lattice_address), 2)
        self.assertEqual(lattice_address[0][0].surface, '喜多方市')
        self.assertEqual(lattice_address[1][0].surface, '三島町')

    def test_geoparse_location_disambiguation_hypernym(self):
        """
        住所内の地名語に複数の候補があるとき、
        上位の地名から正しい候補を選択できることを確認する。
        """
        lattice = self.parser.analyze_sentence('横浜市緑区寺山町118番地')
        lattice_address = self.parser.add_address_candidates(lattice)
        self.assertIsInstance(lattice_address, list)
        self.assertEqual(len(lattice_address), 1)
        self.assertEqual(len(lattice_address[0]), 1)
        self.assertIsInstance(lattice_address[0][0], Node)
        self.assertEqual(lattice_address[0][0].surface, '横浜市緑区寺山町118番地')

        # 内部の形態素を確認
        answer = ['横浜市緑区寺山町', '118番', '地']
        inner_morphemes = lattice_address[0][0].morphemes
        self.assertEqual(len(inner_morphemes), len(answer))
        for i, node in enumerate(inner_morphemes):
            self.assertIsInstance(node, Node)
            self.assertEqual(node.surface, answer[i])

    def test_geoparse_location_disambiguation_hyponym(self):
        """
        住所内の地名語に複数の候補があるとき、
        下位の地名から正しい候補を選択できることを確認する。
        """
        lattice = self.parser.analyze_sentence('緑区おゆみ野三丁目15番地3')
        lattice_address = self.parser.add_address_candidates(lattice)
        self.assertIsInstance(lattice_address, list)
        self.assertEqual(len(lattice_address), 2)
        self.assertEqual(len(lattice_address[0]), 1)
        self.assertIsInstance(lattice_address[0][0], Node)
        self.assertEqual(lattice_address[0][0].surface, '緑区おゆみ野三丁目15番地')

        # '緑区おゆみ野' は NEologd で固有名詞に結合されている
        inner_morphemes = lattice_address[0][0].morphemes
        midoriku_oyumino = inner_morphemes[0]
        self.assertEqual('固有名詞', midoriku_oyumino.morphemes['subclass1'])

    def test_geoparse_result(self):
        """
        住所を含む文の解析を geoparse() で実行した結果を確認する。
        """
        answer = [
            '{"type": "Feature", "geometry": null, "properties": {"surface": "NII", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "NII", "pos": "名詞", "prononciation": "エヌアイアイ", "subclass1": "固有名詞", "subclass2": "一般", "subclass3": "*", "surface": "NII", "yomi": "エヌアイアイ"}}}',
            '{"type": "Feature", "geometry": null, "properties": {"surface": "は", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "は", "pos": "助詞", "prononciation": "ワ", "subclass1": "係助詞", "subclass2": "*", "subclass3": "*", "surface": "は", "yomi": "ハ"}}}',
            '{"type": "Feature", "geometry": {"type": "Point", "coordinates": [139.758148, 35.692332]}, "properties": {"surface": "千代田区一ツ橋2-1", "node_type": "ADDRESS", "morphemes": [{"type": "Feature", "geometry": null, "properties": {"surface": "千代田区一ツ橋", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "千代田区一ツ橋", "pos": "名詞", "prononciation": "チヨダクヒトツバシ", "subclass1": "固有名詞", "subclass2": "地域", "subclass3": "一般", "surface": "千代田区一ツ橋", "yomi": "チヨダクヒトツバシ"}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "2", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "*", "pos": "名詞", "prononciation": "", "subclass1": "数", "subclass2": "*", "subclass3": "*", "surface": "2", "yomi": ""}}}, {"type": "Feature", "geometry": null, "properties": {"surface": "-1", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "−1", "pos": "名詞", "prononciation": "マイナスイチ", "subclass1": "固有名詞", "subclass2": "一般", "subclass3": "*", "surface": "-1", "yomi": "マイナスイチ"}}}], "address_properties": {"id": 11460296, "name": "1番", "x": 139.758148, "y": 35.692332, "level": 7, "note": null, "fullname": ["東京都", "千代田区", "一ツ橋", "二丁目", "1番"]}}}',
            '{"type": "Feature", "geometry": null, "properties": {"surface": "-2", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "−2", "pos": "名詞", "prononciation": "マイナスニ", "subclass1": "固有名詞", "subclass2": "一般", "subclass3": "*", "surface": "-2", "yomi": "マイナスニ"}}}',
            '{"type": "Feature", "geometry": null, "properties": {"surface": "に", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "に", "pos": "助詞", "prononciation": "ニ", "subclass1": "格助詞", "subclass2": "一般", "subclass3": "*", "surface": "に", "yomi": "ニ"}}}',
            '{"type": "Feature", "geometry": null, "properties": {"surface": "あり", "node_type": "NORMAL", "morphemes": {"conjugated_form": "五段・ラ行", "conjugation_type": "連用形", "original_form": "ある", "pos": "動詞", "prononciation": "アリ", "subclass1": "自立", "subclass2": "*", "subclass3": "*", "surface": "あり", "yomi": "アリ"}}}',
            '{"type": "Feature", "geometry": null, "properties": {"surface": "ます", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・マス", "conjugation_type": "基本形", "original_form": "ます", "pos": "助動詞", "prononciation": "マス", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "ます", "yomi": "マス"}}}',
            '{"type": "Feature", "geometry": null, "properties": {"surface": "。", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "。", "pos": "記号", "prononciation": "。", "subclass1": "句点", "subclass2": "*", "subclass3": "*", "surface": "。", "yomi": "。"}}}',
        ]
        result = self.parser.geoparse('NIIは千代田区一ツ橋2-1-2にあります。')
        for i, feature in enumerate(result):
            geojson = json.dumps(feature, ensure_ascii=False)
            self.assertEqual(geojson, answer[i])
