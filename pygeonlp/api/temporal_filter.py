"""
このモジュールは、特定の時間範囲内に存在した地名語だけを抽出するといった
時間フィルタを実装しています。
"""

import datetime
from logging import getLogger
import re

from pygeonlp.api.filter import Filter, FilterError

logger = getLogger(__name__)


class TemporalFilter(Filter):
    """
    時間フィルタの基底クラス。

    時間フィルタは、形態素に対応する地名語ノード候補のうち、
    条件に一致するものを残し、一致しないものを削除します。
    全ての候補が条件に一致しない場合、品詞情報として固有名詞を持つ
    一般ノードを一つ作成して置き換えます。

    時間フィルタでは、地名語ノードの prop.valid_from および prop.valid_to を
    そのノードが存在する期間とします。

    - valid_from が設定されていない場合
        無限の過去から存在していたとみなします。
    - valid_to が設定されていない場合
        無限の未来まで存在しているとみなします。

    Attributes
    ----------
    duration : (datetime.date, datetime.date)
        期間の開始日と終了日のタプル。
    """

    def __init__(self, date_from, date_to=None, **kwargs):
        """
        Parameters
        ----------
        date_from : str, datetime.date, datetime.datetime
            期間の開始日時。
        date_to : str, datetime.date, datetime.datetime, optional
            期間の終了日時。

        Notes
        -----
        date_to を省略した場合、 date_from が表す一時点が期間になります。
        たとえば TimeExistsFilter('2001-01-01') は、 2001年1月1日時点に
        存在していた地名語ノードを残すフィルタになります。
        """
        super().__init__()
        self.duration = self.__class__.get_duration_from_dates(
            date_from, date_to)
        self.when_all_failed = 'convert_to_normal'

    @classmethod
    def get_date_from_isostr(cls, datestr):
        """
        ISO フォーマット、または類似したフォーマットから date に相当する部分を取得します。

        Parameters
        ----------
        datestr : str
            日付または日時文字列。

        Returns
        -------
        datetime.date
            日付部分を表す date オブジェクト。

        """
        if datestr is None or datestr == '':
            return None

        re_date = r"(\d{4})[/\-\s](\d{1,2})[/\-\s](\d{1,2})"

        match = re.match(re_date, datestr)
        if not match:
            raise FilterError("'{}' は日付として解析できません".format(
                datestr))

        ymd = match.groups()
        date = datetime.date(int(ymd[0]), int(ymd[1]), int(ymd[2]))
        return date

    @classmethod
    def get_duration_from_dates(cls, datestr0, datestr1):
        """
        2つの日付文字列から期間を表す tuple を取得します。

        Parameters
        ----------
        datestr0 : str, datetime.date, datetime.datetime
            期間の開始日時を指定します。
        datestr1 : str, datetime.date, datetime.datetime
            期間の終了日時を指定します。

        Returns
        -------
        tuple
            期間の開始日時と終了日時を表す datetime.date オブジェクトの
            tuple を返します。
        """
        if isinstance(datestr0, (datetime.date, datetime.datetime)):
            date0 = datestr0
        elif isinstance(datestr0, str):
            date0 = cls.get_date_from_isostr(datestr0)
        else:
            raise TypeError(("1番目のパラメータの型は "
                             "str, datetime.date, datetime.datetime"
                             " のいずれかで指定してください。"))

        if not datestr1:
            date1 = date0
        else:
            if isinstance(datestr1, (datetime.date, datetime.datetime)):
                date1 = datestr1
            elif isinstance(datestr1, str):
                date1 = cls.get_date_from_isostr(datestr1)
            else:
                raise TypeError(("2番目のパラメータの型は "
                                 "str, datetime.date, datetime.datetime"
                                 " のいずれかで指定してください。"))

        if (date0 > date1):
            date0, date1 = date1, date0

        return (date0, date1)

    @classmethod
    def duration_from_candidate(cls, candidate):
        '''
        候補ノードの valid_from, valid_to から有効期間を表す
        tuple を取得する。
        valid_from, valid_to が含まれていない場合は None を返す。
        '''
        if candidate.prop is None:
            return None

        prop = candidate.prop
        date0 = cls.get_date_from_isostr(prop.get('valid_from', None))
        date1 = cls.get_date_from_isostr(prop.get('valid_to', None))

        return (date0, date1)


