import json
import logging
import os
import unittest

import jageocoder

import pygeonlp.api as api
from pygeonlp.api.node import Node


logger = logging.getLogger(__name__)

"""
jageocoder を利用するテスト。

このモジュールのテストを行なうには、次のコマンドを実行してください。

python -m unittest -v pygeonlp.tests.test_api_geocoder
"""


class TestModuleMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create test database
        testdir = os.path.abspath(os.path.join(os.getcwd(), 'apitest'))
        os.environ['GEONLP_DB_DIR'] = testdir
        os.makedirs(testdir, 0o755, exist_ok=True)
        api.setup_basic_database(db_dir=testdir)
        api.init(db_dir=testdir)

        # Initialize jageocoder
        jageocoder_db_dir = jageocoder.get_db_dir(mode='r')
        if jageocoder_db_dir:
            cls.parser = api.parser.Parser(jageocoder=True)
        else:
            cls.parser = None

    def setUp(self):
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
        self.assertEqual(lattice_address[0][0].surface, '千代田区一ツ橋2-1-')

        # 内部の形態素を確認
        answer = ['千代田区', '一ツ橋', '2', '-', '1', '-']
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
        # 「寺山町」が MeCab の結果通り、住所要素の区切りと一致しない
        answer = ['横浜市', '緑区', '寺山', '町', '118', '番地']
        inner_morphemes = lattice_address[0][0].morphemes
        self.assertEqual(len(inner_morphemes), len(answer))
        for i, node in enumerate(inner_morphemes):
            self.assertIsInstance(node, Node)
            self.assertEqual(node.surface, answer[i])

        # '緑区' が '横浜市緑区' に解決されていることを確認
        midoriku = inner_morphemes[1]
        self.assertIn('横浜市', midoriku.prop['hypernym'])

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

        # '緑区' が '千葉市緑区' に解決されていることを確認
        inner_morphemes = lattice_address[0][0].morphemes
        midoriku = inner_morphemes[0]
        self.assertIn('千葉市', midoriku.prop['hypernym'])

    def test_geoparse_result(self):
        """
        住所を含む文の解析を geoparse() で実行した結果を確認する。
        """
        answer = [
            {"surface": "NII", "node_type": "NORMAL"},
            {"surface": "は", "node_type": "NORMAL"},
            {"surface": "千代田区一ツ橋2-1-", "node_type": "ADDRESS"},
            {"surface": "2", "node_type": "NORMAL"},
            {"surface": "に", "node_type": "NORMAL"},
            {"surface": "あり", "node_type": "NORMAL"},
            {"surface": "ます", "node_type": "NORMAL"},
            {"surface": "。", "node_type": "NORMAL"},
        ]
        result = self.parser.geoparse('NIIは千代田区一ツ橋2-1-2にあります。')
        for i, feature in enumerate(result):
            prop = feature['properties']
            self.assertEqual(prop['surface'], answer[i]['surface'])
            self.assertEqual(prop['node_type'], answer[i]['node_type'])
