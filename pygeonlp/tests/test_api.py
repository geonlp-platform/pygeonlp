import logging
import os
import unittest

import pygeonlp.api as api

logger = logging.getLogger(__name__)


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
        self.assertIn('82wiE0', words)  # 新宿線神保町駅

    def test_set_active_classes(self):
        # Set active classes and check the results
        classes = [".*", "-鉄道施設/.*"]
        api.setActiveClasses(classes)
        words = api.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertNotIn('82wiE0', words)  # 新宿線神保町駅は鉄道施設

        # Reset active classes
        api.setActiveClasses()
        words = api.searchWord('神保町')
        self.assertIsInstance(words, dict)
        self.assertIn('82wiE0', words)  # 新宿線神保町駅


if __name__ == '__main__':
    unittest.main()
