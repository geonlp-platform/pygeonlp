from logging import getLogger

from pygeonlp.api.node import Node

logger = getLogger(__name__)


MAX_COMBINATIONS = 256


class LinkerError(RuntimeError):
    pass


class LinkedResults(object):
    """
    ラティス表現からパス表現の候補を
    次々に出力するイテレータを作成します。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.linker import LinkedResults
    >>> api.init()
    >>> for lr in LinkedResults(api.analyze('国会議事堂前まで歩きました。')):
    ...     [x.simple() for x in lr]
    ["国会議事堂前(GEOWORD:['東京地下鉄', '4号線丸ノ内線'])", 'まで(NORMAL)', '歩き(NORMAL)', 'まし(NORMAL)', 'た(NORMAL)', '。(NORMAL)']
    ["国会議事堂前(GEOWORD:['東京地下鉄', '9号線千代田線'])", 'まで(NORMAL)', '歩き(NORMAL)', 'まし(NORMAL)', 'た(NORMAL)', '。(NORMAL)']
    """

    def __init__(self, lattice):
        """
        Parameters
        ----------
        lattice : list
            入力となるラティス表現

        Returns
        -------
        int
            常に 0
        """
        self.lattice = lattice
        self.reset_counter()

    def __iter__(self):
        return self

    def __next__(self):
        """
        カウンターが示している候補リストを返し、カウンターを次に進めます。
        """
        output = self.get_result()
        if output is None:
            raise StopIteration()

        self.increment_counter()
        return output

    def counter(self):
        """
        カウンターを返します。
        """
        return self.counters

    def get_result(self):
        """
        カウンターが示している候補リストを返します。
        カウンターは次に進めません。
        """
        if self.counters[0] == -1:
            # 既に最後まで取得済みの場合は None を返す
            return None

        output = []
        n = 0
        while n < len(self.lattice):
            node = self.lattice[n][self.counters[n]]
            output.append(node)

            # 住所ノード以外が保存されているかチェック
            has_non_address_node = False
            for _node in self.lattice[n]:
                if _node.node_type != Node.ADDRESS:
                    has_non_address_node = True
                    break

            if isinstance(node.morphemes, (list, tuple,)) and \
                    has_non_address_node:
                n += len(node.morphemes)
            else:
                n += 1

        return output

    def reset_counter(self):
        """
        カウンターを初期化します。
        """
        self.counters = [0] * len(self.lattice)
        # 形態素ノードの種別を事前に計算する
        # 0: 非地名語のみ
        # 1: 地名語を含む（住所は含まない）
        # 2: 住所の先頭ノード
        self.node_types = [Node.NORMAL] * len(self.lattice)
        n = 0
        while n < len(self.lattice):
            nodes = self.lattice[n]

            for node in nodes:
                if node.node_type == Node.ADDRESS:
                    self.node_types[n] = Node.ADDRESS
                    break
                elif node.node_type == Node.GEOWORD:
                    self.node_types[n] = Node.GEOWORD

            n += 1

        logger.debug("ノード種別リスト: {}".format(self.node_types))

    def increment_counter(self):
        """
        カウンターを次に進めます。
        """
        positions = []
        pos = 0

        # ラティス上で地名語・住所ノード候補を含む位置のリストを作成
        # 住所ノードが選択されている場合は住所に含まれる要素はスキップ
        while pos < len(self.lattice):
            i = self.counters[pos]
            node = self.lattice[pos][i]
            next_pos = pos + 1

            if node.node_type == Node.ADDRESS:
                positions.append(pos)
                has_non_address_node = False
                for _node in self.lattice[pos]:
                    if _node.node_type != Node.ADDRESS:
                        has_non_address_node = True
                        break

                if has_non_address_node:
                    # この形態素には住所ノード以外も存在するので
                    # 住所が終わる位置までスキップ
                    next_pos = pos + len(node.morphemes)

            elif node.node_type == Node.GEOWORD:
                positions.append(pos)

            pos = next_pos

        # 位置のリストの最後尾から、カウンターを 1 増やす
        # 候補の数を超えた場合は 0 に戻し、
        # 一つ手前の位置でインクリメントを継続する
        while len(positions) > 0:
            pos = positions.pop()
            i = self.counters[pos] + 1
            if i < len(self.lattice[pos]):
                self.counters[pos] = i
                return
            else:
                self.counters[pos] = 0

        # インクリメントできなかった = 最後の候補に到達した場合
        # カウンターの先頭を -1 にセット
        self.counters[0] = -1


