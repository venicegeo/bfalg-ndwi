#!/bin/bash

DEPLOY_DIR=deploy

mkdir -p $DEPLOY_DIR/lib/python2.7
mkdir -p $DEPLOY_DIR/lib64/python2.7

# package libraries
cp -L /usr/lib64/libagg.so.2 $DEPLOY_DIR/lib64/
cp -L /usr/lib64/libpotrace.so.0 $DEPLOY_DIR/lib64/
cp /usr/local/lib/libgdal.so.1 $DEPLOY_DIR/lib/

# package app and python libs
pip install .
# rsync is the best way
rsync -ax /usr/lib/python2.7/site-packages/ $DEPLOY_DIR/lib/python2.7/site-packages/ --exclude-from $DEPLOY_DIR/excluded_packages
rsync -ax /usr/lib64/python2.7/site-packages/ $DEPLOY_DIR/lib64/python2.7/site-packages/ --exclude-from $DEPLOY_DIR/excluded_packages
# but if running docker on mac, comment out above two lines and uncomment these two lines
#cp -R /usr/lib $DEPLOY_DIR/lib
#cp -R /usr/lib64 $DEPLOY_DIR/lib64
# gdal seems to be in it's own dir, so we'll link it
ln -s GDAL-1.11.5-py2.7-linux-x86_64.egg/osgeo $DEPLOY_DIR/lib64/python2.7/site-packages/osgeo
# create link to CLI
ln -s lib/python2.7/site-packages/bfalg_ndwi/ndwi.py $DEPLOY_DIR/bfalg-ndwi.py

# zip up contents
cd $DEPLOY_DIR
zip -ruq ../deploy.zip ./ -x excluded_packages package.sh
