#!/bin/bash

cd ..
nosetests -v -s --with-coverage --cover-inclusive --cover-package bfalg_ndwi --debug=bfalg_ndwi
cd test
rm *.jp2
rm *.tif
rm *.TIF
rm *.aux.xml
rm *.geojson
