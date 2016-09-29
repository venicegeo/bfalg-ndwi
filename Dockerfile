FROM debian:jessie

RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install -y python-pip python-dev libgdal-dev
RUN pip install numpy

WORKDIR /work
COPY ./ /work

RUN pip install .
