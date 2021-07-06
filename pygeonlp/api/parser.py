import copy
import json
import logging
import re

from .filter import EntityClassFilter, GreedySearchFilter
from .linker import RankedResults, MAX_COMBINATIONS
from .node import Node


logger = logging.getLogger(__name__)


class ParseError(RuntimeError):
    """
    パージング処理の際に例外が起こると、このクラスが発生します。
    """
    pass


class Parser(object):
    """
    形態素解析と地名語抽出を行なうパーザ。

    Attributes
    ----------
    capi_ma : pygeonlp.capi
        拡張形態素解析を行なう C++ で実装されたモジュール capi のインスタンス。
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

    def __init__(self, capi_ma=None, jageocoder=None, address_regex=None,
                 scoring_class=None, scoring_options=None):
        """
        パーザを初期化します。

        Parameters
        ----------
        capi_ma : pygeonlp.capi, optional
            拡張形態素解析を行う C++ モジュール capi のインスタンス。
            省略した場合、 default_service の capi_ma を利用します。
        jageocoder : jageocoder, optional
            住所ジオコーダー jageocoder モジュール。
            省略した場合、ジオコーディング機能は使用しません。
        address_regex : str, optional
            住所表記の開始とみなす地名語の固有名クラスを表す正規表現。
            省略した場合、`r'^(都道府県|市区町村|行政地域|居住地名)(/.+|)'`
            を利用します。
        scoring_class : class, optional
            パスのスコアとノード間のスコアを計算する関数を持つ
            スコアリングクラス。
            指定しない場合、`pygeonlp.api.scoring` モジュール内の
            `ScoringClass` が利用されます。
        scoring_options : any, optional
            スコアリングクラスの初期化に渡すオプションパラメータ。

        Notes
        -----
        jageocoder パラメータには jageocoder.address.AddressTree インスタンスを
        指定することもできます。
        """
        self.scoring_class = scoring_class
        self.scoring_options = scoring_options
        self.ranker = RankedResults(
            scoring_class=self.scoring_class,
            scoring_options=self.scoring_options,
            max_results=1, max_combinations=MAX_COMBINATIONS)

        self.capi_ma = capi_ma

        if self.scoring_class is None:
            from .scoring import ScoringClass
            self.scorer = ScoringClass(scoring_options)
        else:
            self.scorer = scoring_class(scoring_options)

        if capi_ma is None:
            from . import default_service
            self.capi_ma = default_service().capi_ma

        if jageocoder is None:
            self.jageocoder_tree = None
            return

        # jageocoder がインストールされているか確認
        try:
            import jageocoder
            if isinstance(jageocoder, jageocoder.address.AddressTree):
                self.jageocoder_tree = jageocoder
            elif isinstance(
                    jageocoder.tree, jageocoder.address.AddressTree):
                self.jageocoder_tree = jageocoder.tree
            else:
                raise ParseError(
                    'The jageocoder module must be initialized first.')

        except ModuleNotFoundError as e:
            raise ParseError(
                'Install jageocoder package to use address geocoding.')

        if address_regex is None:
            self.address_regex = re.compile(
                r'^(都道府県|市区町村|行政地域|居住地名)(\/.+|)')
        else:
            self.address_regex = re.compile(address_regex)

    def _check_word(self, word, filter):
        """
        Word の形態素情報が filter に含まれる全ての key, value と
        一致しているかどうかを調べます。

        Parameters
        ----------
        word : dict
            チェック対象となる dict オブジェクト。
        filter : dict
            チェックする項目と値を持つ dict オブジェクト。

        Returns
        -------
        bool
            全ての項目が一致する場合 True, 一つでも一致しない場合 False。
        """
        if not isinstance(word, dict):
            return False

        for k, v in filter.items():
            if not k in word:
                return False

            if word[k] != v:
                return False

        return True

    def analyze_sentence(self, sentence, **kwargs):
        """
        sentence を解析し、全ての地名語候補を含む Node リストを
        ラティス表現で返します。

        Parameters
        ----------
        sentence : str
            解析対象の文字列。

        Returns
        -------
        list
            ラティス表現。形態素ごとに、対応する地名語候補のリストを含むリストです。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> parser = api.parser.Parser()
        >>> for nodes in parser.analyze_sentence('NIIは千代田区一ツ橋2-1-2にあります。'):
        ...     [x.simple() for x in nodes]
        ...
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
        from . import getWordInfo

        lattice = []
        words = self.capi_ma.parseNode(sentence)

        i = 0  # 処理中の単語のインデックス
        while i < len(words):
            word = words[i]
            if i < len(words) - 1:
                next_word = words[i + 1]
            else:
                next_word = None

            if i < len(words) - 2:
                nnext_word = words[i + 2]
            else:
                nnext_word = None

            surface = word['surface']
            if surface == '':
                i += 1
                continue  # BOS, EOS をスキップ

            # 人名チェック 1 - 姓, 名 または 人名, 人名の場合
            if next_word is not None and \
               (word['conjugated_form'] == '名詞-固有名詞-人名-姓' or
                self._check_word(word, {
                    'pos': '名詞',
                    'subclass1': '固有名詞',
                    'subclass2': '人名'
                })) and \
               (next_word['conjugated_form'] == '名詞-固有名詞-人名-名' or
                    self._check_word(next_word, {
                        'pos': '名詞',
                        'subclass1': '固有名詞',
                        'subclass2': '人名'
                    })):
                lattice.append(
                    [Node(surface,
                          Node.NORMAL,
                          self._get_alternative_word(word))])
                lattice.append(
                    [Node(next_word['surface'],
                          Node.NORMAL,
                          self._get_alternative_word(next_word))])
                i += 2
                continue

            # 人名チェック 2 - 名詞, 名詞-接尾-人名 の場合
            if word['pos'] == '名詞' and \
               self._check_word(next_word, {
                   'pos': '名詞',
                   'subclass1': '接尾',
                   'subclass2': '人名'
               }):
                lattice.append([Node(surface, Node.NORMAL,
                                     self._get_alternative_word(word))])
                lattice.append([Node(next_word['surface'],
                                     Node.NORMAL, next_word)])
                i += 2
                continue

            # 人名チェック 3 - 名詞, 名詞, 名詞-接尾-人名 の場合
            if word['pos'] == '名詞' and \
                next_word['pos'] == '名詞' and \
               self._check_word(nnext_word, {
                   'pos': '名詞',
                   'subclass1': '接尾',
                   'subclass2': '人名'
               }):
                lattice.append([Node(surface, Node.NORMAL,
                                     self._get_alternative_word(word))])
                lattice.append([Node(next_word['surface'],
                                     Node.NORMAL,
                                     self._get_alternative_word(next_word))])
                lattice.append([Node(nnext_word['surface'],
                                     Node.NORMAL,
                                     self._get_alternative_word(nnext_word))])
                i += 3
                continue

            # 年号チェック
            if surface in ('明治', '大正', '昭和', '平成', '令和', '西暦',):
                is_era = False
                j = i + 1
                while j < len(words):
                    n = words[j]
                    if n['surface'] in ('年', '年度', '年代', '元年', ) or \
                       n['pos'] == '記号':
                        is_era = True
                        break
                    elif n['subclass1'] != '数':
                        break

                    j += 1

                if is_era:
                    for k in range(i, j + 1):
                        n = words[k]
                        lattice.append([Node(n['surface'],
                                             Node.NORMAL,
                                             self._get_alternative_word(n))])
                        i = j + 1

                    continue

            if word['subclass2'] != '地名語' or \
               word['subclass1'] == '接尾':
                lattice.append([Node(surface, Node.NORMAL, word)])
                i += 1
                continue

            # 地名語の処理
            node_candidates = []

            # 地名語以外の可能性を追加
            if word['conjugated_form'] not in ("", "*"):
                pos_args = word['conjugated_form'].split('-')
                alternative = self._get_alternative_word(word)
                node_candidates.append(
                    Node(surface, Node.NORMAL, alternative))

            # 地名語候補を列挙
            geolods = word['subclass3'].split('/')
            geolod_ids = {}
            for x in geolods:
                geolod_id = x.split(':')[0]
                geolod_ids[geolod_id] = x

            for geolod_id, geoword in getWordInfo(geolod_ids.keys()).items():
                if geoword is None:
                    raise RuntimeError(
                        "No geoword found with id='{}', word={}".format(
                            geolod_id, word))

                geometry = {
                    'type': 'Point',
                    'coordinates': [
                        float(geoword['longitude']),
                        float(geoword['latitude']),
                    ]
                }
                morpheme = copy.copy(word)
                morpheme['subclass3'] = geolod_ids[geolod_id]
                node_candidates.append(
                    Node(surface, Node.GEOWORD, morpheme,
                         geometry=geometry, prop=geoword))

            lattice.append(node_candidates)
            i += 1

        # センテンス終了
        return lattice

    def add_address_candidates(self, lattice, keep_nodes=False, **kwargs):
        """
        ラティス表現に住所候補を追加します。

        Parameters
        ----------
        lattice : list
            analyze_sentence の結果のラティス表現（住所を含まない）。
        keep_nodes : bool, optional
            住所以外のノードを維持するかどうかを指示するフラグ。
            デフォルトは False （維持しない）。

        Returns
        -------
        list
            住所候補を追加したラティス表現。


        Examples
        --------
        >>> import pygeonlp.api as api
        >>> import jageocoder
        >>> api.init()
        >>> dbdir = api.get_jageocoder_dir()
        >>> jageocoder.init(f'sqlite:///{dbdir}/address.db', f'{dbdir}/address.trie')
        >>> parser = api.parser.Parser(jageocoder=jageocoder)
        >>> lattice = parser.analyze_sentence('NIIは千代田区一ツ橋2-1-2にあります。')
        >>> lattice_address = parser.add_address_candidates(lattice, True)
        >>> for nodes in lattice_address:
        ...     [x.simple() for x in nodes]
        ...
        ['NII(NORMAL)']
        ['は(NORMAL)']
        ["千代田区(GEOWORD:['東京都'])", '千代田区一ツ橋2-1-(ADDRESS:東京都/千代田区/一ツ橋/二丁目/1番)[6]']
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
        >>> lattice_address = parser.add_address_candidates(lattice)
        >>> for nodes in lattice_address:
        ...     [x.simple() for x in nodes]
        ...
        ['NII(NORMAL)']
        ['は(NORMAL)']
        ['千代田区一ツ橋2-1-(ADDRESS:東京都/千代田区/一ツ橋/二丁目/1番)[6]']
        ['2(NORMAL)']
        ['に(NORMAL)']
        ['あり(NORMAL)']
        ['ます(NORMAL)']
        ['。(NORMAL)']
        """
        if not self.jageocoder_tree:
            return lattice

        address_end_pos = 0

        i = 0  # 処理中のノードインデックス
        while i < len(lattice):
            nodes = lattice[i]

            can_be_address = False
            for node in nodes:
                if node.node_type == Node.GEOWORD and \
                   self.address_regex.match(node.prop.get('ne_class', '')):
                    can_be_address = True
                    break
                elif node.node_type == Node.NORMAL and \
                    self._check_word(node.morphemes, {
                        'pos': '名詞',
                        'subclass1': '固有名詞',
                        'subclass2': '地域',
                        'subclass3': '一般'}):
                    can_be_address = True
                    break

            if can_be_address:
                res = self.get_addresses(lattice, i)
                if res['address']:
                    morphemes = []
                    parent = None
                    for ns in lattice[i:res['pos']]:
                        if parent is None or len(ns) == 1:
                            cand = ns[0]
                        else:
                            # 親住所要素に最も関係する住所要素を選ぶ
                            max_score = 0
                            cand = None
                            for n in ns:
                                score = self.scorer.node_relation_score(
                                    parent, n)
                                if score > max_score:
                                    cand = n
                                    max_score = score

                        n = cand.as_dict()
                        morphemes.append(n)
                        parent = cand

                    if not keep_nodes:
                        lattice = lattice[0:i] + [[]] + lattice[res['pos']:]

                    for address in res['address']:
                        geometry = {
                            'type': 'Point',
                            'coordinates': [
                                address['x'],
                                address['y'], ]
                        }
                        new_node = Node(
                            surface=res['surface'],
                            node_type=Node.ADDRESS,
                            morphemes=morphemes,
                            geometry=geometry,
                            prop=address,
                        )
                        lattice[i].append(new_node)

                    if keep_nodes:
                        i = res['pos']
                    else:
                        i += 1

                    continue

            i += 1

        # センテンス終了
        return lattice

    def _get_alternative_word(self, word):
        """
        形態素ノードの conjugated_form に記載された
        地名語以外の形態素情報を復元して返します。

        Parameters
        ----------
        word : dict
            形態素情報をもつ語。

        Return
        ------
        dict
            復元した形態素情報を追加した語。
        """
        if not self._check_word(word,
                                {'pos': '名詞',
                                 'subclass1': '固有名詞',
                                 'subclass2': '地名語'
                                 }) or word['conjugated_form'] == '*':
            return word

        pos_args = word['conjugated_form'].split('-')
        alternative = copy.copy(word)
        alternative.update({
            'conjugated_form': '名詞-固有名詞-地名語',
            'pos': pos_args[0],
            'subclass1': pos_args[1] if len(pos_args) > 1 else '*',
            'subclass2': pos_args[2] if len(pos_args) > 2 else '*',
            'subclass3': pos_args[3] if len(pos_args) > 3 else '*',
        })
        return alternative

    def get_addresses(self, lattice, pos):
        """
        ラティス表現の単語列から住所部分を抽出します。

        Parameters
        ----------
        lattice : list
            analyze_sentence() が返すノードのリスト（ラティス表現）。
        pos : int
            住所抽出を開始するリストのインデックス。

        Returns
        -------
        dict
            以下の要素を持つ dict オブジェクトを返します。

            address : jageocoder.address.AddressNode
                ジオコーディングの結果, 住所ではなかった場合 None。
            pos : int
                住所とみなされた形態素ノードの次のインデックス。
        """
        surface = ''
        i = pos
        while i < len(lattice):
            surface += lattice[i][0].surface
            i += 1
            if len(surface) > 50:
                # 住所文字列は最長で 50 文字と仮定
                break

        geocoding_result = self.jageocoder_tree.search(surface)

        if len(geocoding_result) < 1:
            return {"address": None, "pos": pos}

        # 一致した文字列が形態素ノード列のどの部分に当たるかチェック
        surface = ''
        i = pos
        while i < len(lattice):
            surface += lattice[i][0].surface
            i += 1
            if len(surface) >= len(geocoding_result[0][1]):
                break

        if i - pos == 1:
            # 先頭の要素だけが住所要素の場合は住所とみなさない
            return {"surface": None, "address": None, "pos": pos}

        return {
            "surface": geocoding_result[0][1],
            "address": [x[0].as_dict() for x in geocoding_result],
            "pos": i,
        }

    def geoparse(self, sentence, filters=None):
        """
        文を解析して GeoJSON Feature 形式に変換可能な dict のリストを返します。

        Parameters
        ----------
        sentence : str
            解析する文字列
        filters : list
            適用するフィルタオブジェクトのリスト

        Returns
        -------
        list
            GeoJSON Feature 形式に変換可能な dict のリスト。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> parser = api.parser.Parser()
        >>> parser.geoparse('国会議事堂前まで歩きました。')
        [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.74305333333334, 35.673543333333335]}, 'properties': {'surface': '国会議事堂前', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '国会議事堂前', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'QUy2yP:国会議事堂前駅', 'surface': '国会議事堂前', 'yomi': ''}, 'geoword_properties': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': '1b5cc77fc2c83713a6750642f373d01f', 'geolod_id': 'QUy2yP', 'hypernym': ['東京地下鉄', '9号線千代田線'], 'institution_type': '民営鉄道', 'latitude': '35.673543333333335', 'longitude': '139.74305333333334', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'まで', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': 'まで', 'pos': '助詞', 'prononciation': 'マデ', 'subclass1': '副助詞', 'subclass2': '*', 'subclass3': '*', 'surface': 'まで', 'yomi': 'マデ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '歩き', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '五段・カ行イ音便', 'conjugation_type': '連用形', 'original_form': '歩く', 'pos': '動詞', 'prononciation': 'アルキ', 'subclass1': '自立', 'subclass2': '*', 'subclass3': '*', 'surface': '歩き', 'yomi': 'アルキ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'まし', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '特殊・マス', 'conjugation_type': '連用形', 'original_form': 'ます', 'pos': '助動詞', 'prononciation': 'マシ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'まし', 'yomi': 'マシ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': 'た', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '特殊・タ', 'conjugation_type': '基本形', 'original_form': 'た', 'pos': '助動詞', 'prononciation': 'タ', 'subclass1': '*', 'subclass2': '*', 'subclass3': '*', 'surface': 'た', 'yomi': 'タ'}}}, {'type': 'Feature', 'geometry': None, 'properties': {'surface': '。', 'node_type': 'NORMAL', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '。', 'pos': '記号', 'prononciation': '。', 'subclass1': '句点', 'subclass2': '*', 'subclass3': '*', 'surface': '。', 'yomi': '。'}}}]

        Notes
        -----
        このメソッドは解析結果から適切なフィルタを判断し、
        候補の絞り込みやランキングを行ないます。
        """
        lattice = self.analyze_sentence(sentence)

        search_plan = "exhaustive"
        if filters is None:
            filters = []

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

        for f in filters:
            lattice = f(lattice)

        results = []
        if self.jageocoder_tree:
            lattice = self.add_address_candidates(lattice)

        for lattice_part in self.get_processible_lattice_part(lattice):
            if len(lattice_part) < 1:
                continue    # 空行

            results += self.ranker.get(lattice_part)

        features = []
        for result in results:
            nodes = result['result']
            for node in nodes:
                features.append(node.as_geojson())

        return features

    def get_processible_lattice_part(self, lattice):
        """
        組み合わせの候補数が MAX_COMBINATIONS 未満になるように
        ラティスの先頭部分から区切りの良い一部分を抽出するジェネレータ。

        Parameters
        ----------
        lattice : list
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
            if self.ranker.count_combinations(lattice_part) < MAX_COMBINATIONS:
                logger.debug("---")
                for nodes in lattice_part:
                    logger.debug("'{}':{}".format(
                        nodes[0].surface,
                        len(nodes)))
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
                    self._check_word(node.morphemes,
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
                    self._check_word(node.morphemes,
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
            while i < pos_to - 1:
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


class Statistics(object):

    @staticmethod
    def count_geowords(lattice):
        """
        ラティス表現を高速に粗く解析し、
        地名語候補を含む形態素の数や ne_class の分布などを集計します。

        詳細な解析を行うためのプランを決定する前処理として利用します。

        Parameters
        ----------
        lattice : list
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
        {'num_geowords': 1, 'num_addresses': 0, 'ne_classes': {'鉄道施設/鉄道駅': 1, '鉄道施設': 1}}
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
