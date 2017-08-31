#!/usr/bin/env python
"""
bfalg-ndwi
https://github.com/venicegeo/bfalg-ndwi

Copyright 2016, RadiantBlue Technologies, Inc.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import os
from codecs import open
from setuptools import setup, find_packages
import imp

here = os.path.abspath(os.path.dirname(__file__))
__version__ = imp.load_source('bfalg_ndwi.version', 'bfalg_ndwi/version.py').__version__

install_requires = []
tests_require = ['nose==1.3.7', 'coverage==4.3.4']

setup(
    name='bfalg_ndwi',
    version=__version__,
    description='Library and CLI for performing coastline extraction using NDWI',
    author='Matthew Hanson (matthewhanson)',
    license='GPL',
    url='https://github.com/venicegeo/bf-alg-ndwi',
    classifiers=[
        'Framework :: Pytest',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points = {
        'console_scripts': ['bfalg-ndwi=bfalg_ndwi.ndwi:cli'],
    },
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
)
