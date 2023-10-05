import copy
import logging
import re

from pygeonlp.api.node import Node

logger = logging.getLogger(__name__)


class FilterError(RuntimeError):
    """
    フィルタ処理の際に例外が起こると、このクラスが発生します。
    """
    pass


class Filter(object):
    """
    ラティス表現を入力として、条件に一致しないノードを除外した結果を
    ラティス表現として出力するフィルタ機能の基底クラス。

    このクラスは全てのフィルタに共通の機能を提供するものなので、
    派生クラスを利用してください。
    """

    def __init__(self, **kwargs):
        """
        フィルタを初期化します。
        初期化の内容は派生するクラスごとに拡張する必要があります。

        Attributes
        ----------
        when_all_failed : str
            全ての候補が条件を満たさなかった場合の挙動を指定します。

            "return_all"
                全ての候補をそのまま残します。
            "convert_to_normal"
                '名詞・固有名詞・地域・一般' ノードを1つ作成して返します。
        """
        self.when_all_failed = 'return_all'

    def apply(self, input, **kwargs):
        """
        入力データの各形態素に対して ``apply_filter()`` を適用し、
        合格したノードだけを残した結果を返します。

        ``apply_filter()`` では一つの形態素に対応する候補ノードの
        リストに含まれる情報のみを利用してフィルタ処理を行なうため、
        前後の形態素を見て判定する必要があるフィルタクラスでは、
        ``apply()`` メソッドを上書きする必要があります。

        Parameters
        ----------
        input : list
            入力となるラティス表現。

        Returns
        -------
        list
            ``filter_func()`` を適用して要素を削除されたラティス表現。
        """
        output = [None] * len(input)
        for i in range(len(input)):
            candidates = input[i]
            output[i] = self.apply_filter(candidates, **kwargs)

            if len(output[i]) > 0:
                continue

            # 1つも候補が残らなかった場合
            if self.when_all_failed == 'return_all':
                # 入力の候補リストをそのまま残す
                output[i] = input[i]
                continue

            if self.when_all_failed == 'convert_to_normal':
                # 非地名語ノードがあればそれを採用する
                for node in candidates:
                    if node.node_type == Node.NORMAL:
                        output[i] = [node]
                        break

                if len(output[i]) > 0:
                    continue

                # 名詞・固有名詞・地域・一般ノードを作成して候補とする
                new_node = copy.copy(candidates[0])
                new_node.node_type = Node.NORMAL
                new_node.morphemes.update({
                    "conjugated_form": "*",
                    "conjugation_type": "*",
                    "pos": "名詞",
                    "subclass1": "固有名詞",
                    "subclass2": "地域",
                    "subclass3": "一般",
                })
                new_node.geometry = None
                new_node.prop = None
                output[i] = [new_node]
                continue

            raise FilterError(
                "定義されていない動作:'{}'".format(self.when_all_failed))

        return output

    def apply_filter(self, candidates, default=None, **kwargs):
        '''
        ラティス表現の1つの形態素に対する複数の候補ノードに対して
        順番に ``filter_func()`` を適用し、条件に一致しないノードを
        削除した候補ノードのリストを返します。

        default で指定された地名語 ID を持つノードが条件に一致した場合、
        結果候補ノードリストの先頭に配置します。

        ``filter_func()`` では個々の候補ノードに含まれる情報のみを
        利用してフィルタへの合否判定処理を行なうため、
        1つの形態素に対する候補ノードを比較して最適なものを
        選択する必要があるフィルタクラスでは、
        ``apply_filter()`` メソッドを上書きする必要があります。

        Parameters
        ----------
        candidates : list
            候補ノードのリスト
        default : str, optional
            最優先候補としたいノードの geolod_id
        **kwargs
            キーワードパラメータ、派生クラスでは利用する可能性があります。

        Returns
        -------
        list
            条件に一致した候補ノードのリスト。
        '''
        top_candidate = None
        passed = []
        excluded = []

        for candidate in candidates:
            if self.filter_func(candidate):
                if candidate.prop is None:
                    # 地名語・住所以外の形態素
                    passed.append(candidate)
                    continue

                if top_candidate is None and \
                   'geolod_id' in candidate.prop and \
                   default == candidate.prop['geolod_id']:
                    top_candidate = candidate
                else:
                    passed.append(candidate)
            else:
                excluded.append(candidate)

        if top_candidate:
            passed.insert(0, top_candidate)

        return passed

    def filter_func(candidate):
        """
        候補ノードが条件に一致するかどうかを判定します。
        派生クラスでそれぞれ実装する必要があります。

        Parameters
        ----------
        candidate : Node
            判定する形態素ノード。

        Returns
        -------
        bool
            基底クラスでは常に True を返します。
        """
        return True

    def __call__(self, input):
        """
        クラスをメソッドのように呼びだせるようにするためのマジックメソッド。
        Filter(input) は Filter.apply(input) を実行します。
        """
        return self.apply(input)

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
        >>> api.filter.Filter.count_geowords(
        ...   parser.analyze_sentence('国会議事堂前まで歩きました。'))
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


