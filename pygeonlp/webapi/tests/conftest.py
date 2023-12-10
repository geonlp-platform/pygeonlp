import pytest

import pygeonlp.api as geonlp_api
from pygeonlp.api.dict_manager import DictManager
from pygeonlp.webapi.app import app
from pygeonlp.webapi import config


@pytest.fixture(scope="session", autouse=True)
def createTempDatabase(tmp_path_factory):
    """
    テスト用に一時的な GeoNLP データベースを作成します。
    テストを実行する際に一度だけ実行されます。
    """
    if True:
        # Setup test database in a temporary directory
        db_dir = str(tmp_path_factory.mktemp('db'))
        manager = DictManager(db_dir=db_dir)
        manager.setupBasicDatabase()
        geonlp_api.init(db_dir=db_dir,
                        **(config.GEONLP_API_OPTIONS))
    else:
        # or, use default database under GEONLP_DB_DIR
        pass


@pytest.fixture(scope="function", autouse=True)
def setup():
    """
    各テスト実行前に自動的に行なう処理を呼びだします。
    """
    app.config['TESTING'] = True


@pytest.fixture
def client():
    """
    Flask アプリケーションのテストクライアントを返します。
    """
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(scope="session")
def require_gdal():
    try:
        from osgeo import gdal
        return gdal.VersionInfo()
    except ModuleNotFoundError:
        pytest.skip("Skip (GDAL not installed)")
