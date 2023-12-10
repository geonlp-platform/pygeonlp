import json
import logging
import os
import site
import sys

from docopt import docopt
import pygeonlp.api
from pygeonlp.api.dict_manager import DictManager
from pygeonlp.api.devtool import pp_mecab

logger = logging.getLogger(__name__)

HELP = """
'pygeonlp' は、自然言語テキストを解析して地名を抽出する
ジオタギング (geo-tagging) またはジオパージング (geo-parsing) と呼ばれる
処理を行なうオープンソースソフトウェアです。

Usage:
  {p} -h
  {p} --version
  {p} geoparse [--db-dir=<dir>] [--json] [<file>]
  {p} search [--db-dir=<dir>] <word>
  {p} list-dictionaries [--db-dir=<dir>]
  {p} show-dictionary [--db-dir=<dir>] <id>
  {p} clear-dictionaries [--db-dir=<dir>]
  {p} add-dictionary [--db-dir=<dir>] (<json-path> <csv-path> | <url>)
  {p} remove-dictionary [--db-dir=<dir>] <id>
  {p} download-dictionary [--db-dir=<dir>] <url> <json-path> <csv-path>
  {p} setup [--db-dir=<dir>] [<dict-src-dir>]

Options:
  -h --help           このヘルプを表示します。
  --json              JSON で出力します。
  --db-dir=<dir>      データベースディレクトリを指定します。

Examples:
- "test.txt" のテキストをジオパーズした結果を出力します
  {p} geoparse test.txt

- "神保町" をデータベースから検索します
  {p} search 神保町

- パッケージに同梱されている辞書ファイルから初期データベースを設定します
  {p} setup

- インストールされている辞書情報一覧を表示します
  {p} list-dictionaries

- 指定した辞書の情報を表示します（辞書の識別子で指定）
  {p} show-dictionary geonlp:geoshape-city

- インストールされている辞書をクリア（全て削除）します
  {p} clear-dictionaries

- ウェブから辞書をインストールします
  {p} add-dictionary https://geonlp.ex.nii.ac.jp/dictionary/ksj-post-office/

- 指定した辞書をアンインストールします

  {p} remove-dictionary geonlp:post-office

- ウェブから辞書をダウンロードし、JSONおよびCSVファイルに保存します
  {p} download-dictionary https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/ geoshape.json geoshape.csv

- JSONおよびCSVファイルから辞書をインストールします
  {p} add-dictionary base_data/geoshape-city.json base_data/geoshape-city.csv

""".format(p='pygeonlp')


def setup_basic_database(db_dir=None, src_dir=None):
    """
    基本的な地名解析辞書を登録したデータベースを作成します。

    Parameters
    ----------
    db_dir : str, optional
        データベースディレクトリを指定します。
        ここにデータベースファイルを作成します。
        既にデータベースが存在する場合は追記します（つまり、
        既に登録済みの地名解析辞書のデータは失われません）。
        省略された場合には ``get_db_dir()`` で決定します。

    src_dir : str, optional
        地名解析辞書ファイルが配置されているディレクトリ。
        省略された場合には、 ``sys.prefix`` または ``site.USER_BASE`` の
        下に ``pygeonlp_basedata`` がないか探します。
        見つからない場合は ``RuntimeError`` を送出しますので、
        ディレクトリを指定してください。
    """
    data_dir = None
    base_dir = os.getcwd()
    candidates = []
    if src_dir:
        candidates.append(src_dir)

    candidates += [
        os.path.join(sys.prefix, 'pygeonlp_basedata'),
        os.path.join(site.USER_BASE, 'pygeonlp_basedata'),
        os.path.join(base_dir, 'base_data'),
        os.path.join(base_dir, 'pygeonlp_basedata'),
    ]

    for cand in candidates:
        if os.path.exists(cand):
            data_dir = cand
            break

    if not data_dir:
        files = DictManager.get_package_files()
        for path in files:
            pos = path.find('/pygeonlp_basedata')
            if pos < 0:
                continue

            data_dir = path[0:pos + len('/pygeonlp_basedata')]

    if not data_dir:
        raise RuntimeError("地名解析辞書がインストールされたディレクトリが見つかりません。")

    if db_dir is None:
        db_dir = pygeonlp.api.get_db_dir()

    os.makedirs(db_dir, 0o755, exist_ok=True)
    manager = DictManager(db_dir=db_dir)

    updated = False
    if manager.getDictionary('geonlp:geoshape-city') is None:
        manager.addDictionaryFromFile(
            jsonfile=os.path.join(data_dir, 'geoshape-city.json'),
            csvfile=os.path.join(data_dir, 'geoshape-city.csv'))
        updated = True

    if manager.getDictionary('geonlp:geoshape-pref') is None:
        manager.addDictionaryFromFile(
            jsonfile=os.path.join(data_dir, 'geoshape-pref.json'),
            csvfile=os.path.join(data_dir, 'geoshape-pref.csv'))
        updated = True

    if manager.getDictionary('geonlp:ksj-station-N02') is None:
        manager.addDictionaryFromFile(
            jsonfile=os.path.join(data_dir, 'ksj-station-N02.json'),
            csvfile=os.path.join(data_dir, 'ksj-station-N02.csv'))
        updated = True

    if updated:
        manager.updateIndex()


