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

上の例では **~/github/mecab-ipadic-neologd/** に GitHub リポジトリを
clone し、 **~/neologd/** に全部入り (-a) の最新辞書 (-n) を
インストールします。

pygeonlp から NEologd を利用する
--------------------------------

pygeonlp で mecab-ipadic-NEologd を MeCab システム辞書として利用するには、
環境変数 **GEONLP_MECAB_DIC_DIR** に neologd をインストールした
ディレクトリを指定してください。 ::

  $ export GEONLP_MECAB_DIC_DIR=~/neologd
  $ echo "国立情報学研究所は千代田区にあります。" | pygeonlp geoparse
  国立情報学研究所        名詞,固有名詞,組織,*,*,*,国立情報学研究所,コクリツジョウホウガクケンキュウジョ,コクリツジョーホーガクケンキュージョ
  は      助詞,係助詞,*,*,*,*,は,ハ,ワ
  千代田区        名詞,固有名詞,地名語,WWIY7G:千代田区,*,,千代田区,,      市区町村,WWIY7G,千代田区,139.75363400,35.69400300
  に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
  あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
  ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
  。      記号,句点,*,*,*,*,。,。,。
  EOS

「国立情報学研究所」が一語の固有名詞として抽出されるようになります。

.. collapse:: (参考) デフォルトシステム辞書の場合

  **GEONLP_MECAB_DIC_DIR** を指定しない場合は
  デフォルトのシステム辞書を利用します。 ::

    $ unset GEONLP_MECAB_DIC_DIR
    $ echo "国立情報学研究所は千代田区にあります。" | pygeonlp geoparse
    国立    名詞,一般,*,*,*,*,国立,コクリツ,コクリツ
    情報    名詞,一般,*,*,*,*,情報,ジョウホウ,ジョーホー
    学      名詞,接尾,一般,*,*,*,学,ガク,ガク
    研究所  名詞,一般,*,*,*,*,研究所,ケンキュウジョ,ケンキュージョ
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    千代田区        名詞,固有名詞,地名語,WWIY7G:千代田区,*,*,千代田区,,     市区町村,WWIY7G,千代田区,139.75363400,35.69400300
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    あり    動詞,自立,*,*,連用形,五段・ラ行,ある,アリ,アリ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS

環境変数を使わずに Python API で実行時に MeCab システム辞書を指定するには、
:py:meth:`pygeonlp.api.init` の解析オプション **system_dic_dir** で
NEologd のカスタムシステム辞書のパスを指定してください。 ::

  $ python
  >>> import pygeonlp.api as api
  >>> import os
  >>> api.init(system_dic_dir=os.path.join(os.environ['HOME'], 'neologd'))
  >>> [(x['properties']['surface'], x['properties']['node_type']) for x in api.geoparse('国立情報学研究所は千代田区にあります。')]
  [('国立情報学研究所', 'NORMAL'), ('は', 'NORMAL'), ('千代田区', 'GEOWORD'), ('に', 'NORMAL'), ('あり', 'NORMAL'), ('ます', 'NORMAL'), ('。', 'NORMAL')]
