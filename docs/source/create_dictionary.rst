.. _create_dictionary:

カスタム辞書の作成
==================

解析したい地名語を含む地名解析辞書がウェブ上に見つからない場合は、
独自の地名解析辞書を作って登録することができます。

地名解析辞書は地名語の表記とその属性のリストを列挙した CSV ファイルと、
辞書の概要（メタデータ）を記述した JSON ファイルから構成されます。

カスタム辞書の例
----------------

ここではサンプルとして、「東京タワー」「東京スカイツリー」という
2つの地名語を含む辞書を作ってみます。

まず CSV ファイルは以下のようになります。

.. literalinclude:: ../../custom_dic/mydic.csv
    :language: text


CSV ファイルの必須項目は以下の5つです。

- entry_id: 辞書内で一意な識別子（1文字以上の文字列）
- body: 地名語の表記（1文字以上255文字以下の文字列）
- ne_class: この語がどんな種類の地名なのかを表す「固有名クラス」
- latitude: 10進度数で表した緯度
- longitude: 10進度数で表した経度

このサンプルでは必須項目の他、 *url* を拡張しています。

次にこの辞書の概要を示す JSON ファイルを作ります。

.. code-block:: javascript

    {
        "name": "カスタム地名語辞書",
        "description": "個人で利用する建物名の辞書",
        "identifier": ["geonlp:my-buildings"]
    }


JSON ファイルの必須項目は *name* と *identifier* の2つです。
ただし *identifier* は必ずリスト ([...]) として定義し、
そのうちの1つは *geonlp:* から始まる必要があります。

このサンプルでは必須項目のほかに、説明用テキストを *description*
に定義しています。

カスタム辞書の登録
------------------

CSV ファイルと JSON ファイルを mydic.csv, mydic.json というファイル名で
保存します（ファイル名は何でも構いません）。

この辞書をデータベースに登録するには **pygeonlp add-dictionary** を使います。 ::

    $ pygeonlp add-dictionary mydic.json mydic.csv

必ず JSON ファイル名を先、 CSV ファイル名を後に指定してください。

登録できたことを確認するため、「東京タワー」をデータベースから検索してみます。 ::

    $ pygeonlp search 東京タワー
    {"_4_mydic001": {"body": "東京タワー", "dictionary_id": 4, "entry_id": "mydic001", "geolod_id": "_4_mydic001", "latitude": "35.65861", "longitude": "139.74556", "ne_class": "通信施設", "url": "https://www.tokyotower.co.jp/", "dictionary_identifier": "geonlp:my-buildings"}}

登録した地名語はジオパーズでも解析できます。 ::

    $ echo "東京タワーは今日も大人気。" | pygeonlp geoparse
    東京タワー      名詞,固有名詞,地名語,_4_mydic001:東京タワー,*,*,東京タワー,,    通信施設,_4_mydic001,東京タワー,139.74556,35.65861
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    今日    名詞,副詞可能,*,*,*,*,今日,キョウ,キョー
    も      助詞,係助詞,*,*,*,*,も,モ,モ
    大人気  名詞,形容動詞語幹,*,*,*,*,大人気,ダイニンキ,ダイニンキ
    。      記号,句点,*,*,*,*,。,。,。
    EOS

非地名語の登録
--------------

地名語以外の単語（人名、組織名などの固有名詞や新語・造語など）を
辞書に登録したい場合、 MeCab ユーザ辞書を利用することができます。
MeCab ユーザ辞書の詳細は MeCab 公式サイトの `単語の追加方法 <https://taku910.github.io/mecab/dic.html>`_
を参照してください。

ここでは例として「情報学研究所」を固有名詞として登録する手順を示します。
登録する前は以下のように解析されます。 ::

    $ echo "情報学研究所にいます。" | pygeonlp geoparse
    情報    名詞,一般,*,*,*,*,情報,ジョウホウ,ジョーホー
    学      名詞,接尾,一般,*,*,*,学,ガク,ガク
    研究所  名詞,一般,*,*,*,*,研究所,ケンキュウジョ,ケンキュージョ
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    い      動詞,自立,*,*,連用形,一段,いる,イ,イ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS

まずユーザ辞書の元となる CSV ファイルを作ります。ファイル名は何でも構いませんが
ここでは *myuserdic.csv* とします。以下の内容を入力します。

.. literalinclude:: ../../custom_dic/myuserdic.csv
    :language: text

.. collapse:: CSV の内容について
    
    CSV ファイルには「表層形,左文脈ID,右文脈ID,コスト,品詞,品詞細分類1,品詞細分類2,
    品詞細分類3,活用型,活用形,原形,読み,発音」を入力する必要があります。
    これらの値が分からない場合は、 mecab コマンドにフォーマットオプションを指定して
    登録したい語と似ている語を解析し、その結果を利用する方法が簡単です。 ::
    
        $ echo "東京大学" | mecab --node-format="%m,%phl,%phr,%c,%H\n"
        東京大学,1292,1292,6081,名詞,固有名詞,組織,*,*,*,東京大学,トウキョウダイガク,トーキョーダイガク
        EOS
    
    登録した語を含む文を解析しても登録した語が出てこない場合は「コスト」を小さくしてみてください。


次にこの CSV ファイルをコンパイルして MeCab ユーザ辞書を作成します。

コンパイルするコマンドは *mecab-dict-index* ですが、環境によって
インストールされている場所が異なります。
Ubuntu では **/usr/lib/mecab/mecab-dict-index** に、
MacOSX + Homebrew では
**/opt/homebrew/Cellar/mecab/0.996/libexec/mecab/mecab-dict-index**
にあります。 *mecab-config* コマンドがインストールされている場合、

    $ mecab-config --libexecdir

で *mecab-dict-index* など MeCab 辞書の管理用コマンドがインストールされている
ディレクトリを取得できます。

また、 MeCab システム辞書がインストールされているディレクトリも調べておく必要があります。

    $ mecab-config --dicdir

を実行して表示されたディレクトリの下に *ipadic* ディレクトリがあり、
その中にシステム辞書がインストールされています。
*dicrc* ファイルが存在することを確認してください。

    Ubuntu 22.04.5 LTS ではこのコマンドは **/usr/lib/x86_64-linux-gnu/mecab/dic**
    を返しますが、実際には **/var/lib/mecab/dic/ipadic-utf8/** にありました。

必要な情報が集まったらユーザ辞書をコンパイルします。 ::

    $ /usr/lib/mecab/mecab-dict-index -d/usr/share/mecab/dic/ipadic \
    -u mecabusr.dic -f utf-8 -t utf-8 myuserdic.csv
    reading myuserdic.csv ... 1
    emitting double-array: 100% |###########################################|
    done!

作成された *mecabusr.dic* を pygeonlp の :ref:`pygeonlp_terms_db_dir`
にコピーします。ユーザ辞書のファイル名は必ず *mecabusr.dic* にしてください。 ::

    $ cp mecabusr.dic ~/geonlp/db/

以上で登録完了です。登録した後は以下のように解析されます。 ::

    echo "情報学研究所にいます。" | pygeonlp geoparse
    情報学研究所    名詞,固有名詞,組織,*,*,*,情報学研究所,ジョウホウガクケンキュウジョ,ジョーホーガクケンキュージョ
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    い      動詞,自立,*,*,連用形,一段,いる,イ,イ
    ます    助動詞,*,*,*,基本形,特殊・マス,ます,マス,マス
    。      記号,句点,*,*,*,*,。,。,。
    EOS
