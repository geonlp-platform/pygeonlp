# Install to Ubuntu22

```
$ python3 -m pipenv install --python /usr/bin/python3.10

$ sudo apt install -y libmecab-dev mecab-ipadic-utf8 libboost-all-dev libsqlite3-dev
$ pip install -e .
$ sudo apt install -y libgdal-dev
$ pip install gdal==3.4.1
$ curl https://www.info-proto.com/static/jageocoder/latest/v2/jukyo_all_v20.zip -o jukyo_all_v20.zip
$ jageocoder install-dictionary jukyo_all_v20.zip
```
