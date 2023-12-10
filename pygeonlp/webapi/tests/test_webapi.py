from pygeonlp.webapi.tests.helpers import validate_jsonrpc, write_resreq

"""
GDAL がインストールされているかどうかをチェックします
"""
"""
gdal_not_installed = False
try:
    import osgeo
except ModuleNotFoundErrlr:
    gdal_not_installed = True
"""


class TestBasicApi:
    """
    基本的な API のテスト
    """

    def test_version(self, client):
        """
        Test ``geonlp.version`` API.
        """
        import pygeonlp.api
        query = {
            'method': 'geonlp.version',
            'params': {},
            'id': 'test_version',
        }
        expected = pygeonlp.api.__version__
        result = validate_jsonrpc(client, query, expected)
        write_resreq(query, result)

    def test_parse(self, client):
        """
        Test ``geonlp.parse`` API.
        """
        query = {
            'method': 'geonlp.parse',
            'params': {'sentence': 'NIIは神保町駅から徒歩7分です。'},
            'id': 'test_parse',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 形態素解析のチェック
        words = 'NII/は/神保町駅/から/徒歩/7/分/です/。'.split('/')
        for pos, feature in enumerate(features):
            prop = feature['properties']
            assert prop['surface'] == words[pos]  # 表記が一致

            if prop['surface'] == '神保町駅':
                assert prop['node_type'] == 'GEOWORD'
            else:
                assert prop['node_type'] == 'NORMAL'

        write_resreq(query, result)

    def test_parse_geocoding(self, client):
        """
        Test ``geonlp.parse`` API using geocoding.
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': 'NIIは千代田区一ツ橋2-1-2にあります。',
                'options': {'geocoding': True}
            },
            'id': 'test_parse_geocoding',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 形態素解析のチェック
        words = 'NII/は/千代田区一ツ橋2-1-/2/に/あり/ます/。'.split('/')
        for pos, feature in enumerate(features):
            prop = feature['properties']
            assert prop['surface'] == words[pos]  # 表記が一致

            if prop['surface'] == '千代田区一ツ橋2-1-':
                assert prop['node_type'] == 'ADDRESS'
            else:
                assert prop['node_type'] == 'NORMAL'

        write_resreq(query, result)

    def test_parse_without_geocoding(self, client):
        """
        Test ``geonlp.parse`` API using geocoding.
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': 'NIIは千代田区一ツ橋2-1-2にあります。',
                'options': {'geocoding': False}
            },
            'id': 'test_parse_without_geocoding',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 形態素解析のチェック
        words = 'NII/は/千代田区/一ツ橋/2/-/1/-/2/に/あり/ます/。'.split('/')
        for pos, feature in enumerate(features):
            prop = feature['properties']
            assert prop['surface'] == words[pos]  # 表記が一致

            if prop['surface'] == '千代田区':
                assert prop['node_type'] == 'GEOWORD'
            elif prop['surface'] == '一ツ橋':
                assert prop['node_type'] == 'NORMAL'
            else:
                assert prop['node_type'] == 'NORMAL'

    def test_parseStructured(self, client):
        """
        Test ``geonlp.parseStructured`` API.
        """
        query = {
            'method': 'geonlp.parseStructured',
            'params': {
                'sentence_list': [
                    'NIIは神保町駅から徒歩7分です。',
                    '千代田区一ツ橋2-1-2にあります。',
                    '竹橋駅も近いです。', ]
            },
            'id': 'test_parseStructured',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 形態素解析のチェック
        words = 'NII/は/神保町駅/から/徒歩/7/分/です/。'.split('/') +\
            '千代田区/一ツ橋/2/-/1/-/2/に/あり/ます/。'.split('/') +\
            '竹橋駅/も/近い/です/。'.split('/')
        for pos, feature in enumerate(features):
            prop = feature['properties']
            assert prop['surface'] == words[pos]  # 表記が一致

            if prop['surface'] in ('神保町駅', '千代田区', '竹橋駅'):
                assert prop['node_type'] == 'GEOWORD'
            else:
                assert prop['node_type'] == 'NORMAL'

        write_resreq(query, result)

    def test_search(self, client):
        """
        Test ``geonlp.search`` API.
        """
        query = {
            'method': 'geonlp.search',
            'params': {'key': '国会議事堂前'},
            'id': 'test_search',
        }
        expected = {
            'Bn4q6d': {
                'body': '国会議事堂前', 'dictionary_id': 3,
                'dictionary_identifier': 'geonlp:ksj-station-N02',
                'entry_id': 'LrGGxY', 'geolod_id': 'Bn4q6d',
                'hypernym': ['東京地下鉄', '4号線丸ノ内線'],
                'institution_type': '民営鉄道',
                'latitude': '35.674845',
                'longitude': '139.74534166666666',
                'ne_class': '鉄道施設/鉄道駅',
                'railway_class': '普通鉄道',
                'suffix': ['駅', '']
            },
            'cE8W4w': {
                'body': '国会議事堂前', 'dictionary_id': 3,
                'dictionary_identifier': 'geonlp:ksj-station-N02',
                'entry_id': '4NFELa',
                'geolod_id': 'cE8W4w',
                'hypernym': ['東京地下鉄', '9号線千代田線'],
                'institution_type': '民営鉄道',
                'latitude': '35.673543333333335',
                'longitude': '139.74305333333334',
                'ne_class': '鉄道施設/鉄道駅',
                'railway_class': '普通鉄道',
                'suffix': ['駅', '']
            }
        }
        result = validate_jsonrpc(client, query, expected)
        write_resreq(query, result)

    def test_getGeoInfo_idlist(self, client):
        """
        Test ``geonlp.getGeoInfo`` API with multiple geolod_id.
        """
        query = {
            'method': 'geonlp.getGeoInfo',
            'params': {'idlist': ['Bn4q6d', 'cE8W4w']},
            'id': 'test_getGeoInfo_idlist',
        }
        expected = {
            'Bn4q6d': {
                'body': '国会議事堂前', 'dictionary_id': 3,
                'dictionary_identifier': 'geonlp:ksj-station-N02',
                'entry_id': 'LrGGxY', 'geolod_id': 'Bn4q6d',
                'hypernym': ['東京地下鉄', '4号線丸ノ内線'],
                'institution_type': '民営鉄道',
                'latitude': '35.674845',
                'longitude': '139.74534166666666',
                'ne_class': '鉄道施設/鉄道駅',
                'railway_class': '普通鉄道',
                'suffix': ['駅', '']
            },
            'cE8W4w': {
                'body': '国会議事堂前', 'dictionary_id': 3,
                'dictionary_identifier': 'geonlp:ksj-station-N02',
                'entry_id': '4NFELa',
                'geolod_id': 'cE8W4w',
                'hypernym': ['東京地下鉄', '9号線千代田線'],
                'institution_type': '民営鉄道',
                'latitude': '35.673543333333335',
                'longitude': '139.74305333333334',
                'ne_class': '鉄道施設/鉄道駅',
                'railway_class': '普通鉄道',
                'suffix': ['駅', '']
            }
        }
        result = validate_jsonrpc(client, query, expected)
        write_resreq(query, result)

    def test_getGeoInfo_nocandidate(self, client):
        """
        Test ``geonlp.getGeoInfo`` API with invalid geolod_id.
        """
        query = {
            'method': 'geonlp.getGeoInfo',
            'params': {'idlist': ['aaaaaa']},
            'id': 'test_getGeoInfo_nocandidate',
        }
        expected = {'aaaaaa': None}
        result = validate_jsonrpc(client, query, expected)
        write_resreq(query, result)

    def test_getDictionaries(self, client):
        """
        Test ``geonlp.getDictionaries`` API.
        """
        query = {
            'method': 'geonlp.getDictionaries',
            'params': {},
            'id': 'test_getDictionaries',
        }
        expected = ['geonlp:geoshape-city',
                    'geonlp:geoshape-pref',
                    'geonlp:ksj-station-N02']
        result = validate_jsonrpc(client, query, expected)
        write_resreq(query, result)

    def test_getDictionaryInfo(self, client):
        """
        Test ``geonlp.getDictionaryInfo`` API.
        """
        query = {
            'method': 'geonlp.getDictionaryInfo',
            'params': {'identifier': 'geonlp:ksj-station-N02'},
            'id': 'test_getDictionaryInfo',
        }
        expected = '{"@context": "https://schema.org/", "@type": "Dataset", "alternateName": "", "creator": [{"@type": "Organization", "name": "株式会社情報試作室", "sameAs": "https://www.info-proto.com/"}], "dateModified": "2021-08-27T17:18:18+09:00", "description": "国土数値情報「鉄道データ（N02）」から作成した、日本の鉄道駅（地下鉄を含む）の辞書です。hypernym には運営者名と路線名を記載しています。「都営」ではなく「東京都」のようになっていますので注意してください。自由フィールドとして、railway_classに「鉄道区分」、institution_typeに「事業者種別」を含みます。", "distribution": [{"@type": "DataDownload", "contentUrl": "https://www.info-proto.com/static/ksj-station-N02.csv", "encodingFormat": "text/csv"}], "identifier": ["geonlp:ksj-station-N02"], "isBasedOn": {"@type": "CreativeWork", "name": "国土数値情報 鉄道データ", "url": "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_2.html"}, "keywords": ["GeoNLP", "地名辞書"], "license": "https://creativecommons.org/licenses/by/4.0/", "name": "国土数値情報 鉄道データ（駅）", "size": "10191", "spatialCoverage": {"@type": "Place", "geo": {"@type": "GeoShape", "box": "26.193265 127.652285 45.41616333333333 145.59723"}}, "temporalCoverage": "../..", "url": "https://www.info-proto.com/static/ksj-station-N02.html"}'
        result = validate_jsonrpc(client, query, expected)
        write_resreq(query, result)

    def test_getDictionaryInfo_nocandidate(self, client):
        """
        Test ``geonlp.getDictionaryInfo`` API with invalid identifier.
        """
        query = {
            'method': 'geonlp.getDictionaryInfo',
            'params': {'identifier': 'geonlp:abcdef'},
            'id': 'test_getDictionaryInfo_nocandidate',
        }
        expected = None
        result = validate_jsonrpc(client, query, expected)
        write_resreq(query, result)

    def test_addressGeocoding(self, client):
        """
        Test ``geonlp.addressGeocoding`` API.
        """
        query = {
            'method': 'geonlp.addressGeocoding',
            'params': {'address': '千代田区一ツ橋2-1-2'},
            'id': 'test_addressGeocoding',
        }
        expected = "*"
        result = validate_jsonrpc(client, query, expected)
        write_resreq(query, result)


class TestParseOptions:
    """
    Parse options のテスト
    """

    def test_parse_option_set_dic(self, client):
        """
        Test 'set-dic' option.

        Notes
        -----
        'set-dic' に r'geoshape' を指定すると、
        identifier に 'geoshape' を含む辞書だけが利用されます。

        'geoshape-city' が利用できるため、
        「和歌山市（市）」に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '和歌山市は晴れ。',
                'options': {'set-dic': r'geoshape'}
            },
            'id': 'test_parse_set_dic',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '和歌山市'
        assert prop['geoword_properties']['geolod_id'] == 'lQccqK'

        write_resreq(query, result)

    def test_parse_option_set_dic_list(self, client):
        """
        Test 'set-dic' option with list of identifiers.

        Notes
        -----
        'set-dic' に ['geoshape'] を指定すると、
        identifier が 'geoshape' と文字列として等しい辞書だけが
        利用されます。

        一致する辞書は無いため、「和歌山」に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '和歌山市は晴れ。',
                'options': {'set-dic': ['geoshape']}
            },
            'id': 'test_parse_set_dic_list',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '和歌山'
        assert 'geoword_properties' not in prop

    def test_parse_option_remove_dic(self, client):
        """
        Test 'remove-dic' option.

        Notes
        -----
        'remove-dic' に r'station' を指定すると、
        identifier に 'station' を含む辞書は利用されません。

        'geoshape-city' が利用できるため、
        「和歌山市（市）」に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '和歌山市は晴れ。',
                'options': {'remove-dic': r'station'}
            },
            'id': 'test_parse_remove_dic',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '和歌山市'
        assert prop['geoword_properties']['dictionary_identifier'] == \
            'geonlp:geoshape-city'

        write_resreq(query, result)

    def test_parse_option_add_dic(self, client):
        """
        Test 'add-dic' option.

        Notes
        -----
        'add-dic' に r'city' を指定すると、
        'remove-dic' で除外指定されていても、
        identifier に 'city' を含む辞書は利用されます。

        'geoshape-city' は 'remove-dic' で除外されますが
        'add-dic' で追加されるため利用可能になり、
        「和歌山市（市）」に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '和歌山市は晴れ。',
                'options': {'remove-dic': r'.*',
                            'add-dic': r'city'}
            },
            'id': 'test_parse_add_dic',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '和歌山市'
        assert prop['geoword_properties']['dictionary_identifier'] == \
            'geonlp:geoshape-city'

        write_resreq(query, result)

    def test_parse_option_set_class(self, client):
        """
        Test 'set-class' option.

        Notes
        -----
        'set-class' に [r'.*', r'-鉄道施設/.*'] を指定すると、
        全ての固有名クラスから '鉄道施設/.*' を除いたものを持つ
        地名語を候補として利用します。

        「和歌山市（駅）」は鉄道施設なので除外され、
        「和歌山市（市）」に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '和歌山市は晴れ。',
                'options': {'set-class': [r'.*', r'-鉄道施設/.*']}
            },
            'id': 'test_parse_set_class',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '和歌山市'
        assert prop['geoword_properties']['dictionary_identifier'] == \
            'geonlp:geoshape-city'

        write_resreq(query, result)

    def test_parse_option_set_class_except(self, client):
        """
        Test 'set-class' option.

        Notes
        -----
        'set-class' に [r'.*', r'-鉄道施設/.*', r'鉄道施設/鉄道駅'] を
        指定すると、この順番に評価するため「鉄道駅」は利用されます。

        「和歌山市（駅）」は鉄道施設/鉄道駅なので対象になります。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '和歌山市は晴れ。',
                'options': {'set-class': [
                    r'.*', r'-鉄道施設/.*', r'.*駅$'
                ]}
            },
            'id': 'test_parse_set_class_except',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '和歌山市'
        assert prop['geoword_properties']['dictionary_identifier'] == \
            'geonlp:ksj-station-N02'

    def test_parse_option_add_class(self, client):
        """
        Test 'add-class' option.

        Notes
        -----
        'add-class' で利用するクラスのリストを指定できます。

        'add-class' に [r'-.*', '市区町村'] を指定すると、
        全ての固有名クラスを対象クラスから除外し、
        次に「市区町村」クラスの地名語を対象に加えます。

        「和歌山市（駅）」は鉄道施設なので除外され、
        「和歌山市（市）」に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '和歌山市は晴れ。',
                'options': {'add-class': [
                    r'-.*', '市区町村'
                ]}
            },
            'id': 'test_parse_add_class',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '和歌山市'
        assert prop['geoword_properties']['dictionary_identifier'] == \
            'geonlp:geoshape-city'

        write_resreq(query, result)

    def test_parse_option_remove_class(self, client):
        """
        Test 'remove-class' option.

        Notes
        -----
        'set-class' で一度に指定する代わりに、
        'remove-class' で除外するクラスのリストを指定できます。

        'remove-class' に [r'.*', '-市区町村'] を指定すると、
        全ての固有名クラスを対象クラスから除外し、
        次に「市区町村」クラスの地名語を対象に加えます。

        'remove-class' のリストではクラス名の先頭に '-' を付けると
        追加の意味になります。

        「和歌山市（駅）」は鉄道施設なので除外され、
        「和歌山市（市）」に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '和歌山市は晴れ。',
                'options': {'remove-class': [
                    r'.*', '-市区町村'
                ]}
            },
            'id': 'test_parse_remove_class',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '和歌山市'
        assert prop['geoword_properties']['dictionary_identifier'] == \
            'geonlp:geoshape-city'

        write_resreq(query, result)

    def test_parse_option_add_remove_class(self, client):
        """
        Test 'add-class' + 'remove-class' options.

        Notes
        -----
        'set-class' で一度に指定する代わりに、
        'add-class' で利用するクラスのリストを、
        'remove-class' で除外するクラスのリストを指定できます。

        ただし必ず 'remove-class' が先に評価されます。

        'add-class' で ['市区町村'] を、
        'remove-class' で [r'.*'] を指定すると、
        全ての固有名クラスを対象クラスから除外し、
        次に「市区町村」クラスの地名語を対象に加えます。

        「和歌山市（駅）」は鉄道施設なので除外され、
        「和歌山市（市）」に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '和歌山市は晴れ。',
                'options': {'add-class': ['市区町村'],
                            'remove-class': [r'.*']}
            },
            'id': 'test_parse_add_remove_class',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '和歌山市'
        assert prop['geoword_properties']['dictionary_identifier'] == \
            'geonlp:geoshape-city'


class TestSpatialFilters:
    """
    SpatialFilter のテスト
    """

    def test_parse_filter_geo_contains(self, client, require_gdal):
        """
        Test 'geo-contains' filter.

        Notes
        -----
        'geo-contains' に GeoJSON または GeoJSON を返す URL を
        指定すると、その範囲に含まれる地名語だけが候補になります。

        東京都付近の四角形を空間範囲として指定することで
        東京都の府中駅に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '府中に行きます。',
                'options': {
                    'geo-contains': {
                        "type": "Polygon",
                        "coordinates": [
                            [[139.43, 35.54], [139.91, 35.54],
                             [139.91, 35.83], [139.43, 35.83],
                                [139.43, 35.54]]]
                    }}
            },
            'id': 'test_parse_geo_contains',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '府中'
        assert '京王線' in prop['geoword_properties']['hypernym']

        write_resreq(query, result)

    def test_parse_filter_geo_disjoint(self, client, require_gdal):
        """
        Test 'geo-disjoint' filter.

        Notes
        -----
        'geo-disjoint' に GeoJSON または GeoJSON を返す URL を
        指定すると、その範囲に含まれない地名語だけが候補になります。

        東京都付近の四角形を空間範囲として指定することで
        京都市の府中駅に解決されます。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': '府中に行きます。',
                'options': {
                    'geo-disjoint': 'https://geoshape.ex.nii.ac.jp/city/geojson/20200101/13/13208A1968.geojson'
                }
            },
            'id': 'test_parse_geo_disjoint',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        prop = features[0]['properties']
        assert prop['surface'] == '府中'
        assert '天橋立鋼索鉄道' in prop['geoword_properties']['hypernym']

        write_resreq(query, result)


class TestTemporalFilters:
    """
    TemporalFilter のテスト
    """

    sentence = ('田無市と保谷市は2001年1月21日に合併して'
                '西東京市になりました。')

    def test_time_exists(self, client):
        """
        Test 'time-exists' filter.

        Notes
        -----
        'time-exists' に日時または日時のペアを指定すると、
        その時点・期間に存在した地名語だけが候補になります。

        西東京市は指定した期間内に設置されたので
        田無市と保谷市、西東京市は全て地名語になります。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': self.sentence,
                'options': {
                    'time-exists': ['2000-01-01', '2001-02-01']
                }
            },
            'id': 'test_time_exists',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        for feature in features:
            prop = feature['properties']
            if prop['surface'] in ('田無市', '保谷市', '西東京市',):
                assert prop['node_type'] == 'GEOWORD'
            else:
                assert prop['node_type'] == 'NORMAL'

        write_resreq(query, result)

    def test_time_exists_single_value(self, client):
        """
        Test 'time-exists' filter with single value.

        Notes
        -----
        'time-exists' に日時または日時を1つ指定すると、
        その時点に存在した地名語だけが候補になります。

        西東京市は指定した時点にはまだ設置されていないので
        田無市と保谷市が地名語、西東京市は固有名詞になります。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': self.sentence,
                'options': {
                    'time-exists': '2000-01-01'
                }
            },
            'id': 'test_time_exists',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        for feature in features:
            prop = feature['properties']
            if prop['surface'] in ('田無市', '保谷市',):
                assert prop['node_type'] == 'GEOWORD'
            elif prop['surface'] in ('西東京市',):
                assert prop['node_type'] == 'NORMAL'
            else:
                assert prop['node_type'] == 'NORMAL'

    def test_time_exists_dict(self, client):
        """
        Test 'time-exists' filter with dict values.

        Notes
        -----
        'time-exists' に 'date_from' と 'date_to' を持つ
        dict を指定すると、
        その期間に存在した地名語だけが候補になります。

        西東京市は指定した期間内に設置されたので
        田無市と保谷市、西東京市は全て地名語になります。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': self.sentence,
                'options': {
                    'time-exists': {
                        'date_from': '2000-01-01',
                        'date_to': '2001-02-01'
                    }
                }
            },
            'id': 'test_time_exists_dict',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        for feature in features:
            prop = feature['properties']
            if prop['surface'] in ('田無市', '保谷市', '西東京市',):
                assert prop['node_type'] == 'GEOWORD'
            else:
                assert prop['node_type'] == 'NORMAL'

    def test_time_before(self, client):
        """
        Test 'time-before' filter.

        Notes
        -----
        'time-before' に日時または日時のペアを指定すると、
        その時点・期間の開始時より前に存在した地名語だけが
        候補になります。

        西東京市は指定した期間の開始時より後に設置されたので
        田無市と保谷市が地名語、西東京市は固有名詞になります。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': self.sentence,
                'options': {
                    'time-before': ['2000-01-01', '2001-02-01']
                }
            },
            'id': 'test_time_before',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        for feature in features:
            prop = feature['properties']
            if prop['surface'] in ('田無市', '保谷市',):
                assert prop['node_type'] == 'GEOWORD'
            elif prop['surface'] in ('西東京市',):
                assert prop['node_type'] == 'NORMAL'
            else:
                assert prop['node_type'] == 'NORMAL'

        write_resreq(query, result)

    def test_time_after(self, client):
        """
        Test 'time-after' filter.

        Notes
        -----
        'time-after' に日時または日時のペアを指定すると、
        その時点・期間の終了時より後に存在した地名語だけが
        候補になります。

        田無市と保谷市は指定した期間の終了時より前に廃止されたので
        田無市と保谷市は固有名詞、西東京市は地名語になります。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': self.sentence,
                'options': {
                    'time-after': ['2000-01-01', '2001-02-01']
                }
            },
            'id': 'test_time_after',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        for feature in features:
            prop = feature['properties']
            if prop['surface'] in ('西東京市',):
                assert prop['node_type'] == 'GEOWORD'
            elif prop['surface'] in ('田無市', '保谷市',):
                assert prop['node_type'] == 'NORMAL'
            else:
                assert prop['node_type'] == 'NORMAL'

        write_resreq(query, result)

    def test_time_overlaps(self, client):
        """
        Test 'time-overlaps' filter.

        Notes
        -----
        'time-overlaps' に日時または日時のペアを指定すると、
        その時点・期間の終了時より後に存在した地名語だけが
        候補になります。

        西東京市は指定した期間内に設置されたので
        田無市と保谷市、西東京市は全て地名語になります。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': self.sentence,
                'options': {
                    'time-overlaps': ['2000-01-01', '2001-02-01']
                }
            },
            'id': 'test_time_overlaps',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        for feature in features:
            prop = feature['properties']
            if prop['surface'] in ('田無市', '保谷市', '西東京市',):
                assert prop['node_type'] == 'GEOWORD'
            else:
                assert prop['node_type'] == 'NORMAL'

        write_resreq(query, result)

    def test_time_covers(self, client):
        """
        Test 'time-covers' filter.

        Notes
        -----
        'time-covers' に日時または日時のペアを指定すると、
        その期間の開始時より終了時まで存在し続けた地名語だけが
        候補になります。

        西東京市は指定した期間内に設置され、
        田無市と保谷市は期間内に廃止されたので、
        田無市、保谷市、西東京市は全て固有名詞になります。
        """
        query = {
            'method': 'geonlp.parse',
            'params': {
                'sentence': self.sentence,
                'options': {
                    'time-covers': ['2000-01-01', '2001-02-01']
                }
            },
            'id': 'test_time_covers',
        }
        expected = '*'
        result = validate_jsonrpc(client, query, expected)

        # GeoJSON Feature Collection のチェック
        assert result['type'] == 'FeatureCollection'
        assert 'features' in result
        features = result['features']

        # 地名語のチェック
        for feature in features:
            prop = feature['properties']
            assert prop['node_type'] == 'NORMAL'

        write_resreq(query, result)
