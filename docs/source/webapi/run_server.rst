.. _run_server:

サーバ実行
==========

テストサーバ起動
----------------

テストサーバを起動するには次のコマンドを実行します。 ::

  $ python3 -m flask --app=pygeonlp.webapi.app run --port=5000

他のマシンからアクセスする必要がある場合は ``--host=0.0.0.0``
も指定してください。 ::

  $ python3 -m flask --app=pygeonlp.webapi.app run --port=5000 --host=0.0.0.0


テストサーバは ``Ctrl+C`` で終了します。


動作テスト
----------

**Flask JSON-RPC** の web browsable API 機能を利用して、
ブラウザ上で WebAPI の確認とテストを行なうことができます。

サービス起動後、**Web brosable API の URL** (
デフォルトでは http://127.0.0.1:5000/api/browse/ )
を開き、動作確認したいメソッドを左メニューから選択します。

パラメータを入力するダイアログが表示されますので、
必要なパラメータを入力して **Save** ボタンを押すと、
送信されたリクエストが Request 欄に、処理結果が Response 欄に表示されます。


プロダクションサーバ起動
------------------------

Flask はデバッグ・テスト目的のサーバのため、実際に運用する際には
Gunicorn など他の WSGI サーバを利用する必要があります。

たとえば Gunicorn を利用する場合は次のように実行してください。 ::

  $ pip3 install gunicorn
  $ gunicorn pygeonlp.webapi.app:app --bind=127.0.0.1:5000

**--bind** はこのサーバにアクセスできるホストとポートを指定します。
どこからでもアクセスできるサービスをポート 8000 で公開したい場合は
**--bind=0.0.0.0:8000** のように指定してください。


サーバ設定
----------

Pygeonlp の環境変数を利用して WebAPI サーバの設定を変更できます。
詳細は :ref:`pygeonlp_envvars` を参照してください。

.. collapse:: データベースのパスを指定したい場合

  デフォルト以外のディレクトリにデータベースを作成した場合は
  サーバを起動する前に環境変数 **GEONLP_DB_DIR** に
  データベースを作成したディレクトリのパスをセットしてください。 ::

    $ export GEONLP_DB_DIR=/usr/local/share/geonlp/db/


.. collapse:: NEologdを利用したい場合

  MeCab システム辞書として
  `NEologd <https://github.com/neologd/mecab-ipadic-neologd/>`_
  などデフォルトの IPADIC 以外の辞書を利用する場合、
  サーバを起動する前に環境変数 **GEONLP_MECAB_DIC_DIR** に
  辞書ディレクトリのパスをセットしてください。 ::

    $ export MECAB_DIC_DIR=$HOME/mecab-ipadic-neologd/

  詳細は :ref:`link_neologd` を参照してください。


.. collapse:: Jageocoderを利用したい場合

  住所辞書をインストールしたいディレクトリを
  環境変数 **JAGEOCODER_DB2_DIR** に設定して、
  Jageocoder の住所辞書をインストールしてからサーバを起動してください。 ::

    $ export JAGEOCODER_DB2_DIR=$HOME/jageocoder/db/

  詳細は :ref:`link_jageocoder` を参照してください。

