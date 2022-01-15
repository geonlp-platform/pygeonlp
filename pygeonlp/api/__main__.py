import logging
import os
import site
import sys

from docopt import docopt
import pygeonlp.api
from pygeonlp.api.dict_manager import DictManager

logger = logging.getLogger(__name__)

HELP = """
'pygeonlp' は、自然言語テキストを解析して地名を抽出する
ジオタギング (geo-tagging) またはジオパージング (geo-parsing) と呼ばれる
処理を行なうオープンソースソフトウェアです。

Usage:
  {p} -h
  {p} list-dictionaries [--db-dir=<dir>]
  {p} show-dictionary [--db-dir=<dir>] <id>
  {p} clear-database [--db-dir=<dir>]
  {p} add-dictionary [--db-dir=<dir>] (<json-path> <csv-path> | <url>)
  {p} remove-dictionary [--db-dir=<dir>] <id>
  {p} download-dictionary [--db-dir=<dir>] <url> <json-path> <csv-path>
  {p} setup [--db-dir=<dir>] [<dict-src-dir>]

Options:
  -h --help           Show this help.
  --db-dir=<dir>      Specify the database directory.

Examples:

- パッケージに同梱されている辞書ファイルから初期データベースを設定します
  python -m {p} setup

- インストールされている辞書情報一覧を表示します
  python -m {p} list-dictionaries

- Identifire で指定した辞書の情報を表示します
  python -m {p} show-dictionary geonlp:geoshape-city

- インストールされている辞書をクリア（全て削除）します
  python -m {p} clear-database

- JSONおよびCSVファイルから辞書をインストールします
  python -m {p} add-dictionary base_data/geoshape-city.json base_data/geoshape-city.csv

- ウェブから辞書をインストールします
  python -m {p} add-dictionary https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/

- ウェブから辞書をダウンロードし、JSONおよびCSVファイルに保存します
  python -m {p} download-dictionary https://geonlp.ex.nii.ac.jp/dictionary/geoshape-city/ geoshape.json geoshape.csv
""".format(p='pygeonlp.api')


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


if __name__ == '__main__':
    args = docopt(HELP)

    if args['--db-dir']:
        db_dir = args['--db-dir']
    else:
        db_dir = pygeonlp.api.get_db_dir()

    manager = pygeonlp.api.dict_manager.DictManager(db_dir)

    if args['list-dictionaries']:
        print(manager.getDictionaries())
        exit(0)

    if args['show-dictionary']:
        print(manager.getDictionary(args['<id>']))
        exit(0)

    if args['clear-database']:
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
        manager.removeDictionary(args['<id>'])
        manager.updateIndex()
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
