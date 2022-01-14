import copy
import logging
import re

import jageocoder as _jageocoder
from jageocoder.itaiji import converter as itaiji_converter

from pygeonlp.api.parser import Parser
from pygeonlp.api.filter import EntityClassFilter, GreedySearchFilter
from pygeonlp.api.linker import Evaluator, MAX_COMBINATIONS
from pygeonlp.api.node import Node

logger = logging.getLogger(__name__)


class WorkflowError(RuntimeError):
    """
    ワークフロー処理の際に例外が起こると、このクラスが発生します。
    """
    pass


class Workflow(object):
    """
    一連のジオパース処理を行なうワークフロー。

    Attributes
    ----------
    service : pygeonlp.service.Service
        利用する Service インスタンス。
    jageocoder_tree : jageocoder.address.AddressTree
        住所ジオコーダー jageocoder の AddressTree インスタンス。
    address_regex : regex
        住所要素の先頭になりえる固有名クラスの正規表現（コンパイル済み）。
    scoring_class : class
        パスのスコアリングに利用するクラス。
    scoring_options : any
        スコアリングクラスを初期化する際のオプションパラメータ。
    scorer : service.ScoringClass instance
        スコアリングを行なうクラスインスタンス。
    """

    def __init__(self, db_dir=None, address_regex=None, jageocoder=None,
                 scoring_class=None, scoring_options=None, filters=None,
                 **options):
        """
        パーザを初期化します。

        Parameters
        ----------
        db_dir : PathLike, optional
            データベースディレクトリ。
            省略した場合は ``api.init.get_db_dir()`` が返す値を利用します。
        address_regex : str, optional
            住所表記の開始とみなす地名語の固有名クラスを表す正規表現。
            省略した場合、``r'^(都道府県|市区町村|行政地域|居住地名)(/.+|)'``
            を利用します。
        jageocoder : jageocoder.tree.AddressTree, optional
            利用する住所ジオコーダーを指定します。省略した場合、
            jageocoder モジュールのデフォルトオブジェクトを利用します。
            False を指定した場合、ジオコーディング機能を利用しません。
        scoring_class : class, optional
            パスのスコアとノード間のスコアを計算する関数を持つ
            スコアリングクラス。
            指定しない場合、``pygeonlp.api.scoring`` モジュール内の
            ``ScoringClass`` が利用されます。
        scoring_options : any, optional
            スコアリングクラスの初期化に渡すオプションパラメータ。
        filters: list
            適用するフィルタオブジェクトのリスト
        """
        self.parser = Parser(
            db_dir=db_dir,
            address_regex=address_regex,
            jageocoder=jageocoder, **options)
        self.evaluator = Evaluator(
            scoring_class=scoring_class,
            scoring_options=scoring_options,
            max_results=1, max_combinations=MAX_COMBINATIONS)
        self.filters = filters or []
        self.scoring_class = scoring_class
        self.scoring_options = scoring_options

    def geoparse(self, sentence):
        """
        文を解析して GeoJSON Feature 形式に変換可能な dict の
        リストを返します。

        Parameters
        ----------
        sentence: str
            解析する文字列

        Returns
        -------
        list
            GeoJSON Feature 形式に変換可能な dict のリスト。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> workflow = api.workflow.Workflow()
        >>> workflow.geoparse('国会議事堂前まで歩きました。')
        [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.74305333333334, 35.673543333333335]}, 'properties': {'surface': '国会議事堂前', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '国会議事堂前', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'cE8W4w:国会議事堂前駅', 'surface': '国会議事堂前', 'yomi': ''}, 'geoword_properties': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': '4NFELa', 'geolod_id': 'cE8W4w', 'hypernym': ['東京地下鉄', '9号線千代田線'], 'institution_type': '民営鉄道', 'latitude': '35.673543333333335', 'longitude': '139.74305333333334', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'まで', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'まで', 'pos': '助詞', 'prononciation': 'マデ', 'subclass1': '副助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'まで', 'yomi': 'マデ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '歩き', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '五段・カ行イ音便', 'conjugation_type': '連用形', 'original_form': '歩く', 'pos': '動詞', 'prononciation': 'アルキ', 'subclass1': '自立', 'subclass2': '*', 'subclass3': '*', 'surface': '歩き', 'yomi': 'アルキ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'まし', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '特殊・マス', 'conjugation_type': '連用形', 'original_form': 'ます', 'pos': '助動詞', 'prononciation': 'マシ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'まし', 'yomi': 'マシ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'た', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '特殊・タ', 'conjugation_type': '基本形', 'original_form': 'た', 'pos': '助動詞', 'prononciation': 'タ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'た', 'yomi': 'タ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '。', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}}}]

        Notes
        -----
        このメソッドは解析結果から適切なフィルタを判断し、
        候補の絞り込みやランキングを行ないます。
        """
        lattice = self.parser.analyze_sentence(sentence)

        # フィルタを適用
        filters = self.set_filters(lattice)
        for f in filters:
            lattice = f(lattice)

        # 住所候補を追加
        lattice = self.parser.add_address_candidates(lattice)

        # 処理可能な長さに分割したラティスをパス表現に変換
        results = []
        for lattice_part in self.get_processible_lattice_part(lattice):
            if len(lattice_part) < 1:
                continue    # 空行

            results += self.evaluator.get(lattice_part)

        features = []
        for result in results:
            nodes = result['result']
            for node in nodes:
                features.append(node.as_geojson())

        return features

    def set_filters(self, lattice):
        """
        利用するフィルタを決定します。

        カスタム Workflow クラスでは、対象とするテキストに応じて
        このメソッドを定義しなおしてください。
        self.filters だけを利用する場合は
        ``return self.filters`` で問題ありません。

        Parameters
        ----------
        lattice: list
            入力となるラティス表現。

        Returns
        -------
        list
            適用する Filter のリスト。

        Note
        ----
        汎用の Workflow では、地名が高い密度で出現する
        ケースに対応するため、地名語クラスの出現頻度によって
        絞り込みを行なう EntityClassFilter を追加します。
        """
        filters = self.filters.copy()

        search_plan = "exhaustive"
        gstat = Statistics.count_geowords(lattice)
        ne_classes = gstat['ne_classes']
        num_geowords = gstat['num_geowords']

        if num_geowords >= 5 and \
           ne_classes.get('都道府県', 0) / num_geowords >= 0.75:
            # 都道府県リスト
            filters.append(EntityClassFilter(r'都道府県/?.*'))
            search_plan = "greedy"
        elif num_geowords >= 5 and \
                ne_classes.get('市区町村', 0) / num_geowords >= 0.75:
            # 市区町村リスト
            filters.append(EntityClassFilter(r'(都道府県|市区町村)/?.*'))
            search_plan = "greedy"
        elif num_geowords >= 5 and \
                ne_classes.get('鉄道施設', 0) / num_geowords >= 0.75:
            # 鉄道駅リスト
            filters.append(EntityClassFilter(r'(市区町村|鉄道施設)/?.*'))
            search_plan = "greedy"

        if search_plan == "greedy":
            # 地震速報や時刻表など同種の地名語が多数出現する場合
            filters.append(GreedySearchFilter(
                scoring_class=self.scoring_class,
                scoring_options=self.scoring_options))

        return filters

    def get_processible_lattice_part(self, lattice):
        """
        組み合わせの候補数が MAX_COMBINATIONS 未満になるように
        ラティスの先頭部分から区切りの良い一部分を抽出するジェネレータ。

        Parameters
        ----------
        lattice: list
            入力となるラティス表現。

        Return
        ------
        list
            先頭部分から切り出した部分的なラティス表現。

        Note
        ----
        この関数はジェネレータなので yield で返します。
        """
        pos_from = 0
        pos_to = len(lattice)

        while pos_from < len(lattice):
            lattice_part = lattice[pos_from:pos_to]
            if pos_to - pos_from == 1 or \
                    self.evaluator.count_combinations(
                        lattice_part) < MAX_COMBINATIONS:
                logger.debug("--- pos {} - {}".format(pos_from, pos_to))
                for i in range(pos_from, pos_to):
                    nodes = lattice[i]
                    logger.debug("{}:'{}' has {} nodes".format(
                        i, nodes[0].surface, len(nodes)))
                logger.debug("---")
                yield lattice_part

                pos_from = pos_to
                pos_to = len(lattice)
                continue

            # 組み合わせ数が多すぎるので分割する
            eliminated = False

            # 句点で分割してみる
            for i in range(pos_from, pos_to - 1):
                node = lattice[i][0]  # i 番目のノード集合の先頭
                if node.node_type != Node.ADDRESS and \
                        node.morphemes['subclass1'] == '句点':
                    pos_to = i + 1
                    eliminated = True
                    break

            if eliminated:
                continue

            # 改行で分割してみる
            for i in range(pos_from, pos_to - 1):
                node = lattice[i][0]  # i 番目のノード集合の先頭
                if node.node_type != Node.ADDRESS and \
                    self.parser.check_word(
                        node.morphemes,
                        {'pos': '記号',
                         'subclass1': '制御コード',
                                      'subclass2': '改行'}):
                    pos_to = i + 1
                    eliminated = True
                    break

            if eliminated:
                continue

            # 記号で分割してみる
            for i in range(pos_from, pos_to - 1):
                node = lattice[i][0]  # i 番目のノード集合の先頭
                if node.node_type != Node.ADDRESS and \
                    self.parser.check_word(node.morphemes,
                                           {'pos': '記号',
                                            'subclass1': '一般'}) and \
                        node.surface in ('／/★●○◎■□◇'):
                    pos_to = i + 1
                    eliminated = True
                    break

            if eliminated:
                continue

            # 読点で分割してみる
            for i in range(pos_from, pos_to - 1):
                node = lattice[i][0]  # i 番目のノード集合の先頭
                if node.node_type != Node.ADDRESS and \
                        node.morphemes['subclass1'] == '読点':
                    pos_to = i + 1
                    eliminated = True
                    break

            if eliminated:
                continue

            # 半分にする、ただし住所表現は分割しない
            i = pos_from
            while i < pos_to:
                logger.debug(
                    '半分 i={i}, pos_from={pos_from}, pos_to={pos_to}'.format(
                        i=i, pos_from=pos_from, pos_to=pos_to))
                if i >= pos_from + int((pos_to - pos_from) / 2):
                    pos_to = i
                    break

                has_non_address_node = False
                for node in lattice[i]:
                    if node.node_type != Node.ADDRESS:
                        has_non_address_node = True
                        break

                node_width = 1
                if has_non_address_node:
                    # 住所ノード以外も保存されている場合
                    for node in lattice[i]:
                        if isinstance(node.morphemes, list):
                            # 住所ノードは複数の形態素を含む
                            node_width = len(node.morphemes)
                            break

                i += node_width

    def getActiveDictionaries(self):
        return self.parser.service.getActiveDictionaries()

    def setActiveDictionaries(self, idlist=None, pattern=None):
        return self.parser.service.setActiveDictionaries(idlist, pattern)

    def disactivateDictionaries(self, idlist=None, pattern=None):
        return self.parser.service.disactivateDictionaries(idlist, pattern)

    def activateDictionaries(self, idlist=None, pattern=None):
        return self.parser.service.activateDictionaries(idlist, pattern)

    def getActiveClasses(self):
        return self.parser.service.getActiveClasses()

    def setActiveClasses(self, patterns=None):
        return self.parser.service.setActiveClasses(patterns)


