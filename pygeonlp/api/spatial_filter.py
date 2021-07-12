"""
このモジュールは、特定の地域内の地名語だけを抽出するといった
空間フィルタを実装しています。

空間演算に OSGeo の GDAL パッケージが必要です。
GDAL Python パッケージをインストールするには、利用している OS で
インストールした libgdal のバージョンに合わせる必要があります。
詳しくは https://pypi.org/project/GDAL/#history を確認してください。

GDAL パッケージをインストールしない場合は空間フィルタは利用できません。
"""

import json
from logging import getLogger
import urllib

from pygeonlp.api.filter import Filter, FilterError

try:
    from osgeo import ogr
except ModuleNotFoundError:
    raise FilterError((
        "SpatialFilter を利用するには 'gdal' パッケージを"
        "インストールしてください。"))

logger = getLogger(__name__)


class SpatialFilter(Filter):
    """
    空間フィルタの基底クラス。

    空間フィルタは、形態素に対応する地名語ノード候補と住所ノード候補のうち、
    条件に一致するものを残し、一致しないものを削除します。
    全ての候補が条件に一致しない場合、品詞情報として固有名詞を持つ
    一般ノードを一つ作成して置き換えます。

    空間フィルタでは、地名語ノードと住所ノードの geometry が持つ GeoJSON を
    そのノードの地点とします。
    """

    def __init__(self, geojson_or_url, **kwargs):
        """
        フィルタを初期化します。

        Parameters
        ----------
        geojson_or_url : str
            空間範囲を表す GeoJSON　または GeoJSON ファイルを取得できる URL。
        """
        super().__init__()
        self.when_all_failed = 'convert_to_normal'
        self.geo = self.__class__.get_geometry(geojson_or_url)

    @classmethod
    def get_geometry_from_geojson_url(cls, url):
        """
        指定された URL から GeoJSON を含むファイルをダウンロードして、
        osgeo.ogr.Geometry オブジェクトを作成します。

        Parameters
        ----------
        url : str
            対象ファイルの URL。

        Returns
        -------
        osgeo.ogr.Geometry
            GeoJSON から作成した Geometry オブジェクト。

        Examples
        --------
        >>> from pygeonlp.api.spatial_filter import SpatialFilter
        >>> SpatialFilter.get_geometry_from_geojson_url(
        ...   'https://geoshape.ex.nii.ac.jp/city/geojson/20200101/13/13101A1968.geojson').ExportToWkt()
        'MULTIPOLYGON (((139.73150362 35.68150121,139.73119903 35.68198095,...,139.73150362 35.68150121)))'
        """
        geo = None

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as res:
                geojson = res.read().decode('utf-8')

            geo = cls.get_geometry_from_geojson(geojson)

        except RuntimeError as e:
            raise FilterError(str(e))

        return geo

    @classmethod
    def get_geometry_from_geojson(cls, geojson):
        """
        指定された GeoJSON 文字列から osgeo.ogr.Geometry オブジェクトを作成します。

        Parameters
        ----------
        geojson : str
            GeoJSON 文字列。
            GeoJSON をデコードした dict も利用できます。

        Returns
        -------
        osgeo.ogr.Geometry
            GeoJSON から作成した Geometry オブジェクト。

        Examples
        --------
        >>> from pygeonlp.api.spatial_filter import SpatialFilter
        >>> SpatialFilter.get_geometry_from_geojson(
        ...   {'type':'Point','coordinates':[139.6917337, 35.6895014]}
        ... ).ExportToWkt()
        'POINT (139.6917337 35.6895014)'
        """
        if isinstance(geojson, str):
            geoobj = json.loads(geojson)
        else:
            geoobj = geojson

        if geoobj['type'] == 'FeatureCollection':
            geojson = json.dumps(geoobj['features'][0]['geometry'])
        elif geoobj['type'] == 'Feature':
            geojson = json.dumps(geoobj['geometry'])
        elif 'coordinates' in geoobj:  # geometry type
            geojson = json.dumps(geoobj)
        else:
            raise FilterError('geojson の種別を判定できませんでした: ' + geojson)

        geo = ogr.CreateGeometryFromJson(geojson)

        if not geo:
            raise FilterError('Cannot parse the given geojson: ' + geojson)

        return geo

    @classmethod
    def get_geometry(cls, geojson_or_url):
        """
        GeoJSON または GeoJSON ファイルを取得できる URL から、
        osgeo.ogr.Geometry オブジェクトを作成します。

        Parameters
        ----------
        geojson_or_url : str
            GeoJSON 文字列またはデコードした dict、
            または GeoJSON ファイルをダウンロードできる URL。

        Returns
        -------
        osgeo.ogr.Geometry
            GeoJSON から作成した Geometry オブジェクト。

        Examples
        --------
        >>> from pygeonlp.api.spatial_filter import SpatialFilter
        >>> SpatialFilter.get_geometry({'type':'Point','coordinates':[139.6917337, 35.6895014]}).ExportToWkt()
        'POINT (139.6917337 35.6895014)'
        """
        if isinstance(geojson_or_url, str):
            try:
                geojson = json.loads(geojson_or_url)
                geo = cls.get_geometry_from_geojson(geojson)
                return geo
            except json.decoder.JSONDecodeError:
                geo = cls.get_geometry_from_geojson_url(geojson_or_url)
        else:
            geo = cls.get_geometry_from_geojson(geojson_or_url)

        return geo

    @classmethod
    def point_from_candidate(cls, candidate):
        """
        候補ノードにふくまれる経度緯度座標から ogr.Geometry オブジェクトを作成します。
        経度緯度が含まれていない場合は None を返します。

        Parameters
        ----------
        candidate : pygeonlp.api.node.Node
            候補ノード。

        Returns
        -------
        osgeo.ogr.Geometry
            Point タイプの Geometry オブジェクト。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> from pygeonlp.api.spatial_filter import SpatialFilter
        >>> api.init()
        >>> SpatialFilter.point_from_candidate(api.analyze('国会議事堂前')[0][0]).ExportToWkt()
        'POINT (139.745341666667 35.674845)'
        """

        if candidate.geometry is None:
            return None

        geojson = json.dumps(candidate.geometry)
        point = ogr.CreateGeometryFromJson(geojson)
        return point


