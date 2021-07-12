import logging


logger = logging.getLogger(__name__)


def pp_geojson(geojson_list, indent=2, file=None):
    """
    geoparse() の結果（GeoJSON互換）を pretty print します。

    Parameters
    ----------
    geojson_list : list
        geoparse() 結果の GeoJSON 互換 dict のリスト。
    indent : int, optional
        インデント幅。デフォルトは2です。
    file : file descriptor, optional
        出力先のファイルデスクリプタ。デフォルトは None です。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.devtool import pp_geojson
    >>> api.init()
    >>> pp_geojson(api.geoparse('アメリカ大使館：港区赤坂'))
    アメリカ大使館 ： ≪港区|市区町村['東京都']≫ ≪赤坂|鉄道施設/鉄道駅['東京地下鉄', '9号線千代田線']≫ EOS
    <BLANKLINE>
    """
    def simple(geojson):
        properties = geojson['properties']
        hypernym = ""

        if properties['node_type'] == "ADDRESS":
            return "【{}:{}】".format(
                properties['surface'],
                properties['address_properties']['fullname'])
        elif properties['node_type'] == "GEOWORD":
            hypernym = properties['geoword_properties'].get('hypernym')
            ne_class = properties['geoword_properties'].get('ne_class')
            if hypernym:
                return "≪{}|{}{}≫".format(
                    properties['surface'], ne_class, hypernym)

            return "≪{}|{}≫".format(properties['surface'], ne_class)

        return properties['surface']

    for pos, geojson in enumerate(geojson_list):
        print("{}".format(simple(geojson)), end=' ', file=file)

    print("EOS\n", file=file)


def pp_lattice(lattice, indent=2, file=None):
    """
    ラティス表現のデータを pretty print します。

    Parameters
    ----------
    lattice: list
        解析結果のラティス表現。
    indent: int, optional
        インデント幅。デフォルトは2です。
    file: file descriptor, optional
        出力先のファイルデスクリプタ。デフォルトは None です。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.devtool import pp_lattice
    >>> import jageocoder
    >>> api.init()
    >>> dbdir = api.get_jageocoder_db_dir()
    >>> jageocoder.init(f'sqlite:///{dbdir}/address.db',
    ...   f'{dbdir}/address.trie')
    >>> parser = api.parser.Parser(jageocoder=jageocoder)
    >>> lattice = parser.analyze_sentence('アメリカ大使館：港区赤坂1-10-5')
    >>> pp_lattice(lattice)
    #0:'アメリカ大使館'
      アメリカ大使館(NORMAL)
    #1:'：'
      ：(NORMAL)
    #2:'港区'
      港区(GEOWORD:['東京都'])
      港区(GEOWORD:['愛知県', '名古屋市'])
      港区(GEOWORD:['大阪府', '大阪市'])
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
    >>> lattice_address_compact = parser.add_address_candidates(lattice)
    >>> pp_lattice(lattice_address_compact)
    #0:'アメリカ大使館'
      アメリカ大使館(NORMAL)
    #1:'：'
      ：(NORMAL)
    #2:'港区赤坂1-10-'
      港区赤坂1-10-(ADDRESS:東京都/港区/赤坂/一丁目/10番)[6]
    #3:'5'
      5(NORMAL)
    """
    for i in range(len(lattice)):
        nodes = lattice[i]
        print("#{}:'{}'".format(i, nodes[0].surface), file=file)
        for j, node in enumerate(nodes):
            print(" " * indent, end='', file=file)
            print(node.simple(), file=file)


def pp_path(path, indent=2, file=None):
    """
    パス表現のデータを pretty print します。

    Parameters
    ----------
    path: list
        解析結果のパス表現。
    indent: int, optional
        インデント幅。デフォルトは2です。
    file: file descriptor, optional
        出力先のファイルデスクリプタ。デフォルトは sys.stdout です。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.linker import LinkedResults
    >>> from pygeonlp.api.devtool import pp_path
    >>> api.init()
    >>> lattice = api.analyze('アメリカ大使館：港区赤坂1-10-5')
    >>> for path in LinkedResults(lattice):
    ...   pp_path(path)
    ...
    [
      #0:アメリカ大使館(NORMAL)
      #1:：(NORMAL)
      #2:港区(GEOWORD:['東京都'])
      #3:赤坂(GEOWORD:['上毛電気鉄道', '上毛線'])
      #4:1(NORMAL)
      #5:-(NORMAL)
      #6:10(NORMAL)
      #7:-(NORMAL)
      #8:5(NORMAL)
    ]
    [
      #0:アメリカ大使館(NORMAL)
      #1:：(NORMAL)
      #2:港区(GEOWORD:['東京都'])
      #3:赤坂(GEOWORD:['東京地下鉄', '9号線千代田線'])
      #4:1(NORMAL)
      #5:-(NORMAL)
      #6:10(NORMAL)
      #7:-(NORMAL)
      #8:5(NORMAL)
    ]
    ...
    """
    print("[", file=file)
    for i in range(len(path)):
        node = path[i]
        print(" " * indent, end='', file=file)
        print("#{}:{}".format(i, node.simple()), file=file)

    print("]", file=file)
