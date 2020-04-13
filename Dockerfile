FROM gcr.io/videocoin-network/python:3.7-ubuntu

ENV BUILD_DEPS build-essential git-core xz-utils

ARG FAUCET_URL_DEV
ARG FAUCET_URL_SNB
ARG FAUCET_URL_KILI
ARG RPC_NODE_URL_DEV
ARG RPC_NODE_URL_SNB
ARG RPC_NODE_URL_KILI
ARG SENDGRID_KEY
ARG REPORT_EMAILS

ADD ./requirements.txt /requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssl \
        wget \
        bzip2 \
        libssl-dev \
        $BUILD_DEPS && \
    pip3 install --upgrade pip && \
    pip3 install --upgrade setuptools  && \
    pip3 install \
        --no-cache-dir \
        -r requirements.txt && \
    rm -rf \
        $HOME/.ssh \
        $HOME/.nvm \
        $HOME/.cache \
        /usr/src && \
    apt-get purge -y --auto-remove wget curl gcc git-core xz-utils && \
    rm -rf /var/lib/apt/lists/* /usr/src /tmp/*


ADD ./src /srv/src

WORKDIR /srv/src
