FROM gcr.io/videocoin-network/python:3.7-ubuntu

ADD ./requirements.txt /requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssl \
        wget \
        bzip2 \
        libssl-dev \
        sqlite3 \
        libsqlite3-dev \
        mediainfo \
        libmediainfo-dev \
        ffmpeg \
        curl \
        build-essential \
        git-core \
        xz-utils && \
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
EXPOSE 8080

WORKDIR /srv/src
RUN python3 manage.py migrate --settings=project.settings
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080", "--settings=project.settings"]