class RankedResults(object):
    """
    ラティス表現から、指定したメソッドで計算したスコアの高いものから
    順に並べたパス表現を作成します。

    スコアリングに独自のメソッドを利用する場合は ``scoring_method`` で指定してください。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.linker import RankedResults
    >>> api.init()
    >>> rr = RankedResults(max_results=5)
    >>> for x in rr.get(api.analyze('福島は大阪から2分です。')):
    ...   (x['score'], [n.simple() for n in x['result']])
    ...
    (46, ["福島(GEOWORD:['西日本旅客鉄道', '大阪環状線'])", 'は(NORMAL)', "大阪(GEOWORD:['西日本旅客鉄道', '東海道線'])", 'から(NORMAL)', '2(NORMAL)', '分(NORMAL)', 'です(NORMAL)', '。(NORMAL)'])
    (46, ["福島(GEOWORD:['西日本旅客鉄道', '大阪環状線'])", 'は(NORMAL)', "大阪(GEOWORD:['西日本旅客鉄道', '大阪環状線'])", 'から(NORMAL)', '2(NORMAL)', '分(NORMAL)', 'です(NORMAL)', '。(NORMAL)'])
    (41, ["福島(GEOWORD:['阪神電気鉄道', '本線'])", 'は(NORMAL)', "大阪(GEOWORD:['西日本旅客鉄道', '東海道線'])", 'から(NORMAL)', '2(NORMAL)', '分(NORMAL)', 'です(NORMAL)', '。(NORMAL)'])
    (41, ["福島(GEOWORD:['阪神電気鉄道', '本線'])", 'は(NORMAL)', "大阪(GEOWORD:['西日本旅客鉄道', '大阪環状線'])", 'から(NORMAL)', '2(NORMAL)', '分(NORMAL)', 'です(NORMAL)', '。(NORMAL)'])
    (36, ["福島(GEOWORD:['福島交通', '飯坂線'])", 'は(NORMAL)', "大阪(GEOWORD:['西日本旅客鉄道', '東海道線'])", 'から(NORMAL)', '2(NORMAL)', '分(NORMAL)', 'です(NORMAL)', '。(NORMAL)'])

    Attributes
    ----------
    scoring_class : class instance
        スコアリングを行なうクラス。
    scoring_options : any
        スコアリングクラスの初期化に渡すオプションパラメータ。
    scorer : service.ScoringClass instance
        スコアリングを行なうクラスインスタンス。
    max_results : int
        保持する結果の最大数。
    """

    def __init__(self, scoring_class=None, scoring_options=None,
                 max_results=5, max_combinations=None):
        """
        Parameters
        ----------
        scoring_class : class, optional
            パスのスコアとノード間のスコアを計算する関数を持つ
            スコアリングクラス。
            指定しない場合、``pygeonlp.api.scoring`` モジュール内の
            ``ScoringClass`` が利用されます。
        scoring_options : any, optional
            スコアリングクラスの初期化に渡すオプションパラメータ。
        max_results : int, optional
            保持する結果の最大数を指定します（デフォルト = 5）。
        max_combinations : int, optional
            ノード候補の組み合わせ数の上限値。これを超える組み合わせが
            可能な入力が与えられた場合は例外 LinkerError を発生します。
            デフォルト値は linker.MAX_COMBINATIONS です。
        """
        self.scoring_class = scoring_class
        self.max_results = max_results
        self.max_combinations = max_combinations

        if self.scoring_class is None:
            from .scoring import ScoringClass
            self.scorer = ScoringClass(scoring_options)
        else:
            self.scorer = scoring_class(scoring_options)

        if self.max_combinations is None:
            self.max_combinations = MAX_COMBINATIONS

    def count_combinations(self, lattice):
        """
        ラティス形式の入力に対し、組み合わせたパス表現の個数を計算します。

        Parameters
        ----------
        lattice : list
            入力となるラティス表現。

        Return
        ------
        int
            組み合わせの数。
        """
        n = 1
        for i in lattice:
            n *= len(i)
            if n > 2147483647:
                break

        return n

    def get(self, lattice):
        """
        ラティス表現を入力として、スコアリングと並べ替えを行ないます。

        Parameters
        ----------
        lattice : list
            入力となるラティス表現。

        Return
        ------
        list
            スコアを 'score', パス表現の解析結果を 'result' に持つ
            dict のリスト。
            スコア降順にソートされ、最大 max_results 個の要素を含みます。
        """
        results = []
        combination = self.count_combinations(lattice)
        if combination > self.max_combinations:
            raise LinkerError(
                "組み合わせ数 {} がしきい値 {} を超えています。".format(
                    combination, self.max_combinations))

        lr = LinkedResults(lattice)
        for path in lr:
            score = self.scorer.path_score(path)
            new_record = {
                "score": score,
                "result": path,
            }
            simple_repr = ''.join([x.simple() for x in path])
            logger.debug("{} => {}".format(simple_repr, score))
            logger.debug("next:{}".format(lr.counter()))

            # スコアが高いものから順に最大 max_results 個の結果を保持する
            n = len(results)
            if n == 0:
                results.append(new_record)
                continue

            while n > 0:
                if results[n - 1]['score'] > score:
                    results.insert(n, new_record)
                    break

                n -= 1
                if n == 0:
                    results.insert(n, new_record)

            results = results[0:self.max_results]

        return results

    def as_dict(self, lattice):
        """
        ``get()`` と同じ処理を行ないますが、結果に含まれるノードの情報を
        JSON に変換可能な dict に変換してから返します。

        Parameters
        ----------
        lattice : list
            入力となるラティス表現。

        Return
        ------
        list
            ``get()`` の出力結果を JSON 変換可能な形式に変換したリスト。
        """
        results = []
        for r in self.get(lattice):
            score = r['score']
            node_list = r['result']
            dict_list = [x.as_dict() for x in node_list]
            results.append({
                "score": score,
                "result": dict_list,
            })

        return results

    def as_geojson(self, lattice):
        """
        ``get()`` と同じ処理を行ないますが、結果に含まれるノードの情報を
        GeoJSON FeatureCollection に変換可能な dict に変換してから返します。

        Parameters
        ----------
        lattice : list
            入力となるラティス表現。

        Return
        ------
        list
            ``get()`` の出力結果を GeoJSON 変換可能な形式に変換したリスト。
        """
        results = []
        for r in self.get(lattice):
            score = r['score']
            node_list = r['result']
            features = [x.as_geojson() for x in node_list]
            results.append({
                "score": score,
                "geojson": {
                    "type": "FeatureCollection",
                    "features": features,
                },
            })

        return results

    @staticmethod
    def collect_geowords(result):
        """
        パス表現の結果に含まれる地名語のセットを返します。

        処理結果に含まれる地名語だけを列挙する場合に利用する簡易メソッドです。
        """
        geowords = []
        for node in result:
            if node.node_type == Node.GEOWORD:
                geowords.append(node)

        return geowords

    @staticmethod
    def collect_addresses(result):
        """
        パス表現の結果に含まれる住所セットを返します。

        処理結果に含まれる住所だけを列挙する場合に利用する簡易メソッドです。
        """
        addresses = []
        for node in result:
            if node.node_type == Node.ADDRESS:
                addresses.append(node)

        return addresses
