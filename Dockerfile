FROM centos:latest

WORKDIR /work
COPY requirements.txt /work/requirements.txt
COPY requirements-dev.txt /work/requirements-dev.txt

RUN yum -y update; \
    # centos packages
    yum install -y epel-release; \
    #yum install -y python-pip numpy python-devel gdal-devel gdal-python swig git wget gcc-c++; \
    yum install -y python-pip numpy python-devel swig git wget gcc-c++ make; \
    # needed for potrace
    yum install -y agg-devel potrace-devel;

# GDAL
ENV GDAL_VERSION 1.11.5
RUN \
    wget http://download.osgeo.org/gdal/$GDAL_VERSION/gdal-$GDAL_VERSION.tar.gz && \
    tar -xzvf gdal-$GDAL_VERSION.tar.gz && \
    cd gdal-$GDAL_VERSION && \
    ./configure \
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
        --with-jasper=no \
        --with-ecw=no \
        --with-kakadu=no \
        --with-mrsid=no \
        --with-jp2mrsid=no \
        --with-bsb=no \
        --with-grib=no \
        --with-mysql=no \
        --with-ingres=no \
        --with-xerces=no \
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

RUN \
    pip install wheel; \
    pip install -r requirements.txt; \
    pip install -r requirements-dev.txt;
