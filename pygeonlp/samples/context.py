"""
コンテキスト情報を利用した geoparsing のサンプル

地理的範囲と固有名クラスごとの優先度をもつ「コンテキスト情報」を
利用するカスタムクラスの実装例です。

Usage: python context.py

以下のクラスを実装し、サンプルテキストを解析した結果を表示します。

- コンテキスト情報の範囲内かつ優先度０以上の固有名クラスを持つ
  地名語だけを残す ContextFilter
- 固有名クラスに応じてスコアを乗じる ContextScoringClass
- ContextScoringClass を利用する ContextEvaluator
- ContextFilter, ContextEvaluator を利用する ContextWorkflow
"""

from logging import getLogger
import os
import re
from typing import Optional, Union

from pygeonlp.api.linker import Evaluator
from pygeonlp.api.filter import Filter
from pygeonlp.api.node import Node
from pygeonlp.api.scoring import ScoringClass
from pygeonlp.api.spatial_filter import GeoContainsFilter
from pygeonlp.api.workflow import Workflow

logger = getLogger(__name__)


class Context(object):
    """
    コンテキスト情報を保持するクラス

    Attributes
    ----------
    target_area: str, bytes, PathLike, None
        このコンテキストが対象とする空間的範囲を表す GeoJSON を
        含むファイルパスまたは URL
    priorities: dict
        固有名クラスごとの優先度
    priorities_with_prefix: dict
        固有名クラスごとの優先度（prefix を含む場合）
    priorities_with_suffix: dict
        固有名クラスごとの優先度（suffix を含む場合）
    """

    def __init__(self):
        """
        コンテキスト情報を初期化
        """
        self.target_area = None
        self.priorities = {}
        self.priorities_with_prefix = {}
        self.priorities_with_suffix = {}

    def setArea(self, geojson_or_url: Union[str, bytes, os.PathLike]):
        """
        空間的範囲をセットする

        Parameters
        ----------
        geojson_or_url: str, bytes, PathLike
            空間的範囲を表す GeoJSON または
            GeoJSON を含む URL
        """
        self.target_area = geojson_or_url

    def getPriority(self, node: Node) -> float:
        """
        指定した形態素ノードに対応する
        このコンテキストでの優先度を返す

        Parameters
        ----------
        node: pygeonlp.api.node.Node
            形態素ノード

        Return
        ------
        float
            優先度
        """
        if node.node_type == Node.ADDRESS:
            # 住所は常に優先度最高 = 1
            return 1.0

        if node.node_type == Node.NORMAL:
            # 非地名語は常に優先度最低 = 0
            return 0.0

        re_ne_class = re.compile(node.prop.get('ne_class'))

        # ノードが prefix, suffix を含むかどうかを判定
        body_pos = node.surface.index(node.prop.get('body'))
        has_prefix = body_pos > 0
        has_suffix = (body_pos +
                      len(node.prop.get('body'))) < len(node.surface)

        if has_suffix:
            # suffix を含む場合の ne_class の優先度を取得
            for ne_class, priority in self.priorities_with_suffix.items():
                if re_ne_class.match(ne_class):
                    return priority

        if has_prefix:
            # prefix を含む場合の ne_class の優先度を取得
            for ne_class, priority in self.priorities_with_prefix.items():
                if re_ne_class.match(ne_class):
                    return priority

        # prefix, suffix を含まない場合の ne_class の優先度を取得
        for ne_class, priority in self.priorities.items():
            if re_ne_class.match(ne_class):
                return priority

        # 設定されていない場合は 0.5
        return 0.5


class ContextFilter(Filter):
    """
    コンテキスト情報を利用して地名語候補を選択するフィルタクラス

    Attributes
    ----------
    context: Context
        利用するコンテキスト情報
    """

    def __init__(self, context: Optional[Context] = None):
        """
        Note
        ----
        このフィルタは、一致する候補が見つからない場合は
        非地名語の固有名詞として処理します。
        """
        self.when_all_failed = 'convert_to_normal'
        self.set_context(context)

    def set_context(self, context: Optional[Context] = None):
        """
        コンテキスト情報をセットする

        Parameters
        ----------
        context: Context, optional
            利用するコンテキスト情報。

        Note
        ----
        コンテキスト情報が空間範囲を持っている場合、
        範囲内の候補を選択するための GeoContainsFilter を作成し、
        self._filter に保持します。
        """
        self.context = context

        if self.context and self.context.target_area:
            self._filter = GeoContainsFilter(
                self.context.target_area)
        else:
            self._filter = None

    def apply_filter(self, candidates, **kwargs):
        """
        Filter.apply_filter() をオーバーライド

        ラティス表現の1つの形態素に対する候補ノード集合
        candidates のうち、コンテキストの空間範囲に含まれ、
        かつ優先度が定義されている地名語クラスを持つノードを
        残します。それ以外は除去します。

        Parameters
        ----------
        candidates : list[Node]
            候補ノードのリスト。
        **kwargs
            キーワードパラメータ。このクラスでは利用しません。

        Returns
        -------
        list[Node]
            条件に一致した候補ノードのリスト。
        """
        if self._filter:
            # 空間範囲が指定されていれば絞り込む
            filtered_candidates = []
            for candidate in candidates:
                if self._filter.filter_func(candidate):
                    filtered_candidates.append(candidate)
        else:
            filtered_candidates = candidates

        # 優先度がセットされている候補だけを含むリストを作成する
        results = []
        for candidate in filtered_candidates:
            priority = self.context.getPriority(node=candidate)
            if priority > 0.0:
                results.append(candidate)

        return results


