.. _pygeonlp_envvars:

環境変数
========

pygeonlp で利用できる環境変数は以下の通りです。

**GEONLP_DB_DIR**
    :ref:`pygeonlp_terms_db_dir` を指定します。

    指定しない場合、 **$(HOME)/geonlp/db** にデータベースを作成します。
    HOME も設定されていない場合はエラーになります。

**GEONLP_MAX_COMBINATIONS**
    解析可能なパス表現の最大値を指定します。
    文を解析した時に、たとえば3番目の単語に4種類の候補があり、
    6番目の単語に3種類の候補が、8番目の単語に5種類の候補があると、
    パス表現の数はこれらの組み合わせなので 4×3×5=60 になります。
    
    組み合わせの数が最大値を超えると
    :py:class:`~pygeonlp.api.linker.LinkerError` になります。

    指定しない場合は 256 です。もし **LinkerError** が出てしまう場合は
    文をより短く分解するか、 **GEONLP_MAX_COMBINATIONS** の値を
    大きめに指定してください。

**GEONLP_EXCLUDED_WORD**
    地名語として解析したくない語を指定します。
    複数の語を指定したい場合は **|** を区切りとして列挙してください。
    詳しくは :ref:`tuning_excluded_word` を参照してください。

    指定しない場合は **本部|一部|月** です。

**GEONLP_ADDRESS_CLASS**
    住所の先頭として抽出する地名語の固有名クラスを正規表現で指定します。

    たとえば「NIIは千代田区一ツ橋にあります」という文から
    「千代田区一ツ橋」を住所として抽出するには、「千代田区」の
    固有名クラスである「市区町村」が **GEONLP_ADDRESS_CLASS** に
    指定されている正規表現とマッチする必要があります。

    指定しない場合は **r'^(都道府県|市区町村|行政地域|居住地名)(\/.+|)'**
    です。

GEONLP_MECAB_DIC_DIR
    形態素解析に利用する MeCab システム辞書のディレクトリを指定します。

    :ref:`link_neologd` を利用する場合は NEologd の辞書をインストールした
    ディレクトリを指定してください。

    指定しない場合は MeCab のシステム辞書を利用します。

JAGEOCODER_DB2_DIR
    住所ジオコーダ jageocoder の住所辞書をインストールしたディレクトリを
    指定します。

    指定しない場合は Python ライブラリがインストールされる
    ディレクトリの下の **jageocoder/db2** にインストールされます。
    
    **jageocoder get-db-dir** コマンドで確認できます。
