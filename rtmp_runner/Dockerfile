FROM python:3.7-slim

RUN apt-get update
RUN apt-get install -y python-dev pkg-config \
   libavformat-dev libavcodec-dev libavdevice-dev \
   libavutil-dev libswscale-dev libswresample-dev libavfilter-dev \
   autoconf automake build-essential cmake \
   libass-dev libfreetype6-dev libjpeg-dev libtheora-dev \
   libtool libvorbis-dev libx264-dev \
   pkg-config yasm zlib1g-dev libpq-dev openssl xz-utils \
   libopus-dev libvpx-dev
ADD ./requirements.txt /requirements.txt
RUN  pip3 install --upgrade pip && \
    pip3 install --upgrade setuptools  && \
    pip3 install \
        --no-cache-dir \
        -r requirements.txt

ADD ./src /srv/src
EXPOSE 8080
WORKDIR /srv/src

#RUN python3 manage.py migrate --settings=project.settings


CMD ["python3", "/srv/src/rtmp.py", "--stream_id", "3af5fa85-6286-4fad-77f9-9a73b91523ee", "--cluster", "https://console.dev.videocoin.network/api/v1"]
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080", "--settings=project.settings"]