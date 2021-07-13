import logging
from multiprocessing import Process
import time
import unittest

from pygeonlp.api.node import Node
import pygeonlp.api as api

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)


def analyze(query):
    service = api.service.Service()
    parser = api.parser.Parser(service=service)
    while True:
        parser.analyze_sentence(query)


class TestMultiProcessing(unittest.TestCase):

    queries = [
        'NIIは千代田区一ツ橋2-1-2にあります。',
        ('東京都恩賜上野動物公園は東京都台東区上野公園の'
            '上野恩賜公園内に在る東京都立動物園。'),
        ('北海道大学（ほっかいどうだいがく、英語: Hokkaido University）は、'
            '札幌市北区北8西5に本部を置く日本の国立大学である。'),
        '2013年9月の第125次IOC総会で開催都市が東京に決定した。',
    ]

    def setUp(self):
        api.init()
        self.parser = api.parser.Parser()

    def test_single_process(self):
        """
        Test analyze in single process.

        "analyze_sentence" should return the result as follows:
        ['NII(NORMAL)']
        ['は(NORMAL)']
        ["千代田区(GEOWORD:['東京都'])"]
        ['一ツ橋(NORMAL)']
        ['2(NORMAL)']
        ['-(NORMAL)']
        ['1(NORMAL)']
        ['-(NORMAL)']
        ['2(NORMAL)']
        ['に(NORMAL)']
        ['あり(NORMAL)']
        ['ます(NORMAL)']
        ['。(NORMAL)']
        """
        query = self.__class__.queries[0]
        lattice = self.parser.analyze_sentence(query)

        self.assertEqual(len(lattice), 13)

        nodes = lattice[2]
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].node_type, Node.GEOWORD)

    def test_five_processes(self):
        """
        Test simultaneous analyzes in multi-processes.
        """

        processes = []
        for q in self.__class__.queries:
            p = Process(target=analyze, args=(q, ))
            p.start()
            processes.append(p)

        time.sleep(10)

        for p in processes:
            p.terminate()


if __name__ == '__main__':
    unittest.main()
