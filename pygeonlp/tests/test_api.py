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

    def setUp(self):
        testdir = os.path.abspath(os.path.join(os.getcwd(), 'apitest'))
        os.environ['GEONLP_DB_DIR'] = testdir
        os.makedirs(testdir, 0o755, exist_ok=True)
        api.setup_basic_database(db_dir=testdir)
        api.init(db_dir=testdir)

    def test_search_word(self):
        words = api.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertIn('AGGwyc', words)  # 新宿線神保町駅

    def test_set_dictionaries(self):
        # Set active dictionaries and check the results
        api.setActiveDictionaries(pattern=r'.*')
        words = api.searchWord('和歌山市')
        self.assertIsInstance(words, dict)
        self.assertEqual(len(words.keys()), 4)

        # Disactivate all dictionaries
        api.disactivateDictionaries(pattern=r'.*')
        words = api.searchWord('和歌山市')
        self.assertIsInstance(words, dict)
        self.assertEqual(len(words.keys()), 0)

    def test_set_active_classes(self):
        # Set active classes and check the results
        classes = [".*", "-鉄道施設/.*"]
        api.setActiveClasses(classes)
        words = api.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertNotIn('AGGwyc', words)  # 新宿線神保町駅は鉄道施設

        # "鉄道施設/.*" は除外するが "駅$" は除外しない
        api.setActiveClasses([".*", "-鉄道施設/.*", r'.*駅$'])
        words = api.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertIn('AGGwyc', words)  # 新宿線神保町駅は鉄道駅

        # Reset active classes
        api.setActiveClasses()
        words = api.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertIn('AGGwyc', words)  # 新宿線神保町駅

    def test_geo_contains_filter(self):
        from pygeonlp.api.spatial_filter import SpatialFilter, GeoContainsFilter
        geojson = SpatialFilter.get_geometry(
            'https://geoshape.ex.nii.ac.jp/city/geojson/20200101/13/13208A1968.geojson').ExportToJson()
        gcfilter = GeoContainsFilter(geojson)
        result = api.geoparse('府中に行きます', filters=[gcfilter])
        self.assertEqual(result[0]['properties']['node_type'], 'GEOWORD')

    def test_geo_disjoint_filter(self):
        from pygeonlp.api.spatial_filter import SpatialFilter, GeoDisjointFilter
        geojson = SpatialFilter.get_geometry(
            'https://geoshape.ex.nii.ac.jp/city/geojson/20200101/13/13208A1968.geojson').ExportToJson()
        gcfilter = GeoDisjointFilter(geojson)
        result = api.geoparse('府中に行きます', filters=[gcfilter])
        self.assertEqual(result[0]['properties']['node_type'], 'GEOWORD')


if __name__ == '__main__':
    unittest.main()
