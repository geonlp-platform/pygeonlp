"""
scoring モジュールは、一通りのジオパージング処理を行なうために必要最小限の、
スコアリング処理の実装をまとめています。
十分な精度が得られない場合、用途に応じてチューニングを行なうか、
別の手法を実装して利用してください。
"""

from logging import getLogger

from pygeonlp.api.linker import RankedResults
from pygeonlp.api.node import Node

logger = getLogger(__name__)


class ScoringClass(object):

    def __init__(self, options=None):
        """
        スコアリングクラスの初期化を行ないます。

        独自のスコアリング手法を実装したクラスを利用して
        アノテーション結果をランキングしたい場合、
        このクラスから派生したクラスを定義し、
        pygeonlp.api.geoparse() を呼びだす際に scoring_class パラメータに
        利用するクラス名を指定してください。

        Parameters
        ----------
        options : any
            パスのスコアリングやノード間のスコアを計算するときに
            利用するパラメータです。

            geoparse() の ``scoring_options`` で指定した値が入ります。
            デフォルト実装では int の値をとり、
            地名語間の関係や距離を計算する際に、いくつ先の形態素まで
            照合するかを指定します。デフォルトは5です。
            地名語や住所の候補を含まない形態素はカウントしません。

            独自のクラスを派生する場合には任意の型が利用できます。
        """
        self.options = options

    def path_score(self, path):
        """
        パス表現の結果を一つ受け取り、スコアを計算して返すデフォルト実装です。

        Parameters
        ----------
        path : list of Node
            解析結果候補のパス表現。

        Returns
        -------
        int
            与えられたパスを評価したスコアを返します。
            値が大きいパスほど geoparse() の結果で上位候補として返されます。

        Notes
        -----
        次のように得点を計算しています。

        - 地名語・住所を候補として全く含まない形態素が存在する場合

            +形態素数 ×1点（地名語か非地名語か不明な形態素は非地名語を優先）

        - 全ての候補の中に住所ノード候補が含まれている場合

            +住所階層数（'東京都/千代田区'なら2）×10点

        - 全ての候補の中に含まれる地名語ノード候補に、
          同じ固有名クラスが2回以上出現する場合

            +出現回数 ×10点

        - ある形態素に地名語ノード候補が含まれる場合

            nlookup 先までの形態素に含まれる地名語・住所ノード候補との
            関係によるスコアを node_relation_score() で計算し加算
        """
        if self.options:
            nlookup = self.options
        else:
            nlookup = 5

        if not isinstance(nlookup, int):
            raise RuntimeError(
                "オプションパラメータは整数値で指定してください。")

        score = 0
        geowords = RankedResults.collect_geowords(path)
        addresses = RankedResults.collect_addresses(path)
        geonodes = geowords + addresses
        score += len(path) - len(geonodes)  # 住所・地名語以外は +1

        # 住所による得点を計算
        for address in addresses:
            score += 10 * len(address.morphemes)  # 住所階層数 * 10

        # 同じ固有名クラスが複数含まれていると得点
        ne_classes = {}
        for geoword in geowords:
            ne_class = geoword.prop['ne_class']
            if ne_class in ne_classes:
                ne_classes[ne_class] += 1
            else:
                ne_classes[ne_class] = 1

        for ne_class, freq in ne_classes.items():
            if freq > 1:
                logger.debug("固有名クラス {} が {} 件存在 (*10)".format(
                    ne_class, freq))
                score += freq * 10

        # ノード間の距離を計算
        # nlookup ノード先まで確認する
        for i0 in range(len(path)):
            n0 = path[i0]
            if n0.node_type == Node.NORMAL:
                continue

            for i1 in range(i0 + 1, len(path)):
                n1 = path[i1]
                if n1.node_type == Node.NORMAL:
                    continue

                score += self.node_relation_score(n0, n1)
                nlookup -= 1
                if nlookup <= 0:
                    break

        return score

    def node_relation_score(self, node0, node1):
        """
        node クラスのインスタンス node0 と node1 との関係による
        スコアを計算するデフォルト実装です。
        関係が強いノードほど高いスコアを返します。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> from pygeonlp.api.scoring import ScoringClass
        >>> api.init()
        >>> s = ScoringClass()
        >>> s.node_relation_score(api.analyze('国会議事堂前')[0][0],
        ...   api.analyze('永田町')[0][0])
        20

        Notes
        -----
        スコアは以下のように計算しています。

        - どちらかのノードが地名語でも住所でもない（NORMAL）場合
            0 点
        - どちらのノードも地名語で、固有名クラスが一致する場合（同クラス）
            +10 点
        - どちらのノードがもう一方の hypernym にふくまれる場合（親子関係）
            +5 点
        - 両方のノードの hypernym が1つ以上一致する場合（兄弟関係）
            +5 点
        - ノード間の距離（単位は degree）を計算し、
            0.2度以下の場合は +5 点、それ以上離れている場合は +1/距離を加算
        """
        if node0.node_type == Node.NORMAL or node1.node_type == Node.NORMAL:
            return 0

        score = 0

        if node0.node_type == Node.GEOWORD and node1.node_type == Node.GEOWORD:
            # 固有名クラスの一致度
            if node0.prop['ne_class'] == node1.prop['ne_class']:
                score += 10

        # 上位下位関係
        hypernym_node0 = None
        hypernym_node1 = None
        if node0.node_type == Node.GEOWORD:
            hypernym_node0 = set(node0.prop.get('hypernym', []))
            if hypernym_node0 & node1.get_notations():
                score += 5

        if node1.node_type == Node.GEOWORD:
            hypernym_node1 = set(node1.prop.get('hypernym', []))
            if hypernym_node1 & node0.get_notations():
                score += 5

        if hypernym_node0 and hypernym_node1 and \
           hypernym_node0 & hypernym_node1:
            # 兄弟関係
            score += 5

        # 相互距離
        try:
            dist = node0.distance(node1)
            if dist < 10000.0:  # 10km 以下
                score += 5
            else:
                # 50km までは 1 点追加
                score += int(50000.0 / dist)
        except RuntimeError:
            pass

        logger.debug("{} と {} のスコア => {}".format(
            node0.simple(), node1.simple(), score))

        return score
