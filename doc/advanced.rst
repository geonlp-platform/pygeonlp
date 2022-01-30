.. _advanced_developers:

カスタム解析モジュールの開発
============================

ここでは、より高度な解析を行うモジュールを独自に開発したい場合に
必要な情報を提供します。

デフォルトの解析フローをカスタマイズ
------------------------------------

テキストを解析する ``api.geoparse(text)`` は、実際には
``api.default_workflow()`` が返すデフォルトの Workflow インスタンスを取得し、
そのクラスメソッドである ``workflow.geoparse(text)`` を呼び出すショートカットです。
そのため解析フローをカスタマイズするには、 Workflow クラスの動作を
理解する必要があります。

デフォルトの Workflow の ``geoparse()`` が実行する解析手順は次の通りです。

- Parser を利用して、テキストから :ref:`pygeonlp_terms_lattice_format` を作成

- Filter を適用して、 :ref:`pygeonlp_terms_lattice_format` に含まれる
  候補を絞り込み、より限定された :ref:`pygeonlp_terms_lattice_format` を作成

- Evaluator を利用して、 :ref:`pygeonlp_terms_lattice_format` から
  :ref:`pygeonlp_terms_path_format` を作成

- :ref:`pygeonlp_terms_path_format` を GeoJSON 形式に変換

Workflow クラスは parser, filters, evaluator の3つのメンバーを持ちます。

上記の手順をカスタマイズしたい場合、これらのメンバーを操作すれば
処理を変更することができます。

単純な例として、市区町村クラスを持つ候補以外を削除する
EntityClassFilter をセットするコードは以下のようになります。 ::

  import pygeonlp.api as api
  from pygeonlp.api.filter import EntityClassFilter
  api.init()
  api.default_workflow().filters = [
      EntityClassFilter(r'市区町村/?.*')]
  results = api.geoparse(text)

もう少し複雑な例として、 Parser を独自拡張した MyParser に
置き換えるには、 parser を次のように上書きします。 ::

  import pygeonlp.api as api
  api.init()
  myparser = MyParser(my_parameter)
  api.default_workflow().parser = myparser
  results = api.geoparse(<text>)

独自ワークフロークラスを定義
----------------------------

デフォルト Workflow のメンバを書き換えるとその後の処理にも影響するため、
想定しない副作用を生じる可能性があります。
そのため、 Workflow クラスから派生した独自のワークフロークラス
MyWorkflow を定義し、その ``geoparse()`` を呼び出す方が安全です。 ::

  from pygeonlp.api.workflow import Workflow

  class MyWorkflow(Workflow):

      def __init__(self, my_parameter, **params):
          super().__init__(**params)
          self.parser = MyParser(my_parameter)

  myworkflow = MyWorkflow(my_parameter)
  results = myworkflow.geoparse(text)

もし parser, filters, evaluator を置き換えるだけでは実現できない
ロジックを実装したい場合、 ``Workflow.geoparse()`` を参考にして
独自ワークフロークラスの ``geoparse()`` メソッドを再定義してください。

実装サンプル
------------

Filter, Evaluator, Workflow の拡張実装例が
`GitHub <https://github.com/geonlp-platform/pygeonlp/blob/main/pygeonlp/samples/context.py>`_
にありますので、参照してください。
