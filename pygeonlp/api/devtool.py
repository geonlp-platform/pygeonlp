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
    アメリカ大使館 ： 【港区赤坂:['東京都', '港区', '赤坂']】 EOS
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
    >>> api.init()
    >>> parser = api.parser.Parser(jageocoder=True)
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
        出力先のファイルデスクリプタ。デフォルトは None です。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.linker import LinkedResults
    >>> from pygeonlp.api.devtool import pp_path
    >>> api.init(jageocoder=False)
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


def _mecabline(geojson):
    """
    geoparse() の結果（GeoJSON表現）の一語分を mecab 類似書式用の
    リストに変換します。

    Parameters
    ----------
    geojson : dict
        geoparse() 結果の GeoJSON 互換 dict。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.devtool import _mecabline as mecabline
    >>> mecabline(api.geoparse('目黒駅')[0])
    ('目黒駅', ('名詞', '固有名詞', '地名語', 'Y2uuN3:目黒駅', '*', '*', '目黒駅', '', ''), ('鉄道施設/鉄道駅', 'Y2uuN3', '目黒駅', '139.71566', '35.632485'))
    """
    # Common properties
    properties = geojson["properties"]
    morphemes = properties["morphemes"]
    node_type = properties["node_type"]

    if node_type in ("NORMAL", "GEOWORD"):
        common = (
            morphemes["pos"],
            morphemes["subclass1"],
            morphemes["subclass2"],
            morphemes["subclass3"],
            morphemes["conjugation_type"],
            morphemes["conjugated_form"],
            morphemes["original_form"],
            morphemes["yomi"],
            morphemes["prononciation"],
        )

    if node_type == "NORMAL":
        geo = tuple()
    elif node_type == "GEOWORD":
        geoword_properties = geojson["properties"]["geoword_properties"]
        prefix = geoword_properties["prefix"][0] \
          if "prefix" in geoword_properties else ""
        suffix = geoword_properties["suffix"][0] \
          if "suffix" in geoword_properties else ""

        geo = (
            geoword_properties["ne_class"],
            geoword_properties["geolod_id"],
            prefix + geoword_properties["body"] + suffix,
            geoword_properties["longitude"],
            geoword_properties["latitude"],
        )

    else:  # ADDRESS
        address_properties = properties["address_properties"]
        levels = (
            "不明",
            "都道府県",
            "郡",
            "市町村・特別区",
            "区",
            "大字",
            "字・小字",
            "街区・地番",
            "住居番号・枝番"
        )
        level = levels[address_properties["level"]]
        original_form = "".join(address_properties["fullname"])
        yomi = "".join(m["properties"]["morphemes"]["yomi"]
                        for m in morphemes)
        prononciation = "".join(m["properties"]["morphemes"]
                        ["prononciation"] for m in morphemes)
        common = (
            "名詞",
            "固有名詞",
            "住所",
            level,
            "*",
            "*",
            original_form,
            yomi,
            prononciation,
        )
        geo = (
            "住所",
            "",
            original_form,
            str(address_properties["x"]),
            str(address_properties["y"]),
        )

    return (properties["surface"], common, geo,)


def pp_mecab(geojson_list, file=None):
    """
    geoparse() の結果（GeoJSON互換）を mecab 類似書式で出力します。

    Parameters
    ----------
    geojson_list : list
        geoparse() 結果の GeoJSON 互換 dict のリスト。
    file : file descriptor, optional
        出力先のファイルデスクリプタ。デフォルトは None です。

    Examples
    --------
    >>> import pygeonlp.api as api
    >>> from pygeonlp.api.devtool import pp_mecab
    >>> pp_mecab(api.geoparse('目黒駅は品川区にあります。'))
    目黒駅  名詞,固有名詞,地名語,Xy26iV:目黒駅,*,*,目黒駅,, 鉄道施設/鉄道駅,Xy26iV,目黒駅,139.71566,35.632485
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    品川区  名詞,固有名詞,地名語,kEAYBl:品川区,*,*,品川区,, 市区町村,kEAYBl,品川区,139.73025000,35.60906600
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS
    <BLANKLINE>
    """  # noqa: E501

    for geojson in geojson_list:
        if geojson is not None:
            line = _mecabline(geojson)
            print("\t".join((
                    line[0],
                    ",".join(line[1]),
                    ",".join(line[2]),
                )), end="\n", file=file
            )

    print("EOS", file=file)
