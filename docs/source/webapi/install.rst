.. _install_pygeonlp_webapi:

インストール手順
================

ウェブサービス機能は pygeonlp に含まれているため、
:ref:`install_pygeonlp` に従って pygeonlp をインストールしてください。

また、ウェブサービス機能でのみ利用する Python パッケージ
`Flask JSON-RPC <https://github.com/cenobites/flask-jsonrpc>`_ は
別途インストールする必要があります。

Flask JSON-RPC をインストールするには pip コマンドを利用します。 ::

  pip3 install flask-jsonrpc


.. _setup_pygeonlp_webapi:

インストール後の作業
--------------------

**データベースの作成**

もしまだの場合、 pygeonlp コマンドでデータベースを作成してください。 ::

  $ pygeonlp setup

で基本辞書セットがインストールされたデータベースを作成します。

データベースの管理方法については :ref:`cli_setup` 以降の説明を参照してください。


アンインストール
----------------

ウェブサービス機能が不要になった場合は Flask JSON-RPC
をアンインストールしてください。 ::

  $ pip3 uninstall flask-jsonrpc

Pygeonlp もアンインストールする場合は :ref:`uninstall_pygeonlp`
の手順に従ってください。
