import logging
import os
import unittest

import pygeonlp.api as api

logger = logging.getLogger(__name__)

"""
doc_string に書くには複雑過ぎる API のテスト。

このモジュールのテストを行なうには、次のコマンドを実行してください。

python -m unittest -v pygeonlp.tests.test_api
"""


class TestModuleMethods(unittest.TestCase):

    service = api.service.Service()

    def setUp(self):
        testdir = os.path.abspath(os.path.join(os.getcwd(), 'apitest'))
        os.makedirs(testdir, 0o755, exist_ok=True)
        self.dictmanager = api.dict_manager.DictManager(db_dir=testdir)
        self.dictmanager.setupBasicDatabase()
        api.init(db_dir=testdir)

    def test_search_word(self):
        words = self.service.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertIn('uN6ecI', words)  # 新宿線神保町駅

    def test_set_dictionaries(self):
        # Set active dictionaries and check the results
        self.service.setActiveDictionaries(pattern=r'.*')
        words = self.service.searchWord('和歌山市')
        self.assertIsInstance(words, dict)
        self.assertEqual(len(words.keys()), 4)

        # Disactivate all dictionaries
        self.service.disactivateDictionaries(pattern=r'.*')
        words = self.service.searchWord('和歌山市')
        self.assertIsInstance(words, dict)
        self.assertEqual(len(words.keys()), 0)

    def test_set_active_classes(self):
        # Set active classes and check the results
        classes = [".*", "-鉄道施設/.*"]
        self.service.setActiveClasses(classes)
        words = self.service.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertNotIn('AGGwyc', words)  # 新宿線神保町駅は鉄道施設

        # "鉄道施設/.*" は除外するが "駅$" は除外しない
        self.service.setActiveClasses([".*", "-鉄道施設/.*", r'.*駅$'])
        words = self.service.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertIn('AGGwyc', words)  # 新宿線神保町駅は鉄道駅

        # Reset active classes
        api.setActiveClasses()
        words = self.service.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertIn('AGGwyc', words)  # 新宿線神保町駅

    def test_geo_contains_filter(self):
        from pygeonlp.api.spatial_filter import SpatialFilter, GeoContainsFilter
        geojson = SpatialFilter.get_geometry((
            'https://geoshape.ex.nii.ac.jp/city/geojson/'
            '20230101/13/13206A1968.geojson')).ExportToJson()
        gcfilter = GeoContainsFilter(geojson)
        api.default_workflow().filters = [gcfilter]
        results = api.geoparse('府中に行きます')
        self.assertEqual(results[0]['properties']['node_type'], 'GEOWORD')
        api.default_workflow().filters = []

    def test_geo_disjoint_filter(self):
        from pygeonlp.api.spatial_filter import SpatialFilter, GeoDisjointFilter
        geojson = SpatialFilter.get_geometry((
            'https://geoshape.ex.nii.ac.jp/city/geojson/'
            '20200101/13/13208A1968.geojson')).ExportToJson()
        gcfilter = GeoDisjointFilter(geojson)
        api.default_workflow().filters = [gcfilter]
        results = api.geoparse('府中に行きます')
        self.assertEqual(results[0]['properties']['node_type'], 'GEOWORD')
        api.default_workflow().filters = []

    def test_issue1(self):
        """
        RecursionError: maximum recursion depth exceeded
        """
        results = api.geoparse("第二希望：東京、静岡、三重、滋賀、大阪")
        self.assertEqual(len(results), 13)
        self.assertEqual(results[4]['properties']['node_type'], 'GEOWORD')

    def test_issue15(self):
        """
        「〇〇線××駅」を正しく解析できない
        """
        results = api.geoparse("高崎線上尾駅は埼玉県にあります。")
        self.assertEqual(results[0]['properties']['surface'], "高崎")
        self.assertEqual(results[1]['properties']['surface'], "線")
        self.assertEqual(results[2]['properties']['surface'], "上尾駅")


if __name__ == '__main__':
    unittest.main()
