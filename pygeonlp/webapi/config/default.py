import logging
import os

import jageocoder
import pygeonlp.api as geonlp_api


class BaseConfig(object):
    DEBUG = False
    TESTING = False

    GEONLP_DIR = geonlp_api.get_db_dir()
    JAGEOCODER_DIR = jageocoder.get_db_dir()
    MECAB_DIC_DIR = os.environ.get('GEONLP_MECAB_DIC_DIR')
    GEONLP_API_OPTIONS = {}

    if MECAB_DIC_DIR is not None:
        GEONLP_API_OPTIONS['system_dic_dir'] = MECAB_DIC_DIR

    LOGGING = {
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': logging.INFO,
            'handlers': ['wsgi']
        }
    }


class ProductionConfig(BaseConfig):
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


config = DevelopmentConfig()