class TimeExistsFilter(TemporalFilter):
    """
    指定した時間範囲に存在していれば合格とするフィルタを作成します。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.temporal_filter import TimeExistsFilter
    >>> api.init()
    >>> tefilter = TimeExistsFilter('2000-01-01', '2001-01-01')
    >>> lattice = api.analyze('田無市と保谷市は2001年1月21日に合併して西東京市になりました。')
    >>> for nodes in lattice:
    ...     [x.simple() for x in nodes]
    ...
    ["田無市(GEOWORD:['東京都'])"]
    ['と(NORMAL)']
    ["保谷市(GEOWORD:['東京都'])"]
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ["西東京市(GEOWORD:['東京都'])"]
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    >>> lattice_filtered = tefilter(lattice)
    >>> # フィルタを適用すると「西東京市」が範囲外なので地名語候補から除外されます
    >>> for nodes in lattice_filtered:
    ...     [x.simple() for x in nodes]
    ...
    ["田無市(GEOWORD:['東京都'])"]
    ['と(NORMAL)']
    ["保谷市(GEOWORD:['東京都'])"]
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ['西東京市(NORMAL)']
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    """

    def filter_func(self, candidate):
        """
        時間範囲に存在していれば True を返します。

        Parameters
        ----------
        candidate : pygeonlp.api.node.Node
            検査対象となるノードオブジェクト。

        Returns
        -------
        bool
            フィルタの条件を満たせば True, 満たさなければ False を返します。
        """
        span = self.__class__.duration_from_candidate(candidate)
        if span is None:
            return True   # 期間を持たない候補は合格

        if span[0] and span[0] > self.duration[1]:
            return False

        if span[1] and span[1] < self.duration[0]:
            return False

        return True


class TimeBeforeFilter(TemporalFilter):
    """
    指定した時間範囲の開始時より前に存在していれば合格とするフィルタを返します。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.temporal_filter import TimeBeforeFilter
    >>> api.init()
    >>> tbfilter = TimeBeforeFilter('2000-01-01')
    >>> lattice = api.analyze('田無市と保谷市は2001年1月21日に合併して西東京市になりました。')
    >>> for nodes in lattice:
    ...     [x.simple() for x in nodes]
    ...
    ["田無市(GEOWORD:['東京都'])"]
    ['と(NORMAL)']
    ["保谷市(GEOWORD:['東京都'])"]
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ["西東京市(GEOWORD:['東京都'])"]
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    >>> lattice_filtered = tbfilter(lattice)
    >>> # フィルタを適用すると「西東京市」が範囲外なので地名語候補から除外されます
    >>> for nodes in lattice_filtered:
    ...     [x.simple() for x in nodes]
    ...
    ["田無市(GEOWORD:['東京都'])"]
    ['と(NORMAL)']
    ["保谷市(GEOWORD:['東京都'])"]
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ['西東京市(NORMAL)']
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    """

    def filter_func(self, candidate):
        """
        時間範囲の開始時より前に存在していれば True を返します。

        Parameters
        ----------
        candidate : pygeonlp.api.node.Node
            検査対象となるノードオブジェクト。

        Returns
        -------
        bool
            フィルタの条件を満たせば True, 満たさなければ False を返します。
        """
        span = self.__class__.duration_from_candidate(candidate)
        if span is None:
            return True   # 期間を持たない候補は合格

        if span[0] and span[0] > self.duration[0]:
            return False

        return True


