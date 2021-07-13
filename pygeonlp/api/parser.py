import copy
import logging
import re

from pygeonlp.api.filter import EntityClassFilter, GreedySearchFilter
from pygeonlp.api.linker import RankedResults, MAX_COMBINATIONS
from pygeonlp.api.node import Node


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

    def __init__(self, service=None, jageocoder=None, address_regex=None,
                 scoring_class=None, scoring_options=None):
        """
        パーザを初期化します。

        Parameters
        ----------
        service : pygeonlp.service.Service, optional
            拡張形態素解析や地名語の検索を行うための Service インスタンス。
            省略した場合、 ``pygeonlp.api.default_service()`` を利用します。
        jageocoder : jageocoder, optional
            住所ジオコーダー jageocoder モジュール。
            省略した場合、ジオコーディング機能は使用しません。
        address_regex : str, optional
            住所表記の開始とみなす地名語の固有名クラスを表す正規表現。
            省略した場合、``r'^(都道府県|市区町村|行政地域|居住地名)(/.+|)'``
            を利用します。
        scoring_class : class, optional
            パスのスコアとノード間のスコアを計算する関数を持つ
            スコアリングクラス。
            指定しない場合、``pygeonlp.api.scoring`` モジュール内の
            ``ScoringClass`` が利用されます。
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

        self.service = service

        if self.scoring_class is None:
            from .scoring import ScoringClass
            self.scorer = ScoringClass(scoring_options)
        else:
            self.scorer = scoring_class(scoring_options)

        if service is None:
            from . import default_service
            self.service = default_service()

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
                    '"jageocoder" モジュールが init() で初期化されていません。')

        except ModuleNotFoundError:
            raise ParseError(
                '"jageocoder" モジュールがインストールされていません。')

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
            if k not in word:
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

        lattice = []
        words = self.service.ma_parseNode(sentence)

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
                alternative = self._get_alternative_word(word)
                node_candidates.append(
                    Node(surface, Node.NORMAL, alternative))

            # 地名語候補を列挙
            geolods = word['subclass3'].split('/')
            geolod_ids = {}
            for x in geolods:
                geolod_id = x.split(':')[0]
                geolod_ids[geolod_id] = x

            for geolod_id, geoword in self.service.getWordInfo(
                    geolod_ids.keys()).items():
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
        >>> from pygeonlp.api.devtool import pp_lattice
        >>> import jageocoder
        >>> api.init()
        >>> dbdir = api.get_jageocoder_db_dir()
        >>> jageocoder.init(f'sqlite:///{dbdir}/address.db', f'{dbdir}/address.trie')
        >>> parser = api.parser.Parser(jageocoder=jageocoder)
        >>> lattice = parser.analyze_sentence('アメリカ大使館：港区赤坂1-10-5')
        >>> lattice_address = parser.add_address_candidates(lattice, True)
        >>> pp_lattice(lattice_address)
        #0:'アメリカ大使館'
          アメリカ大使館(NORMAL)
        #1:'：'
          ：(NORMAL)
        #2:'港区'
          港区(GEOWORD:['東京都'])
          港区(GEOWORD:['愛知県', '名古屋市'])
          港区(GEOWORD:['大阪府', '大阪市'])
          港区赤坂1-10-(ADDRESS:東京都/港区/赤坂/一丁目/10番)[6]
        #3:'赤坂'
          赤坂(GEOWORD:['上毛電気鉄道', '上毛線'])
          赤坂(GEOWORD:['東京地下鉄', '9号線千代田線'])
          赤坂(GEOWORD:['富士急行', '大月線'])
          赤坂(GEOWORD:['福岡市', '1号線(空港線)'])
        #4:'1'
          1(NORMAL)
        #5:'-'
          -(NORMAL)
        #6:'10'
          10(NORMAL)
        #7:'-'
          -(NORMAL)
        #8:'5'
          5(NORMAL)
        >>> lattice_address = parser.add_address_candidates(lattice)
        >>> pp_lattice(lattice_address)
        #0:'アメリカ大使館'
          アメリカ大使館(NORMAL)
        #1:'：'
          ：(NORMAL)
        #2:'港区赤坂1-10-'
          港区赤坂1-10-(ADDRESS:東京都/港区/赤坂/一丁目/10番)[6]
        #3:'5'
          5(NORMAL)
        >>> node = lattice_address[2][0]
        >>> len(node.morphemes)
        6
        >>> '東京都' in node.morphemes[0]['prop']['hypernym']
        True
        >>> node.morphemes[1]['node_type'] == 'NORMAL'
        True
        >>> lattice = parser.analyze_sentence('喜多方市三島町')
        >>> lattice_address = parser.add_address_candidates(lattice, True)
        >>> pp_lattice(lattice_address)
        #0:'喜多方市'
          ...
        #1:'三島町'
          ...
        """
        if not self.jageocoder_tree:
            return lattice

        i = 0  # 処理中のノードインデックス
        while i < len(lattice):
            nodes = lattice[i]

            can_be_address = False
            for node in nodes:
                if node.node_type == Node.GEOWORD and \
                   self.address_regex.match(node.prop.get('ne_class', '')):
                    can_be_address = True
                    break
                """
                ToDo: 地域・一般も住所ジオコーディングする
                elif node.node_type == Node.NORMAL and \
                    self._check_word(node.morphemes, {
                        'pos': '名詞',
                        'subclass1': '固有名詞',
                        'subclass2': '地域',
                        'subclass3': '一般'}):
                    can_be_address = True
                    break
                """

            if can_be_address:
                res = self.get_addresses(lattice, i)
                if res['address']:
                    new_nodes = []
                    for address in res['address']:
                        morphemes = self._get_address_morphemes(
                            address, lattice[i:res['pos']])
                        if len(morphemes) == 0:
                            # 一致する形態素列が見つからなかった
                            continue

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
                        new_nodes.append(new_node)

                    if len(new_nodes) > 0:
                        if keep_nodes:
                            lattice[i] += new_nodes
                            i = res['pos']
                        else:
                            lattice = lattice[0:i] + \
                                [new_nodes] + lattice[res['pos']:]
                            i += 1

                        continue

            i += 1

        # センテンス終了
        return lattice

    def _get_address_morphemes(self, address_element, lattice_part):
        """
        住所ジオコーダが返した住所候補に対応する
        形態素 Node のリストを生成して返します。

        Parameters
        ----------
        address_element : dict
            次のような要素を持つ住所候補。
            - id: 3754681
            - name: '皆瀬'
            - x: 140.669102
            - y: 39.005262
            - level: 5
            - note: None
            - fullname: ['秋田県', '湯沢市', '皆瀬']
        lattice_part : list of Node
            住所候補に対応するラティス表現の部分配列。
            形態素列を作成する際に、住所要素と一致するノードを利用します。

        Returns
        -------
        list of Node
            住所要素ごとに対応する形態素 Node を作成し、
            リストを返します。
            パラメータ例では "秋田県" に対応するノード、
            "湯沢市" に対応するノード、 "皆瀬" に対応するノードを
            作成します。
        """
        morphemes = []
        parent = Node(
            surface="",
            node_type=Node.ADDRESS,
            morphemes={
                'conjugated_form': '*',
                'conjugation_type': '*',
                'original_form': "",
                'pos': '名詞',
                'prononciation': '',
                'subclass1': '固有名詞',
                'subclass2': '地域',
                'subclass3': '一般',
                'surface': "",
                'yomi': ''},
            geometry={
                'type': 'Point',
                'coordinates': [
                    address_element['x'], address_element['y']],
            },
            prop=address_element,
        )

        for nodes in lattice_part:
            node = nodes[0]
            if node.node_type != Node.GEOWORD:
                # 非地名語はそのまま
                morphemes.append(node.as_dict())
                continue

            dummy_node = Node(
                surface=node.surface,
                node_type=Node.NORMAL,
                morphemes=copy.deepcopy(node.morphemes),
                geometry=None,
                prop=None,
            )
            dummy_node.morphemes.update({
                'subclass1': '固有名詞',
                'subclass2': '地域',
                'subclass3': '一般',
            })

            if node.surface not in address_element['fullname']:
                # 住所要素のどの表記とも一致しない
                morphemes.append(dummy_node.as_dict())
                continue

            # 親ノードに最も関係スコアの高い地名語ノードを選ぶ
            max_score = 0
            cand = None

            for node in nodes:
                if not self.address_regex.match(node.prop.get('ne_class', '')):
                    # 固有名クラスが住所表記のものではない
                    score = 0
                else:
                    score = self.scorer.node_relation_score(parent, node)
                    if score > max_score:
                        cand = node
                        max_score = score
            if cand:
                # 親ノードと関係のある候補が見つかった場合
                parent = cand
            else:
                cand = dummy_node

            morphemes.append(cand.as_dict())

        return morphemes

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
            if len(surface) > len(geocoding_result[0][1]):
                # 形態素 lattice[i] は住所の区切りと一致しない
                break

            i += 1
            if len(surface) == len(geocoding_result[0][1]):
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