class GeoContainsFilter(SpatialFilter):
    """
    指定した空間範囲に含まれていれば合格とするフィルタを作成します。

    Attributes
    ----------
    geo : osgeo.ogr.Geometry
        空間範囲を表す Geometry オブジェクト。 Polygon, MultiPolygon など、
        Contains() 演算が可能なタイプである必要があります。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.spatial_filter import GeoContainsFilter
    >>> api.init()
    >>> gcfilter = GeoContainsFilter({"type":"Polygon","coordinates":[[[139.6231,35.5461],[139.9106,35.5461],[139.9106,35.8271],[139.6231,35.8271],[139.6231,35.5461]]]})
    >>> # gcfilter はおおよそ23区を囲む矩形のフィルタ
    >>> lattice = api.analyze('新宿駅から八王子駅までは約40分です。')
    >>> for nodes in lattice:
    ...     [x.simple() for x in nodes]
    ...
    ["新宿駅(GEOWORD:['京王電鉄', '京王線'])", "新宿駅(GEOWORD:['小田急電鉄', '小田原線'])", "新宿駅(GEOWORD:['東京地下鉄', '4号線丸ノ内線'])", "新宿駅(GEOWORD:['東京都', '10号線新宿線'])", "新宿駅(GEOWORD:['東京都', '12号線大江戸線'])", "新宿駅(GEOWORD:['東日本旅客鉄道', '山手線'])", "新宿駅(GEOWORD:['東日本旅客鉄道', '中央線'])"]
    ['から(NORMAL)']
    ["八王子駅(GEOWORD:['東日本旅客鉄道', '横浜線'])", "八王子駅(GEOWORD:['東日本旅客鉄道', '中央線'])", "八王子駅(GEOWORD:['東日本旅客鉄道', '八高線'])"]
    ['まで(NORMAL)']
    ['は(NORMAL)']
    ['約(NORMAL)']
    ['40(NORMAL)']
    ['分(NORMAL)']
    ['です(NORMAL)']
    ['。(NORMAL)']
    >>> lattice_filtered = gcfilter(lattice)
    >>> # フィルタを適用すると「八王子駅」が範囲外なので地名語候補から除外されます
    >>> for nodes in lattice_filtered:
    ...     [x.simple() for x in nodes]
    ...
    ["新宿駅(GEOWORD:['京王電鉄', '京王線'])", "新宿駅(GEOWORD:['小田急電鉄', '小田原線'])", "新宿駅(GEOWORD:['東京地下鉄', '4号線丸ノ内線'])", "新宿駅(GEOWORD:['東京都', '10号線新宿線'])", "新宿駅(GEOWORD:['東京都', '12号線大江戸線'])", "新宿駅(GEOWORD:['東日本旅客鉄道', '山手線'])", "新宿駅(GEOWORD:['東日本旅客鉄道', '中央線'])"]
    ['から(NORMAL)']
    ['八王子駅(NORMAL)']
    ['まで(NORMAL)']
    ['は(NORMAL)']
    ['約(NORMAL)']
    ['40(NORMAL)']
    ['分(NORMAL)']
    ['です(NORMAL)']
    ['。(NORMAL)']

    """

    def __init__(self, geojson_or_url):
        super().__init__(geojson_or_url)

    def filter_func(self, candidate):
        point = self.__class__.point_from_candidate(candidate)
        if point is None:
            return True   # 座標を持たない候補は合格

        logger.debug("{} contains {} returns {}.".format(
            self.geo, point, self.geo.Contains(point)))
        return self.geo.Contains(point)