class TimeAfterFilter(TemporalFilter):
    """
    指定した時間範囲の終了時より後に存在していれば合格とするフィルタを作成します。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.temporal_filter import TimeAfterFilter
    >>> api.init()
    >>> tafilter = TimeAfterFilter('2001-01-22')
    >>> lattice = api.analyze('田無市と保谷市は2001年1月21日に合併して西東京市になりました。')
    >>> for nodes in lattice:
    ...     [x.simple() for x in nodes]
    ...
    ["田無市(GEOWORD:['東京都'])"]
    ['と(NORMAL)']
    ["保谷市(GEOWORD:['東京都'])"]
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ["西東京市(GEOWORD:['東京都'])"]
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    >>> lattice_filtered = tafilter(lattice)
    >>> # フィルタを適用すると「田無市」「保谷市」が範囲外なので地名語候補から除外されます
    >>> for nodes in lattice_filtered:
    ...     [x.simple() for x in nodes]
    ...
    ['田無市(NORMAL)']
    ['と(NORMAL)']
    ['保谷市(NORMAL)']
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ["西東京市(GEOWORD:['東京都'])"]
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    """

    def filter_func(self, candidate):
        """
        時間範囲の開始時より前に存在していれば True を返します。

        Parameters
        ----------
        candidate : pygeonlp.api.node.Node
            検査対象となるノードオブジェクト。

        Returns
        -------
        bool
            フィルタの条件を満たせば True, 満たさなければ False を返します。
        """
        span = self.__class__.duration_from_candidate(candidate)
        if span is None:
            return True   # 期間を持たない候補は合格

        if span[1] and span[1] < self.duration[1]:
            return False

        return True


class TimeOverlapsFilter(TemporalFilter):
    """
    指定した時間範囲内に存在していれば合格とするフィルタを作成します。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.temporal_filter import TimeOverlapsFilter
    >>> api.init()
    >>> tofilter = TimeOverlapsFilter('2001-01-01', '2001-02-01')
    >>> lattice = api.analyze('田無市と保谷市は2001年1月21日に合併して西東京市になりました。')
    >>> for nodes in lattice:
    ...     [x.simple() for x in nodes]
    ...
    ["田無市(GEOWORD:['東京都'])"]
    ['と(NORMAL)']
    ["保谷市(GEOWORD:['東京都'])"]
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ["西東京市(GEOWORD:['東京都'])"]
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    >>> lattice_filtered = tofilter(lattice)
    >>> # フィルタを適用しても、「田無市」「保谷市」は2001年1月1日より後まで存在し、
    >>> # 「西東京市」は2001年2月1日より前から存在するので、いずれもそのまま残ります
    >>> for nodes in lattice_filtered:
    ...     [x.simple() for x in nodes]
    ...
    ["田無市(GEOWORD:['東京都'])"]
    ['と(NORMAL)']
    ["保谷市(GEOWORD:['東京都'])"]
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ["西東京市(GEOWORD:['東京都'])"]
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    """

    def filter_func(self, candidate):
        """
        時間範囲の開始時より後、または終了時より前に存在していれば True を返します。

        Parameters
        ----------
        candidate : pygeonlp.api.node.Node
            検査対象となるノードオブジェクト。

        Returns
        -------
        bool
            フィルタの条件を満たせば True, 満たさなければ False を返します。
        """
        span = self.__class__.duration_from_candidate(candidate)
        if span is None:
            return True   # 期間を持たない候補は合格

        if span[0] and span[0] > self.duration[1]:
            return False

        if span[1] and span[1] < self.duration[0]:
            return False

        return True


