import json
from logging import getLogger

from geographiclib.geodesic import Geodesic

logger = getLogger(__name__)

try:
    from osgeo import ogr
    have_gdal = True
except ModuleNotFoundError:
    logger.info(("gdal パッケージがインストールされていないため、"
                 "ノード間の地理的距離計算をスキップします。"))
    have_gdal = False


class Node(object):
    """
    形態素ノードを表すクラス。

    service.analyze() が返すラティス表現や、 linker.RankedResults.get() が
    返すパス表現では、形態素は Node インスタンスとして格納されます。

    Attributes
    ----------
    surface : str
        表記文字列。
    node_type : int
        ノードの種類。地名語ノードは1、住所ノードは2、それ以外は0です。
    morphemes : list of dict
        形態素の属性。
    geometry : object or None
        地理属性。
    prop : dict
        その他の属性（geowordまたは住所）。
    """
    IGNORE = -1
    NORMAL = 0
    GEOWORD = 1
    ADDRESS = 2

    def __init__(self, surface, node_type, morphemes,
                 geometry=None, prop=None):
        """
        ノード情報を初期化します。

        ノードは基本的に Parser が作成したものを利用してください。
        """

        self.surface = surface
        self.node_type = node_type
        self.morphemes = morphemes
        self.geometry = geometry
        self.prop = prop
        self._attr = {}  # 動的に計算する属性

    def get_lonlat(self):
        """
        ノードの経度、緯度を返します。

        Returns
        -------
        dict
            以下の要素を持つ dict。

            - lat : float
                ノードの代表点の緯度。
            - lon : float
                ノードの代表点の経度。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> node = api.analyze('国会議事堂前')[0][0]
        >>> node.get_lonlat()
        {'lat': 35.674845, 'lon': 139.74534166666666}

        >>> import pygeonlp.api as api
        >>> import jageocoder
        >>> api.init()
        >>> dbdir = api.get_jageocoder_db_dir()
        >>> jageocoder.init(f'sqlite:///{dbdir}/address.db', f'{dbdir}/address.trie')
        >>> node = api.analyze('千代田区一ツ橋2-1-2', jageocoder=jageocoder)[0][0]
        >>> node.get_lonlat()
        {'lat': 35.692332, 'lon': 139.758148}
        """
        if self.node_type == self.__class__.GEOWORD:
            return {
                'lat': float(self.prop['latitude']),
                'lon': float(self.prop['longitude']),
            }

        if self.node_type == self.__class__.ADDRESS:
            return {
                'lat': self.prop['y'],
                'lon': self.prop['x'],
            }

        return None

    def __get_type_string(self):
        if self.node_type == self.__class__.NORMAL:
            return "NORMAL"
        elif self.node_type == self.__class__.GEOWORD:
            return "GEOWORD"
        elif self.node_type == self.__class__.ADDRESS:
            return "ADDRESS"

        return "UNKNOWN"

    def __repr__(self):
        return json.dumps(self.as_dict(), ensure_ascii=False)

    def simple(self):
        """
        ノード情報をシンプルな形式で表現します。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> api.analyze('国会議事堂前')[0][0].simple()
        "国会議事堂前(GEOWORD:['東京地下鉄', '4号線丸ノ内線'])"

        Returns
        -------
        str
            シンプルな形式の文字列。
        """

        hypernym = None
        if self.node_type == Node.GEOWORD:
            hypernym = self.prop.get('hypernym')

        if self.node_type == Node.ADDRESS:
            res = "{}({}:{})[{}]".format(
                self.surface,
                self.__get_type_string(),
                "/".join(self.prop['fullname']),
                len(self.morphemes))
        elif hypernym:
            res = "{}({}:{})".format(self.surface,
                                     self.__get_type_string(), hypernym)
        else:
            res = "{}({})".format(self.surface, self.__get_type_string())

        return res

    def as_dict(self):
        """
        ノード情報を JSON 出力可能な dict オブジェクトに変換します。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> api.analyze('国会議事堂前')[0][0].as_dict()
        {'surface': '国会議事堂前', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '国会議事堂前', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'fuquyv:国会議事堂前駅', 'surface': '国会議事堂前', 'yomi': ''}, 'geometry': {'type': 'Point', 'coordinates': [139.74534166666666, 35.674845]}, 'prop': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'e630bf128884455c4994e0ac5ca49b8d', 'geolod_id': 'fuquyv', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}

        Returns
        -------
        dict
            JSON 出力可能な dict オブジェクト。
        """
        obj = {
            "surface": self.surface,
            "node_type": self.__get_type_string(),
            "morphemes": self.morphemes,
            "geometry": self.geometry,
            "prop": self.prop,
        }
        return obj

    def as_geojson(self):
        """
        ノード情報を GeoJSON の Feature 形式にダンプ可能な dict オブジェクトに変換します。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> api.analyze('国会議事堂前')[0][0].as_geojson()
        {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.74534166666666, 35.674845]}, 'properties': {'surface': '国会議事堂前', 'node_type': 'GEOWORD', 'morphemes': {'conjugated_form': '*', 'conjugation_type': '*', 'original_form': '国会議事堂前', 'pos': '名詞', 'prononciation': '', 'subclass1': '固有名詞', 'subclass2': '地名語', 'subclass3': 'fuquyv:国会議事堂前駅', 'surface': '国会議事堂前', 'yomi': ''}, 'geoword_properties': {'body': '国会議事堂前', 'dictionary_id': 3, 'entry_id': 'e630bf128884455c4994e0ac5ca49b8d', 'geolod_id': 'fuquyv', 'hypernym': ['東京地下鉄', '4号線丸ノ内線'], 'institution_type': '民営鉄道', 'latitude': '35.674845', 'longitude': '139.74534166666666', 'ne_class': '鉄道施設/鉄道駅', 'railway_class': '普通鉄道', 'suffix': ['駅', ''], 'dictionary_identifier': 'geonlp:ksj-station-N02-2019'}}}

        Returns
        -------
        dict
            GeoJSON Feature 形式に変換可能な dict オブジェクト。
        """
        feature = {
            "type": "Feature",
            "geometry": self.geometry,
            "properties": {
                "surface": self.surface,
                "node_type": self.__get_type_string(),
                "morphemes": self.morphemes,
            }
        }
        if self.node_type == Node.GEOWORD:
            feature['properties']['geoword_properties'] = self.prop
        elif self.node_type == Node.ADDRESS:
            feature['properties']['address_properties'] = self.prop

        return feature

    def _add_node(self, surface, node):
        """
        形態素ノードをブロックに追加します。

        Parameters
        ----------
        surface : str
            ノードの表記
        node : dict
            形態素ノード、地名語ノードまたは住所ノード
        """
        self.surface += surface
        self.nodes.append(node)

    def get_notations(self):
        """
        このノードの表記として可能性があるものの候補を取得し、
        set を返します（重複を除去し、 AND を高速に計算するため）。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> # set は順番を保持しないので sorted で昇順にソート
        >>> sorted(api.analyze('国会議事堂前')[0][0].get_notations())
        ['国会議事堂前', '国会議事堂前駅']

        Notes
        -----
        何度も計算しないように、計算した結果は ``_attr['notations']`` に保持します。
        """
        if 'notations' in self._attr:
            return self._attr['notations']

        if self.node_type != Node.GEOWORD:
            self._attr['notations'] = set(self.surface,)
            return self._attr['notations']

        body = self.prop.get('body')
        prefixes = self.prop.get('prefix', None)
        suffixes = self.prop.get('suffix', None)
        cands = [body]
        if prefixes:
            for prefix in prefixes:
                cands.append(prefix + body)

        if suffixes:
            for suffix in suffixes:
                cands.append(body + suffix)

        if prefixes and suffixes:
            for prefix in prefixes:
                for suffix in suffixes:
                    cands.append(prefix + body + suffix)

        self._attr['notations'] = set(cands)
        return self._attr['notations']

    def get_point_object(self):
        """
        地名語ノードまたは住所ノードの場合、経度緯度から Point オブジェクトを作成します。

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> api.analyze('国会議事堂前')[0][0].get_point_object().ExportToWkt()
        'POINT (139.745341666667 35.674845)'

        Notes
        -----
        ``gdal`` がインストールされていない場合は None を返します。
        何度も計算しないように、計算した結果は ``_attr['point']`` に保持します。
        """
        if 'point' in self._attr:
            return self._attr['point']

        if have_gdal is False or self.geometry is None:
            return None

        point = ogr.CreateGeometryFromJson(json.dumps(self.geometry))
        self._attr['point'] = point
        return point

    def distance(self, node):
        """
        自身と他のノードの距離 (m) を計算します。
        このメソッドは geographiclib を利用します。
        https://pypi.org/project/geographiclib/

        Examples
        --------
        >>> import pygeonlp.api as api
        >>> api.init()
        >>> lattice = api.analyze('国会議事堂前,永田町')
        >>> n0 = lattice[0][0]
        >>> n1 = lattice[2][0]
        >>> round(n0.distance(n1), 6)
        676.592019
        """
        p0 = self.get_lonlat()
        p1 = node.get_lonlat()

        if p0 is None or p1 is None:
            raise RuntimeError(
                "ジオメトリを持たないノード間の距離は計算できません。")

        geod = Geodesic.WGS84
        g = geod.Inverse(p0['lat'], p0['lon'], p1['lat'], p1['lon'])

        return g['s12']
