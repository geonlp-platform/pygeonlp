import doctest
import os
import unittest

import pygeonlp.api as api


def setup(test):
    testdir = os.path.abspath(os.path.join(os.getcwd(), 'apitest'))
    os.environ['GEONLP_DB_DIR'] = testdir
    os.makedirs(testdir, 0o755, exist_ok=True)
    api.setup_basic_database(db_dir=testdir)
    api.init(db_dir=testdir)


def load_tests(loader, tests, ignore):
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
    unittest.main()
