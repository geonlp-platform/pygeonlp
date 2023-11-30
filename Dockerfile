# syntax = docker/dockerfile:1.2

FROM osgeo/gdal:ubuntu-full-3.6.3
# This image is built on "Ubuntu 22.04.2 LTS"

ENV JAGEOCODER_DB2_DIR /opt/db2

# Install the required Python packages.
RUN apt-get update && apt-get install -y \
    libmecab-dev \
    mecab-ipadic-utf8 \
    libboost-all-dev \
    libsqlite3-dev \
    curl \
    python3 \
    python3-dev \
    python3-pip
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install pygeonlp && python3 -m pygeonlp.api setup

# Install Jageocoder gaiku_all_v20.zip
RUN curl https://www.info-proto.com/static/jageocoder/latest/gaiku_all_v21.zip \
    -o /opt/gaiku_all_v21.zip && \
    jageocoder install-dictionary /opt/gaiku_all_v21.zip && \
    rm /opt/gaiku_all_v21.zip
