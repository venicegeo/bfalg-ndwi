#!/bin/bash

# system paths
LIBPATH='/usr/lib/x86_64-linux-gnu'
PYTHONPATH='/usr/local/lib/python2.7/dist-packages'

mkdir -p lib/python2.7

# package libraries
cp -L /usr/local/lib/libgdal.so.1 lib/
cp -L $LIBPATH/libpotrace.so.0 lib/

# package app and python libs
pip install ../
# rsync is the best way
rsync -ax $PYTHONPATH ./lib/python2.7/ --exclude-from excluded_packages
ln -s GDAL-1.11.5-py2.7-linux-x86_64.egg/osgeo lib/python2.7/dist-packages/osgeo
# create link to CLI
ln -s lib/python2.7/dist-packages/bfalg_ndwi/ndwi.py bfalg-ndwi.py

# zip up contents
#zip -ruq ../deploy.zip ./ -x excluded_packages package*.sh Dockerfile.*