class ContextScoringClass(ScoringClass):
    """
    コンテキスト情報を利用してパスのスコアを計算する
    スコアリングクラス

    パスに地名語が含まれている場合、コンテキスト情報で
    定義されている地名語クラスの優先度を乗算します。
    """

    def __init__(self, context: Context):
        super().__init__()
        self.context = context

    def path_score(self, path):
        """
        デフォルト実装のスコアにコンテキスト情報の
        優先度を乗算します。
        """
        score = super().path_score(path)

        geowords = Evaluator.collect_geowords(path)
        for geoword in geowords:
            score *= self.context.getPriority(geoword)
            if score == 0.0:
                break

        return score


class ContextEvaluator(Evaluator):
    """
    コンテキスト情報を利用して最適な候補を返す Evaluator
    """

    def __init__(self, context: Context, max_results: int = 5):
        super().__init__(
            scoring_class=ContextScoringClass(context),
            max_results=max_results)


class ContextWorkflow(Workflow):
    """
    コンテキスト情報を利用してテキスト解析を行なう Workflow
    """

    def __init__(self, context,
                 db_dir=None, address_regex=None, jageocoder=None,
                 max_results=5):
        self.max_results = max_results
        super().__init__(
            db_dir=db_dir,
            address_regex=address_regex,
            jageocoder=jageocoder)

        self.set_context(context)

    def set_context(self, context):
        """
        利用するコンテキスト情報をセットします

        Parameters
        ----------
        context: Context
            利用するコンテキスト情報

        Note
        ----
        セットされたコンテキスト情報を利用して、
        filters と evaluator を作り直します。
        """
        self.context = context
        self.filters = [ContextFilter(context)]
        self.evaluator = ContextEvaluator(context, self.max_results)


if __name__ == '__main__':
    import logging
    from pygeonlp.api.workflow import Workflow
    from pygeonlp.api.devtool import pp_geojson

    logging.basicConfig(level=logging.WARNING)
    with open(os.path.join(
            os.path.dirname(__file__),
            'nihonkai_engan.geojson'), 'r') as f:
        geojson = f.read()

    context_heavy_snowfall_20220113 = Context()
    context_heavy_snowfall_20220113.setArea(geojson)
    context_heavy_snowfall_20220113.priorities = {
        r'道路施設/バス停': 0.0,
        r'道路施設/.*': 0.7,
        r'鉄道施設/.*': 0.6,
        r'市区町村': 0.8,
    }
    context_heavy_snowfall_20220113.priorities_with_suffix = {
        r'道路施設/.*': 1.0,
        r'鉄道施設/.*': 1.0,
        r'市区町村': 1.0,
    }

    workflow = ContextWorkflow(
        context_heavy_snowfall_20220113,
        max_results=1)

    article = """北海道 NEWS WEB
https://www3.nhk.or.jp/sapporo-news/20220113/7000042131.html

大雪の影響続く ＪＲ各線で計１９１本が運休

01月13日　11時29分

ＪＲ北海道は、１３日も大雪の影響で一部の特急や普通列車などあわせて１９１本の運休を決めています。

ＪＲ北海道によりますと、１３日も大雪の影響で４つの在来線で運転の見合わせが出ていて、午前１１時現在であわせて１９１本が運休、または運休を決めています。
▼室蘭線は、岩見沢と苫小牧の間で始発から午後３時ごろまで、▼宗谷線は、名寄と南稚内の間で始発から午後２時半ごろまで、南稚内と稚内の間で始発から終日、運転を見合わせます。
また▼石勝線は、南千歳と新夕張の間で午後５時ごろまで、▼釧網線も、釧路と網走の間で午後２時ごろまでそれぞれ始発から運転を見合わせます。
１３日、これまでに運休が決まっている特急は、札幌と釧路を結ぶ「おおぞら」や稚内と旭川を結ぶ「サロベツ」など合わせて１７本に上っています。
このほか在来線では▼函館・千歳線が札幌と新千歳空港を結ぶ快速エアポート３５本などあわせて６３本、▼函館線で３８本、▼根室線で２０本、▼室蘭線で１２本、▼釧網線で９本、▼宗谷線で９本、▼石北線で８本、▼石勝線で８本、▼学園都市線で７本が運休となっています。
ＪＲ北海道は、今後の天候によってはさらに運休が増えるおそれもあるとしてホームページで最新の情報を確認するよう呼びかけています。
"""
    # 結果の GeoJSON を pp_geojson() で簡易表示します
    pp_geojson(workflow.geoparse(article))
    # GeoJSON で出力するには json.dumps() を利用します
    # import json
    # print(json.dumps(
    #     workflow.geoparse(article),
    #     indent=2, ensure_ascii=False))