class TimeCoversFilter(TemporalFilter):
    """
    指定した時間範囲の開始時から終了時まで存在していれば合格とするフィルタを作成します。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.temporal_filter import TimeCoversFilter
    >>> api.init()
    >>> tcfilter = TimeCoversFilter('2001-01-01', '2001-02-01')
    >>> lattice = api.analyze('田無市と保谷市は2001年1月21日に合併して西東京市になりました。')
    >>> for nodes in lattice:
    ...     [x.simple() for x in nodes]
    ...
    ["田無市(GEOWORD:['東京都'])"]
    ['と(NORMAL)']
    ["保谷市(GEOWORD:['東京都'])"]
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ["西東京市(GEOWORD:['東京都'])"]
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    >>> lattice_filtered = tcfilter(lattice)
    >>> # フィルタを適用すると、「田無市」「保谷市」は2001年2月1日より前に消滅し、
    >>> # 「西東京市」は2001年1月1日より前から存在するので、地名語候補から除外されます。
    >>> for nodes in lattice_filtered:
    ...     [x.simple() for x in nodes]
    ...
    ['田無市(NORMAL)']
    ['と(NORMAL)']
    ['保谷市(NORMAL)']
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ['西東京市(NORMAL)']
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    """

    def filter_func(self, candidate):
        """
        時間範囲の開始時より前、かつ、終了時より後に存在していれば True を返します。

        Parameters
        ----------
        candidate : pygeonlp.api.node.Node
            検査対象となるノードオブジェクト。

        Returns
        -------
        bool
            フィルタの条件を満たせば True, 満たさなければ False を返します。
        """
        span = self.__class__.duration_from_candidate(candidate)
        if span is None:
            return True   # 期間を持たない候補は合格

        if span[0] and span[0] > self.duration[0]:
            return False

        if span[1] and span[1] < self.duration[1]:
            return False

        return True


class TimeContainsFilter(TemporalFilter):
    """
    指定した時間範囲の開始時と終了時の間だけ存在していれば合格とするフィルタを
    作成します。開始時より前に存在していたり、終了時より後に存在している場合は
    不合格になります。

    そのため、 valid_from, valid_to のいずれかが未指定の場合は不合格になります。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.temporal_filter import TimeContainsFilter
    >>> api.init()
    >>> tcfilter = TimeContainsFilter('2001-01-01', '2001-02-01')
    >>> lattice = api.analyze('田無市と保谷市は2001年1月21日に合併して西東京市になりました。')
    >>> for nodes in lattice:
    ...     [x.simple() for x in nodes]
    ...
    ["田無市(GEOWORD:['東京都'])"]
    ['と(NORMAL)']
    ["保谷市(GEOWORD:['東京都'])"]
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ["西東京市(GEOWORD:['東京都'])"]
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']
    >>> lattice_filtered = tcfilter(lattice)
    >>> # フィルタを適用すると、「田無市」「保谷市」は2001年1月1日より前にも存在し、
    >>> # 「西東京市」は2001年2月1日より後まで存在するので、地名語候補から除外されます。
    >>> for nodes in lattice_filtered:
    ...     [x.simple() for x in nodes]
    ...
    ['田無市(NORMAL)']
    ['と(NORMAL)']
    ['保谷市(NORMAL)']
    ['は(NORMAL)']
    ['2001(NORMAL)']
    ['年(NORMAL)']
    ['1(NORMAL)']
    ['月(NORMAL)']
    ['21(NORMAL)']
    ['日(NORMAL)']
    ['に(NORMAL)']
    ['合併(NORMAL)']
    ['し(NORMAL)']
    ['て(NORMAL)']
    ['西東京市(NORMAL)']
    ['に(NORMAL)']
    ['なり(NORMAL)']
    ['まし(NORMAL)']
    ['た(NORMAL)']
    ['。(NORMAL)']

    """

    def filter_func(self, candidate):
        """
        時間範囲の開始時と終了時の間に存在していれば True を返します。

        Parameters
        ----------
        candidate : pygeonlp.api.node.Node
            検査対象となるノードオブジェクト。

        Returns
        -------
        bool
            フィルタの条件を満たせば True, 満たさなければ False を返します。
        """
        span = self.__class__.duration_from_candidate(candidate)
        if span is None:
            return True   # 期間を持たない候補は合格

        if span[0] and span[0] >= self.duration[0] and \
           span[1] and span[1] <= self.duration[1]:
            return True

        return False
