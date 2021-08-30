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
            {"surface": "NII", "node_type": "NORMAL"},
            {"surface": "は", "node_type": "NORMAL"},
            {"surface": "千代田区一ツ橋2-1", "node_type": "ADDRESS"},
            {"surface": "-2", "node_type": "NORMAL"},
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

    def test_geoparse_combined_address(self):
        """
        「多摩市落合1-15」の「多摩市落合」が一語として解析されるため
        地名語として抽出できない場合も住所として解析できることを確認する。
        """
        result = self.parser.geoparse('多摩市落合1-15-2')
        self.assertEqual(result[0]['properties']['surface'], '多摩市落合1-15')
        self.assertEqual(result[0]['properties']['node_type'], 'ADDRESS')

    def test_geoparse_combined_address_oneword(self):
        """
        「鹿児島県枕崎市」が一語として解析され、住所表記がそこで完了していても
        住所として解析できることを確認する。
        """
        result = self.parser.geoparse('鹿児島県枕崎市')
        self.assertEqual(result[0]['properties']['surface'], '鹿児島県枕崎市')
        self.assertEqual(result[0]['properties']['node_type'], 'ADDRESS')

    def test_ma_with_suffix_oneword(self):
        """
        「世田谷区内」のように1語として解析される語に対しても
        suffix（内）を除去した「世田谷区」が抽出できることを確認する。
        """
        nodes = api.ma_parseNode('世田谷区内の')
        self.assertEqual(nodes[1]['surface'], '世田谷区')
        self.assertEqual(nodes[1]['subclass2'], '地名語')
        self.assertEqual(nodes[2]['surface'], '内')
        self.assertEqual(nodes[2]['subclass1'], '接尾')

    def test_geoparse_combined_address_oneword(self):
        """
        「鹿児島県枕崎市」が一語として解析され、住所表記がそこで完了していても
        住所として解析できることを確認する。
        """
        result = self.parser.geoparse('鹿児島県枕崎市')
        self.assertEqual(result[0]['properties']['surface'], '鹿児島県枕崎市')
        self.assertEqual(result[0]['properties']['node_type'], 'ADDRESS')

    def test_geoparse_originalform_address(self):
        """
        「東京・世田谷区」の original_form 「東京都世田谷区」を利用して
        住所として解析できることを確認する。
        """
        result = self.parser.geoparse('東京・世田谷区')
        self.assertEqual(result[0]['properties']['surface'], '東京・世田谷区')
        self.assertEqual(result[0]['properties']['node_type'], 'ADDRESS')
        self.assertEqual(
            result[0]['properties']['address_properties']['fullname'],
            ['東京都', '世田谷区'])