class EntityClassFilter(Filter):
    """
    形態素ごとの候補ノード集合の中に、指定した固有名クラスと一致する地名語が
    含まれていれば、それ以外の候補は削除するフィルタ。
    テキストに含まれている地名語の固有名クラスが事前に分かっていて、
    そのクラスに一致する地名語だけを抽出したい場合などに利用します。

    候補ノード集合の中に一致する地名語が無い場合は候補リストをそのまま返します。
    """

    def __init__(self, ne_class, **kwargs):
        """
        Parameters
        ----------
        ne_class : str
            このフィルタで選択したい固有名クラスを表す正規表現文字列。
            例： r'国/?.*'
        """
        super().__init__(**kwargs)
        self.when_all_failed = 'convert_to_normal'
        self.re_ne_class = re.compile(ne_class)

    def filter_func(self, candidate, **kwargs):
        """
        Parameters
        ----------
        candidate : Node
            対象の形態素ノード

        Returns
        -------
        bool
            ne_class に一致する場合は True,
            一致しない場合は Falase
        """
        prop = candidate.prop
        if prop is None:
            # 非地名語ノードも削除する
            # 条件に該当する地名語ノードが無い場合は、
            # when_all_failed の指定により全てのノードが復元される
            return False

        ne_class = prop.get('ne_class', None)
        if ne_class is None:
            return False

        return self.re_ne_class.match(ne_class)