class GeoDisjointFilter(SpatialFilter):
    """
    指定した空間範囲に含まれていなければ合格とするフィルタを作成します。

    Attributes
    ----------
    geo : osgeo.ogr.Geometry
        空間範囲を表す Geometry オブジェクト。 Polygon, MultiPolygon など、
        Disjoint() 演算が可能なタイプである必要があります。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.spatial_filter import GeoDisjointFilter
    >>> api.init()
    >>> gdfilter = GeoDisjointFilter({"type":"Polygon","coordinates":[[[139.6231,35.5461],[139.9106,35.5461],[139.9106,35.8271],[139.6231,35.8271],[139.6231,35.5461]]]})
    >>> # gdfilter はおおよそ23区を囲む矩形のフィルタ
    >>> lattice = api.analyze('新宿駅から八王子駅までは約40分です。')
    >>> for nodes in lattice:
    ...     [x.simple() for x in nodes]
    ...
    ["新宿駅(GEOWORD:['京王電鉄', '京王線'])", "新宿駅(GEOWORD:['小田急電鉄', '小田原線'])", "新宿駅(GEOWORD:['東京地下鉄', '4号線丸ノ内線'])", "新宿駅(GEOWORD:['東京都', '10号線新宿線'])", "新宿駅(GEOWORD:['東京都', '12号線大江戸線'])", "新宿駅(GEOWORD:['東日本旅客鉄道', '山手線'])", "新宿駅(GEOWORD:['東日本旅客鉄道', '中央線'])"]
    ['から(NORMAL)']
    ["八王子駅(GEOWORD:['東日本旅客鉄道', '横浜線'])", "八王子駅(GEOWORD:['東日本旅客鉄道', '中央線'])", "八王子駅(GEOWORD:['東日本旅客鉄道', '八高線'])"]
    ['まで(NORMAL)']
    ['は(NORMAL)']
    ['約(NORMAL)']
    ['40(NORMAL)']
    ['分(NORMAL)']
    ['です(NORMAL)']
    ['。(NORMAL)']
    >>> lattice_filtered = gdfilter(lattice)
    >>> # フィルタを適用すると「新宿駅」が範囲内なので地名語候補から除外されます
    >>> for nodes in lattice_filtered:
    ...     [x.simple() for x in nodes]
    ...
    ['新宿駅(NORMAL)']
    ['から(NORMAL)']
    ["八王子駅(GEOWORD:['東日本旅客鉄道', '横浜線'])", "八王子駅(GEOWORD:['東日本旅客鉄道', '中央線'])", "八王子駅(GEOWORD:['東日本旅客鉄道', '八高線'])"]
    ['まで(NORMAL)']
    ['は(NORMAL)']
    ['約(NORMAL)']
    ['40(NORMAL)']
    ['分(NORMAL)']
    ['です(NORMAL)']
    ['。(NORMAL)']
    """

    def __init__(self, geojson_or_url):
        super().__init__(geojson_or_url)

    def filter_func(self, candidate):
        point = self.__class__.point_from_candidate(candidate)
        if point is None:
            return True  # 座標を持たない候補は合格

        return self.geo.Disjoint(point)
