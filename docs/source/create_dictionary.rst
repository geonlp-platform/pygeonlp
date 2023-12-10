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
