#!/bin/bash

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

DEPLOY_DIR=deploy

mkdir -p $DEPLOY_DIR/lib/python2.7

# package libraries
cp -L /usr/lib64/libagg.so.2 $DEPLOY_DIR/lib/
cp -L /usr/lib64/libpotrace.so.0 $DEPLOY_DIR/lib/
cp /usr/local/lib/libgdal.so.1 $DEPLOY_DIR/lib/

# package app and python libs
pip install .
# rsync is the best way
rsync -ax /usr/lib/python2.7/site-packages/ $DEPLOY_DIR/lib/python2.7/site-packages/ --exclude-from $DEPLOY_DIR/excluded_packages
# gdal seems to be in it's own dir, so we'll link it
rsync -ax /usr/lib64/python2.7/site-packages/GDAL-1.11.5-py2.7-linux-x86_64.egg/osgeo $DEPLOY_DIR/lib/python2.7/site-packages/
rsync -ax /usr/lib64/python2.7/site-packages/potrace $DEPLOY_DIR/lib/python2.7/site-packages/
rsync -ax /usr/lib64/python2.7/site-packages/gippy $DEPLOY_DIR/lib/python2.7/site-packages/
# create link to CLI
ln -s lib/python2.7/site-packages/bfalg_ndwi/ndwi.py $DEPLOY_DIR/bfalg-ndwi.py

# zip up contents
cd $DEPLOY_DIR
zip -ruq ../deploy.zip ./ -x excluded_packages package.sh