class Statistics(object):

    @staticmethod
    def count_geowords(lattice):
        """
        ラティス表現を高速に粗く解析し、
        地名語候補を含む形態素の数や ne_class の分布などを集計します。

        詳細な解析を行うためのプランを決定する前処理として利用します。

        Parameters
        ----------
        lattice: list
            ラティス表現。

        Returns
        -------
        dict
            以下の要素を含む集計結果を返します。

            num_geowords: int
                地名語候補を1つ以上含む形態素ノードの数。
            num_addresses: int
                住所候補を1つ以上含む形態素ノードの数。
            ne_classes: dict
                固有名クラスをキー、そのクラスの地名語を1つ以上含む
                形態素ノードの数を値とする dict。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> parser = api.parser.Parser()
        >>> api.parser.Statistics.count_geowords(parser.analyze_sentence('国会議事堂前まで歩きました。'))
        {'num_geowords': 1, 'num_addresses': 0,
            'ne_classes': {'鉄道施設/鉄道駅': 1, '鉄道施設': 1}}
        """
        num_geowords = 0
        num_addresses = 0
        ne_classes = {}
        for nodes in lattice:
            contains_geoword = False
            contains_address = False
            ne_list = []
            for node in nodes:
                if node.node_type == Node.NORMAL:
                    continue

                if node.node_type == Node.ADDRESS:
                    contains_address = True
                    continue

                if node.node_type == Node.GEOWORD:
                    contains_geoword = True
                    ne_class = node.prop.get('ne_class', None)
                    if ne_class:
                        ne_list.append(ne_class)

            if contains_geoword:
                num_geowords += 1

            if contains_address:
                num_addresses += 1

            for ne in set(ne_list):
                if ne in ne_classes:
                    ne_classes[ne] += 1
                else:
                    ne_classes[ne] = 1

                if '/' not in ne:
                    continue

                ne_basic = ne[0: ne.find('/')]
                if ne_basic in ne_classes:
                    ne_classes[ne_basic] += 1
                else:
                    ne_classes[ne_basic] = 1

        return {
            "num_geowords": num_geowords,
            "num_addresses": num_addresses,
            "ne_classes": ne_classes,
        }