def main():
    args = docopt(HELP)

    if args['--version']:
        print(pygeonlp.api.__version__)
        exit(0)

    if args['--db-dir']:
        db_dir = args['--db-dir']
    else:
        db_dir = pygeonlp.api.get_db_dir()

    manager = pygeonlp.api.dict_manager.DictManager(db_dir)
    if manager.capi_ma is None and args['setup'] is False:
        while True:
            r = input(
                f"{db_dir} に基本辞書セットをインストールしますか? (y/n):"
            )
            if r[0].lower() == 'y':
                manager.setupBasicDatabase()
                print("完了しました。")
                break
            else:
                print((
                    "pygeonlp setup コマンドを実行して"
                    "辞書をインストールしてください。"
                ))
                exit(1)

    if args['geoparse']:
        pygeonlp.api.init(db_dir=db_dir)
        if args['<file>']:
            with open(args['<file>'], "r") as f:
                for line in f:
                    line = line.rstrip()
                    if line == "":
                        continue

                    geojson = pygeonlp.api.geoparse(line)
                    if args['--json']:
                        print(json.dumps(geojson, ensure_ascii=False))
                    else:
                        print(pp_mecab(geojson))

        else:
            for line in sys.stdin:
                line = line.rstrip()
                if line != "":
                    geojson = pygeonlp.api.geoparse(line)
                    if args['--json']:
                        print(json.dumps(geojson, ensure_ascii=False))
                    else:
                        pp_mecab(geojson)

        exit(0)

    if args['search']:
        pygeonlp.api.init(db_dir=db_dir)
        word = pygeonlp.api.searchWord(args["<word>"])
        print(json.dumps(word, ensure_ascii=False))
        exit(0)

    if args['list-dictionaries']:
        for metadata in manager.getDictionaries():
            dic = json.loads(metadata.jsonld)
            print("{} : {}\n- {}\n{}\n".format(
                metadata.get_identifier(),
                metadata.get_name(),
                dic["url"],
                dic["description"]))

        exit(0)

    if args['show-dictionary']:
        print(
            json.dumps(
                json.loads(manager.getDictionary(args['<id>']).jsonld),
                indent=2,
                ensure_ascii=False
            )
        )
        exit(0)

    if args['clear-dictionaries']:
        manager.clearDatabase()
        manager.updateIndex()
        exit(0)

    if args['add-dictionary']:
        if args['<json-path>']:
            manager.addDictionaryFromFile(
                args['<json-path>'], args['<csv-path>'])
        else:
            manager.addDictionaryFromWeb(args['<url>'])

        manager.updateIndex()
        exit(0)

    if args['remove-dictionary']:
        metadata = manager.getDictionary(args['<id>'])
        if metadata is not None:
            manager.removeDictionary(args['<id>'])
            manager.updateIndex()
        else:  # Supports cases specified by URLs.
            for metadata in manager.getDictionaries():
                dic = json.loads(metadata.jsonld)
                if dic["url"] == args["<id>"]:
                    identifier = metadata.get_identifier()
                    manager.removeDictionary(identifier)
                    manager.updateIndex()
                    break

            else:  # Call the method to raise error.
                manager.removeDictionary(args['<id>'])

        exit(0)

    if args['download-dictionary']:
        manager.saveDictionaryFromWeb(
            jsonfile=args['<json-path>'],
            csvfile=args['<csv-path>'],
            url=args['<url>'])

        exit(0)

    if args['setup']:
        src_dir = args['<dict-src-dir>']
        manager.setupBasicDatabase(src_dir=src_dir)
        exit(0)

    raise RuntimeError('Unexpected args: {}'.format(args))


if __name__ == '__main__':
    main()
