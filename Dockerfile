# bfalg-ndwi
# https://github.com/venicegeo/bfalg-ndwi

# Copyright 2016, RadiantBlue Technologies, Inc.

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

FROM cloudfoundry/cflinuxfs2

WORKDIR /build

RUN apt-get update; \
    apt-get install -y wget python-pip python-dev python-numpy swig git zip libproj-dev libgeos-dev; \
    apt-get install -y libagg-dev; # libpotrace-dev;

# CentOS
#RUN yum -y update; \
#    yum install -y epel-release; \
#    yum install -y python-pip numpy python-devel swig git wget gcc-c++ make zip; \
#    yum install -y agg-devel potrace-devel;

# environment variables
ENV \
    #GDAL_VERSION=1.11.5 \
    GDAL_VERSION=2.1.2 \
    GDAL_CONFIG=/usr/local/bin/gdal-config \
    POTRACE_VERSION=1.14

# install potrace
RUN \
    wget http://potrace.sourceforge.net/download/$POTRACE_VERSION/potrace-$POTRACE_VERSION.tar.gz; \
    tar -xzvf potrace-$POTRACE_VERSION.tar.gz; \
    cd potrace-$POTRACE_VERSION; \
    ./configure --with-libpotrace; \
    make && make install && cd .. && \
    rm -rf potrace-$POTRACE_VERSION*

# install gdal
RUN \
    wget http://download.osgeo.org/gdal/$GDAL_VERSION/gdal-$GDAL_VERSION.tar.gz && \
    tar -xzvf gdal-$GDAL_VERSION.tar.gz && \
    cd gdal-$GDAL_VERSION && \
    ./configure \
        --with-static-proj4 \
        --with-geotiff=yes \
        --with-python=yes \
        --with-hdf4=no \
        --with-hdf5=no \
        --with-threads \
        --with-gif=no \
        --with-pg=no \
        --with-grass=no \
        --with-libgrass=no \
        --with-cfitsio=no \
        --with-pcraster=no \
        --with-netcdf=no \
        --with-png=no \
        --with-jpeg=no \
        --with-gif=no \
        --with-ogdi=no \
        --with-fme=no \
        --with-jasper=yes \
        --with-ecw=no \
        --with-kakadu=no \
        --with-mrsid=no \
        --with-jp2mrsid=no \
        --with-bsb=no \
        --with-grib=no \
        --with-mysql=no \
        --with-ingres=no \
        --with-xerces=yes \
        --with-expat=no \
        --with-odbc=no \
        --with-curl=yes \
        --with-sqlite3=no \
        --with-dwgdirect=no \
        --with-idb=no \
        --with-sde=no \
        --with-perl=no \
        --with-php=no \
        --without-mrf \
        --with-hide-internal-symbols=yes \
        CFLAGS="-O2 -Os" CXXFLAGS="-O2 -Os" && \
        make && make install && cd .. && \
        rm -rf gdal-$GDAL_VERSION*

ENV \
    LD_LIBRARY_PATH=/usr/local/lib

# install requirements
COPY requirements.txt /build/requirements.txt
COPY requirements-dev.txt /build/requirements-dev.txt

RUN \
    pip install wheel numpy; \
    pip install -r requirements.txt; \
    pip install -r requirements-dev.txt;
