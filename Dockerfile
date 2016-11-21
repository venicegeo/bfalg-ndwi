FROM centos:latest

WORKDIR /work
COPY requirements.txt /work/requirements.txt
COPY requirements-dev.txt /work/requirements-dev.txt

RUN yum -y update; \
    # centos packages
    yum install -y epel-release; \
    yum install -y python-pip numpy python-devel gdal-devel gdal-python swig git wget gcc-c++; \
    # needed for potrace
    yum install -y agg-devel potrace-devel;

RUN \
    pip install wheel numpy; \
    pip install -r requirements.txt; \
    pip install -r requirements-dev.txt;
