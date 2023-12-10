.. _run_docker:

Docker で実行
=============

ウェブサービスのサーバを Docker で起動する方法について説明します。


イメージの作成
--------------

空のフォルダを作成し、その中にテキストエディタで
以下の内容を含む Dockerfile を作成します。

.. literalinclude:: ../../../Dockerfile-webapi
  :language: docker

jageocoder や neologd を利用したい場合はコメントを外してください。

Docker ファイルを作成したディレクトリで、
`docker build <https://docs.docker.jp/engine/reference/commandline/build.html>`_
を実行してイメージを作成します。 ::

  $ docker build docker build -t pygeonlp_webapi_image .

これで *pygeonlp_webapi_image* というタグ名を持つイメージが作成されます。


サーバコンテナを起動
--------------------

作成したイメージから、
`docker run <https://docs.docker.jp/engine/reference/run.html>`_
でサーバを実行するコンテナを起動します。 ::

  $ docker run --name pygeonlp_webapi -d -p 5000:5000 pygeonlp_webapi_image

**-d** オプションはデタッチドモード (コンテナをバックグラウンドで実行) を指定し、
**-p** オプションは Docker のホストのポートをコンテナ内のポートに接続します。
**--name** オプションでコンテナ名を指定しているので、 *pygeonlp_webapi* という
名前を持つコンテナを生成します。

この状態で WebAPI サーバが起動しているので、
http://localhost:5000/api/browse にアクセスして WebAPI ブラウザが
動いていることを確認します。

サーバコンテナを終了
--------------------

サーバコンテナはディタッチドモードで動き続けるため、終了するときには
`docker stop <https://docs.docker.jp/engine/reference/commandline/stop.html>`_
で停止します。パラメータはコンテナ名です。 ::

  $ docker stop pygeonlp_webapi

終了したサーバコンテナは
`docker start <https://docs.docker.jp/engine/reference/commandline/start.html>`_
で再起動できます。 ::

  $ docker start pygeonlp_webapi


コンテナとイメージを削除
------------------------

不要になったコンテナは
`docker rm <https://docs.docker.jp/engine/reference/commandline/rm.html>`_
で削除できます。パラメータはイメージのタグ名です。 ::

  $ docker rm pygeonlp_webapi

イメージも不要になった場合は、
`docker rmi <https://docs.docker.jp/engine/reference/commandline/rmi.html>`_
で削除します。 ::

  $ docker rmi pygeonlp_webapi_image
