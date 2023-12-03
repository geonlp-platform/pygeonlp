.. _link_neologd:

NEologd 連携
============

pygeonlp を NEologd (Neologism dictionary for MeCab) と
連携することで、テキスト中の固有表現の抽出精度を改善できます。

NEologd のインストール手順は
`公式サイト <https://github.com/neologd/mecab-ipadic-neologd/>`_ を参照してください。

以下に手順の一例を示します。 ::

  $ mkdir -p ~/github
  $ cd ~/github
  $ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
  $ cd mecab-ipadic-neologd
  $ ./bin/install-mecab-ipadic-neologd --prefix ~/neologd -n -a

上の例では ``~/github/mecab-ipadic-neologd/`` に GitHub リポジトリを
clone し、 ``~/neologd/`` に全部入り (-a) の最新辞書 (-n) を
インストールします。

pygeonlp から NEologd を利用する
--------------------------------

pygeonlp で mecab-ipadic-NEologd をシステム辞書として利用するには、
`api.init() <pygeonlp.api.html#pygeonlp.api.init>`_ の解析オプション
``system_dic_dir`` で NEologd のカスタムシステム辞書のパスを
指定してください。 ::

  $ python
  >>> import pygeonlp.api as api
  >>> import os
  >>> api.init(system_dic_dir=os.path.join(os.environ['HOME'], 'neologd'))
  >>> [(x['properties']['surface'], x['properties']['node_type']) for x in api.geoparse('国立情報学研究所は千代田区にあります。')]
  [('国立情報学研究所', 'NORMAL'), ('は', 'NORMAL'), ('千代田区', 'GEOWORD'), ('に', 'NORMAL'), ('あり', 'NORMAL'), ('ます', 'NORMAL'), ('。', 'NORMAL')]

「国立情報学研究所」が一語の固有表現として抽出されます。

比較のため、 ``system_dic_dir`` を指定しない場合は次のようになります。 ::

  $ python
  >>> import pygeonlp.api as api
  >>> api.init()
  >>> [(x['properties']['surface'], x['properties']['node_type']) for x in api.geoparse('国立情報学研究所は千代田区にあります。')]
  [('国立', 'GEOWORD'), ('情報', 'NORMAL'), ('学', 'NORMAL'), ('研究所', 'NORMAL'), ('は', 'NORMAL'), ('千代田区', 'GEOWORD'), ('に', 'NORMAL'), ('あり', 'NORMAL'), ('ます', 'NORMAL'), ('。', 'NORMAL')]

Mecab 標準辞書として NEologd を利用する
---------------------------------------

この手順は非推奨です。

NEologd のカスタムシステム辞書をインストールする際に
``--prefix`` オプションを指定しないと、 Mecab 標準辞書を上書きします。 ::

  $ sudo ./mecab-ipadic-neologd/bin/install-mecab-neologd 

この場合は api.init() で ``system_dic_dir`` を指定しなくても
NEologd カスタムシステム辞書が利用されます。

ただしこの手順は、 OS のパッケージ管理機能がインストールした
システム辞書を変更するため、パッケージ更新の際に問題が起こる
可能性があり、推奨しません。
