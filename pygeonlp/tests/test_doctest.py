import doctest
import os
import shutil
import unittest

import pygeonlp.api as api

"""
doc_string に書かれているサンプルコードを doctest で検証するテスト。

このモジュールのテストを行なうには、次のコマンドを実行してください。

python -m unittest -v pygeonlp.tests.test_doctest
"""


def get_testdir():
    return os.path.abspath(os.path.join(os.getcwd(), 'apitest'))


def setup(test):
    testdir = get_testdir()
    os.environ['GEONLP_DB_DIR'] = testdir
    os.makedirs(testdir, 0o755, exist_ok=True)
    api.init(db_dir=testdir)

    # デフォルト以外の辞書が登録されていたら
    # データベースを作り直す
    default_dics = [
        'geonlp:geoshape-city',
        'geonlp:geoshape-pref',
        'geonlp:ksj-station-N02',
    ]

    installed_dictionaries = [
        x.get_identifier() for x in api.getDictionaries()]
    for identifier in installed_dictionaries:
        if identifier not in default_dics:
            api.clearDatabase()
            break

    api.setup_basic_database(db_dir=testdir)
    api.init(db_dir=testdir)


def load_tests(loader, tests, ignore):
    shutil.rmtree(get_testdir(), ignore_errors=True)

    from pygeonlp.api import devtool, temporal_filter
    modules = [
        api, api.service, api.metadata, api.dictionary, api.node,
        api.parser, api.linker, devtool,
        api.filter, temporal_filter,
    ]
    
    try:
        from pygeonlp.api import spatial_filter
        spatial_filter.SpatialFilter.get_geometry_from_geojson(
            {'type': 'Point', 'coordinates': [139.6917337, 35.6895014]})
        modules.append(spatial_filter)
    except api.filter.FilterError:
        # Since GDAL is not installed, spatial_filter test will be skipped.
        pass

    flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

    for module in modules:
        tests.addTest(
            doctest.DocTestSuite(module, setUp=setup, optionflags=flags))

    return tests


if __name__ == "__main__":
    unittest.main(failfast=True)
