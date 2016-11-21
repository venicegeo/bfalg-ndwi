#!/bin/bash

DEPLOY_DIR=app/deploy

# package libraries
#mkdir -p $DEPLOY_DIR/lib/python2.7
#mkdir -p $DEPLOY_DIR/lib64/python2.7

#cp /usr/lib64/libhdf5.so.8 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libnetcdf.so.7 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libjasper.so.1 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libopenjp2.so.7 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libxerces-c-3.1.so $DEPLOY_DIR/lib64/
#cp /usr/lib64/libodbcinst.so.2 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libodbc.so.2 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libwebp.so.4 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libfreexl.so.1 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libpoppler.so.46 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libarmadillo.so.4 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libgeos_c.so.1 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libproj.so.0 $DEPLOY_DIR/lib64/
#cp /usr/lib64/libgdal.so.1 $DEPLOY_DIR/lib64/


# package app and python libs
pip install app/.
#rsync -ax /usr/lib/python2.7/site-packages/ $DEPLOY_DIR/lib/python2.7/site-packages/ --exclude-from $DEPLOY_DIR/excluded_packages
#rsync -ax /usr/lib64/python2.7/site-packages/ $DEPLOY_DIR/lib64/python2.7/site-packages/ --exclude-from $DEPLOY_DIR/excluded_packages
rsync -ax /usr/lib/ $DEPLOY_DIR/lib/
rsync -ax /usr/lib64/ $DEPLOY_DIR/lib64/


# zip up contents
cd $DEPLOY_DIR
#zip -ruq deploy.zip ./ -x deploy.zip excluded_packages package.sh