class GreedySearchFilter(Filter):
    """
    前後の地名語との関係を見て最もスコアが高くなる地名語を
    1 つだけ残し、それ以外は削除するフィルタ。

    ただし同点となる地名語が複数存在する場合は複数の候補を残します。
    """

    def __init__(self, scoring_class=None, scoring_options=None, **kwargs):
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
        """
        super().__init__(**kwargs)
        self.when_all_failed = 'return_all'

        if scoring_class is None:
            from .scoring import ScoringClass
            self.scorer = ScoringClass(scoring_options)
        else:
            self.scorer = scoring_class(scoring_options)

    def apply(self, input, **kwargs):
        """
        このフィルタは前後の形態素ノードを調べて地名語間の関係を計算するため、
        ``apply()`` をオーバーライドします。

        Parameters
        ----------
        input : list
            入力となるラティス表現。

        Returns
        -------
        list
            フィルタを適用したラティス表現。
        """
        output = [None] * len(input)

        # 地名語と住所を集めたリスト geowords_pile を作る
        # geowords_pile = [[pos, [geoword]]], pos はラティスでの位置
        geowords_pile = []
        n = 0
        while n < len(input):
            nodes = input[n]
            geowords = []
            for node in nodes:
                if node.node_type == Node.ADDRESS:
                    geowords.clear()
                    n += len(node.morphemes) - 1
                    break
                elif node.node_type == Node.GEOWORD:
                    geowords.append(node)

            if len(geowords) > 0:
                geowords_pile.append([n, geowords])

            n += 1

        for k, geowords in enumerate(geowords_pile):
            candidates = ",".join([x.simple() for x in geowords[1]])
            logger.debug("{}: {}".format(k, candidates))

        # ラティスの i 番目のノード集合を最適なものに絞り込む
        pile_index = 0
        for i in range(len(input)):
            if pile_index == len(geowords_pile) or \
                    i < geowords_pile[pile_index][0]:
                # 地名語・住所を含まない場合はそのまま
                output[i] = input[i]
                continue

            if len(input[i]) == 1:
                # 候補が一つしか無い場合もそのまま
                output[i] = input[i]
                pile_index += 1
                continue

            dt = 1  # チェックする前後の範囲
            best_nodes = input[i]
            while dt < len(geowords_pile):
                # pile_index - dt 番目の地名語集合を手がかりとする
                candidates = ",".join([x.simple() for x in input[i]])

                k = pile_index - dt
                if k >= 0:
                    hint_geowords = geowords_pile[k][1]
                    hints = ",".join([x.simple() for x in hint_geowords])
                    best_nodes = self._get_best(input[i], hint_geowords)
                    if len(best_nodes) == 1:
                        logger.debug("'{}' を選択（候補:{}, ヒント:{}）".format(
                            best_nodes[0].simple(), candidates, hints))
                        break

                k = pile_index + dt
                if k < len(geowords_pile):
                    hint_geowords = geowords_pile[k][1]
                    hints = ",".join([x.simple() for x in hint_geowords])
                    best_nodes = self._get_best(input[i], hint_geowords)
                    if len(best_nodes) == 1:
                        logger.debug("'{}' を選択（候補:{}, ヒント:{}）".format(
                            best_nodes[0].simple(), candidates, hints))
                        break

                dt += 1

            output[i] = best_nodes
            pile_index += 1

        return output

    def _get_best(self, nodes, hint_geowords):
        """
        形態素ノードリストの中から、前方・後方の地名語との関係が
        最も強いノードを返します。

        同じスコアになるノードが複数存在する場合は全て返します。

        Parameters
        ----------
        nodes : list
            形態素ノードのリスト
        hint_geowords : list
            地名語ノードまたは住所ノードを1つ以上含む、関係を調べる対象の
            ノードリスト

        Returns
        -------
        list
            関係が最も強い形態素ノード、または元のノードのリスト
        """
        scores = [[node, 0.0] for node in nodes]

        for i0 in range(len(nodes)):
            for i1 in range(len(hint_geowords)):
                scores[i0][1] += self.scorer.node_relation_score(
                    nodes[i0], hint_geowords[i1])

        results = []
        max_score = 0.0
        for score in scores:
            if score[1] > max_score:
                results = [score[0]]
                max_score = score[1]
            elif score[1] == max_score:
                results.append(score[0])

        return results


class InputBasedFilter(Filter):
    """
    入力によって対象とする地名語クラスやパス表現の選択ロジックを
    変更して、実時間で処理可能な候補に絞り込むフィルタ。
    """

    def __init__(self, **kwargs):
        """
        フィルタを初期化します。
        このクラスには指定するパラメータはありません。
        """
        super().__init__(**kwargs)

    def apply(self, lattice, **kwargs):
        """
        入力ベースフィルタを適用します。

        Parameters
        ----------
        lattice: list
            入力となるラティス表現。

        Returns
        -------
        list
            フィルタ適用後のラティス表現。

        Note
        ----
        時刻表や地震速報など、特定の地名語クラスを持つ地名が
        高い密度で出現する文字列を解析する場合、候補となるクラスを
        絞り込んで解析処理時間を短縮し、精度を向上させます。
        """
        filters = []

        search_plan = "exhaustive"
        gstat = Filter.count_geowords(lattice)
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
            # 鉄道駅リスト（交通情報や時刻表など）
            filters.append(EntityClassFilter(r'(市区町村|鉄道施設)/?.*'))
            search_plan = "greedy"

        if search_plan == "greedy":
            # 地震速報や時刻表など同種の地名語が多数出現する場合
            filters.append(GreedySearchFilter())

        # 選択したフィルタを適用
        for f in filters:
            lattice = f(lattice)

        return lattice
