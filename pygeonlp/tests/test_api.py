import doctest
import os
import unittest

import pygeonlp.api as api


def setup(test):
    testdir = os.path.abspath(os.path.join(os.getcwd(), "apitest"))
    os.environ['GEONLP_DIR'] = testdir
    os.makedirs(testdir, 0o755, exist_ok=True)
    api.init(dict_dir=testdir)

    updated = False
    if api.getDictionary('geonlp:geoshape-city') is None:
        api.addDictionaryFromFile(
            jsonfile='base_data/geoshape-city.json',
            csvfile='base_data/geoshape-city.csv')
        updated = True

    if api.getDictionary('geonlp:geoshape-pref') is None:
        api.addDictionaryFromFile(
            jsonfile='base_data/geoshape-pref.json',
            csvfile='base_data/geoshape-pref.csv')
        updated = True

    if api.getDictionary('geonlp:ksj-station-N02-2019') is None:
        api.addDictionaryFromFile(
            jsonfile='base_data/ksj-station-N02-2019.json',
            csvfile='base_data/ksj-station-N02-2019.csv')
        updated = True

    if updated:
        api.updateIndex()


def load_tests(loader, tests, ignore):
    from pygeonlp.api import temporal_filter
    modules = [
        api, api.service, api.metadata, api.dictionary, api.node,
        api.parser, api.linker,
        api.filter, temporal_filter,
    ]

    try:
        from osgeo import ogr
        from pygeonlp.api import spatial_filter
        modules.append(spatial_filter)
    except:
        # Since GDAL is not installed, spatial_filter test will be skipped.
        pass

    flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    for module in modules:
        tests.addTest(
            doctest.DocTestSuite(module, setUp=setup, optionflags=flags))

    return tests


if __name__ == "__main__":
    unittest.main()
