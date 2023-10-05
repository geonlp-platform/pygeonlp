import copy
import logging
import re

import jageocoder as _jageocoder
from jageocoder.itaiji import converter as itaiji_converter

from pygeonlp.api.node import Node
from pygeonlp.api.service import Service

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
        利用しない場合は False を指定してください。
    address_regex : regex
        住所要素の先頭になりえる固有名クラスの正規表現（コンパイル済み）。
    scoring_class : class
        パスのスコアリングに利用するクラス。
    """

    def __init__(self, db_dir=None, jageocoder=None, address_regex=None,
                 **options):
        """
        パーザを初期化します。

        Parameters
        ----------
        db_dir : PathLike, optional
            データベースディレクトリ。
            省略した場合は ``api.init.get_db_dir()`` が返す値を利用します。
        jageocoder : jageocoder.tree.AddressTree, optional
            利用する住所ジオコーダーを指定します。省略した場合、
            jageocoder モジュールのデフォルトオブジェクトを利用します。
            False を指定した場合、ジオコーディング機能を利用しません。
        address_regex : str, optional
            住所表記の開始とみなす地名語の固有名クラスを表す正規表現。
            省略した場合、``r'^(都道府県|市区町村|行政地域|居住地名)(/.+|)'``
            を利用します。
        """
        self.service = Service(db_dir=db_dir, **options)

        if jageocoder is False:
            self.jageocoder_tree = None

        else:
            # jageocoder 辞書が初期化されていなければ初期化
            if not _jageocoder.is_initialized():
                db_dir = _jageocoder.get_db_dir(mode='r')
                if db_dir is None:
                    if jageocoder is None:
                        logger.info(
                            'jageocoder 用住所辞書が見つかりません。')
                        self.jageocoder_tree = None
                    else:
                        raise ParseError(
                            'jageocoder 用住所辞書が見つかりません。')
                else:
                    _jageocoder.init(mode='r')

            if _jageocoder.is_initialized():
                self.jageocoder_tree = _jageocoder.get_module_tree()

        if address_regex is None:
            self.address_regex = re.compile(
                r'^(都道府県|市区町村|行政地域|居住地名)(\/.+|)')
        else:
            self.address_regex = re.compile(address_regex)

    def set_jageocoder(self, jageocoder):
        """
        この Parser が利用する jageocoder を変更します。

        Parameters
        ----------
        jageocoder : jageocoder.tree.AddressTree, optional
            利用する住所ジオコーダーを指定します。省略した場合、
            jageocoder モジュールのデフォルトオブジェクトを利用します。
            False を指定した場合、ジオコーディング機能を利用しません。
        """
        from jageocoder.tree import AddressTree

        if jageocoder is False:
            self.jageocoder_tree = None
            return

        if isinstance(jageocoder, AddressTree):
            self.jageocoder_tree = jageocoder
            return

        # jageocoder 辞書が初期化されていなければ初期化
        if not _jageocoder.is_initialized():
            db_dir = _jageocoder.get_db_dir(mode='r')
            if db_dir is None:
                raise ParseError(
                    'jageocoder 用住所辞書が見つかりません。')

            _jageocoder.init(mode='r')

        self.jageocoder_tree = _jageocoder.get_module_tree()

    def check_word(self, word, filter):
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
                self.check_word(word, {
                    'pos': '名詞',
                    'subclass1': '固有名詞',
                    'subclass2': '人名'
                })) and \
               (next_word['conjugated_form'] == '名詞-固有名詞-人名-名' or
                    self.check_word(next_word, {
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
               self.check_word(next_word, {
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
               self.check_word(nnext_word, {
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
        >>> from pygeonlp.api.node import Node
        >>> api.init()
        >>> parser = api.parser.Parser(jageocoder=True)
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
        >>> '東京都' in node.morphemes[0].prop['hypernym']
        True
        >>> node.morphemes[1].node_type == Node.NORMAL
        True
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
                # 地域・一般の場合でも、都道府県または市区町村名から始まる場合は
                # 住所ジオコーディングの対象とする（NEologdで結合しているケース）
                elif node.node_type == Node.NORMAL and \
                    self.check_word(node.morphemes, {
                        'pos': '名詞',
                        'subclass1': '固有名詞',
                        'subclass2': '地域',
                        'subclass3': '一般'}):
                    # jageocoder の trie を利用して語の候補を得る
                    prefixes = self.jageocoder_tree.trie.common_prefixes(
                        itaiji_converter.standardize(node.surface))
                    if node.morphemes['original_form'] != '':
                        prefixes.update(
                            self.jageocoder_tree.trie.common_prefixes(
                                itaiji_converter.standardize(
                                    node.morphemes['original_form'])))

                    for prefix in prefixes.keys():
                        if can_be_address is True:
                            break

                        # prefix と一致する正規化前の部分文字列を得る
                        surface = ''
                        for c in node.surface:
                            surface += c
                            if itaiji_converter.standardize(surface) == prefix:
                                break

                        words = self.service.searchWord(surface)
                        for word in words.values():
                            if self.address_regex.match(word['ne_class']):
                                can_be_address = True
                                break

                    break

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
        address_element: dict
            次のような要素を持つ住所候補。
            - id: 3754681
            - name: '皆瀬'
            - x: 140.669102
            - y: 39.005262
            - level: 5
            - note: None
            - fullname: ['秋田県', '湯沢市', '皆瀬']
        lattice_part: list of Node
            住所候補に対応するラティス表現の部分配列。
            形態素列を作成する際に、住所要素と一致するノードを利用します。

        Returns
        -------
        list of Node
            住所要素ごとに対応する形態素 Node を作成し、
            リストを返します。
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
                morphemes.append(node)
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
                morphemes.append(dummy_node)
                continue

            # 親ノードに最も関係スコアの高い地名語ノードを選ぶ
            max_score = 0
            cand = None

            for node in nodes:
                if not self.address_regex.match(node.prop.get('ne_class', '')):
                    # 固有名クラスが住所表記のものではない
                    score = 0
                else:
                    score = self._calc_node_score_by_distance(parent, node)
                    if score > max_score:
                        cand = node
                        max_score = score

            if cand:
                # 親ノードと関係のある候補が見つかった場合
                parent = cand
            else:
                cand = dummy_node

            morphemes.append(cand)

        return morphemes

    def _calc_node_score_by_distance(self, node0, node1) -> int:
        score = 0
        # 距離が近いほど高得点を返す
        try:
            dist = node0.distance(node1)
            if dist < 10000.0:  # 10km 以下
                score += 5
            else:
                # 50km までは 1 点追加
                score += int(50000.0 / dist)
        except RuntimeError:
            pass

        return score

    def _get_alternative_word(self, word):
        """
        形態素ノードの conjugated_form に記載された
        地名語以外の形態素情報を復元して返します。

        Parameters
        ----------
        word: dict
            形態素情報をもつ語。

        Return
        ------
        dict
            復元した形態素情報を追加した語。
        """
        if not self.check_word(word,
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

    def get_surfaces(self, lattice, pos_from, limit):
        """
        ラティス表現の単語列の pos 番目から、 limit で指定した
        文字数を超える位置までの表記のリストを取得します。

        単語の surface と original_form の組み合わせを列挙します。

        Parameters
        ----------
        lattice: list
            analyze_sentence() が返すノードのリスト（ラティス表現）。
        pos_from: int
            表記リストの先頭となるノードのインデックス。
        limit: int
            文字列の長さ（limit を超えたノードを含む）

        Returns
        -------
        list
            単語列（単語表記のリスト）
        """
        candidate = []
        for pos in range(pos_from, len(lattice)):

            nodes = lattice[pos]
            if len(''.join(candidate)) > limit:
                break

            node = nodes[0]
            original_form = node.morphemes['original_form']
            if node.morphemes['pos'] != '名詞' or \
                    original_form in ('', '*', node.surface):
                candidate.append(node.surface)
            else:
                candidate.append(original_form)

        return candidate

    def get_addresses(self, lattice, pos):
        """
        ラティス表現の単語列から住所部分を抽出します。

        Parameters
        ----------
        lattice: list
            analyze_sentence() が返すノードのリスト（ラティス表現）。
        pos: int
            住所抽出を開始するリストのインデックス。

        Returns
        -------
        dict
            以下の要素を持つ dict オブジェクトを返します。

            address: jageocoder.address.AddressNode
                ジオコーディングの結果, 住所ではなかった場合 None。
            pos: int
                住所とみなされた形態素ノードの次のインデックス。
        """
        surfaces = self.get_surfaces(lattice, pos, 50)
        geocoding_result = self.jageocoder_tree.searchNode(''.join(surfaces))
        if len(geocoding_result) == 0:
            return {"address": None, "pos": pos}

        address_string = geocoding_result[0][1]  # 変換できた住所文字列
        check_address = re.sub(r'番$', '番地', address_string)

        # 一致した文字列が形態素ノード列のどの部分に当たるかチェック
        surface = ''
        i = 0
        while i < len(surfaces):
            surface += surfaces[i]
            if len(surface) > len(check_address):
                # 形態素 lattice[i] は住所の区切りと一致しないので
                # lattice[0:i] までを利用してジオコーディングをやり直す
                return self.get_addresses(lattice[0:pos + i], pos)

            i += 1
            if len(surface) == len(check_address):
                break

        if i == 1 and lattice[pos][0].node_type == Node.GEOWORD:
            # 先頭の要素だけが住所要素を構成し、
            # 地名語なら住所とみなさない（地名語とする）
            return {"address": None, "pos": pos}

        return {
            "surface": ''.join([x[0].surface for x in lattice[pos: pos+i]]),
            "address": [x[0].as_dict() for x in geocoding_result],
            "pos": pos + i,
        }

    def analyze(self, sentence, **kwargs):
        """
        文を解析した結果をラティス表現で返します。

        Parameters
        ----------
        sentence : str
            解析するテキスト。

        Returns
        -------
        list
            解析結果のラティス表現。

        Examples
        --------
        >>> from pygeonlp.api.parser import Parser
        >>> parser = Parser()
        >>> parser.analyze('今日は国会議事堂前まで歩きました。')
        [[{"surface": "今日", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "今日", "pos": "名詞", "prononciation": "キョー", "subclass1": "副詞可能", "subclass2": "*", "subclass3": "*", "surface": "今日", "yomi": "キョウ"}, "geometry": null, "prop": null}], [{"surface": "は", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "は", "pos": "助詞", "prononciation": "ワ", "subclass1": "係助詞", "subclass2": "*", "subclass3": "*", "surface": "は", "yomi": "ハ"}, "geometry": null, "prop": null}], [{"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "Bn4q6d:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geometry": {"type": "Point", "coordinates": [139.74534166666666, 35.674845]}, "prop": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "LrGGxY", "geolod_id": "Bn4q6d", "hypernym": ["東京地下鉄", "4号線丸ノ内線"], "institution_type": "民営鉄道", "latitude": "35.674845", "longitude": "139.74534166666666", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02"}}, {"surface": "国会議事堂前", "node_type": "GEOWORD", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "国会議事堂前", "pos": "名詞", "prononciation": "", "subclass1": "固有名詞", "subclass2": "地名語", "subclass3": "cE8W4w:国会議事堂前駅", "surface": "国会議事堂前", "yomi": ""}, "geometry": {"type": "Point", "coordinates": [139.74305333333334, 35.673543333333335]}, "prop": {"body": "国会議事堂前", "dictionary_id": 3, "entry_id": "4NFELa", "geolod_id": "cE8W4w", "hypernym": ["東京地下鉄", "9号線千代田線"], "institution_type": "民営鉄道", "latitude": "35.673543333333335", "longitude": "139.74305333333334", "ne_class": "鉄道施設/鉄道駅", "railway_class": "普通鉄道", "suffix": ["駅", ""], "dictionary_identifier": "geonlp:ksj-station-N02"}}], [{"surface": "まで", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "まで", "pos": "助詞", "prononciation": "マデ", "subclass1": "副助詞", "subclass2": "*", "subclass3": "*", "surface": "まで", "yomi": "マデ"}, "geometry": null, "prop": null}], [{"surface": "歩き", "node_type": "NORMAL", "morphemes": {"conjugated_form": "五段・カ行イ音便", "conjugation_type": "連用形", "original_form": "歩く", "pos": "動詞", "prononciation": "アルキ", "subclass1": "自立", "subclass2": "*", "subclass3": "*", "surface": "歩き", "yomi": "アルキ"}, "geometry": null, "prop": null}], [{"surface": "まし", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・マス", "conjugation_type": "連用形", "original_form": "ます", "pos": "助動詞", "prononciation": "マシ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "まし", "yomi": "マシ"}, "geometry": null, "prop": null}], [{"surface": "た", "node_type": "NORMAL", "morphemes": {"conjugated_form": "特殊・タ", "conjugation_type": "基本形", "original_form": "た", "pos": "助動詞", "prononciation": "タ", "subclass1": "*", "subclass2": "*", "subclass3": "*", "surface": "た", "yomi": "タ"}, "geometry": null, "prop": null}], [{"surface": "。", "node_type": "NORMAL", "morphemes": {"conjugated_form": "*", "conjugation_type": "*", "original_form": "。", "pos": "記号", "prononciation": "。", "subclass1": "句点", "subclass2": "*", "subclass3": "*", "surface": "。", "yomi": "。"}, "geometry": null, "prop": null}]]

        Note
        ----
        ラティス表現では全ての地名語の候補を列挙して返します。
        ``analyze_sentence()`` に住所ジオコーディングの結果も追加します。
        """  # noqa: E501
        varray = self.analyze_sentence(sentence, **kwargs)

        if self.jageocoder_tree:
            varray = self.add_address_candidates(varray, **kwargs)

        return varray
