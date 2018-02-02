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
import unittest
import os
import requests
import gippy
import bfalg_ndwi.ndwi as alg


def download_image(url):
    """ Download a test image """
    fout = os.path.join(os.path.dirname(__file__), os.path.basename(url))
    if not os.path.exists(fout):
        print('Downloading image %s' % fout)
        stream = requests.get(url, stream=True)
        try:
            with open(fout, 'wb') as f:
                for chunk in stream.iter_content(1024):
                    f.write(chunk)
        except:
            raise Exception("Problem downloading %s" % url)
    return fout


class TestNDWI(unittest.TestCase):
    """ Test masking functions """

    images = {
        'landsat': {
            'img1': 'http://landsat-pds.s3.amazonaws.com/L8/008/028/LC80080282016215LGN00/LC80080282016215LGN00_B1.TIF',
            'img2': 'http://landsat-pds.s3.amazonaws.com/L8/008/028/LC80080282016215LGN00/LC80080282016215LGN00_B5.TIF',
            'qimg': 'http://landsat-pds.s3.amazonaws.com/L8/008/028/LC80080282016215LGN00/LC80080282016215LGN00_BQA.TIF',
            'nfeat': 725,
            'nfeat_coast': 589
        },
        'sentinel': {
            'img1': 'https://sentinel-s2-l1c.s3.amazonaws.com/tiles/10/S/FE/2017/4/20/0/B03.jp2',
            'img2': 'https://sentinel-s2-l1c.s3.amazonaws.com/tiles/10/S/FE/2017/4/20/0/B08.jp2',
            'nfeat': 63,
            'nfeat_coast': 65
        }
    }

    testdir = os.path.dirname(__file__)

    @classmethod
    def setUpClass(cls):
        """ Download all test images """
        for source, imgs in cls.images.iteritems():
            for name, url in imgs.iteritems():
                if isinstance(url, str):
                    cls.images[source][name] = download_image(url)
        print cls.images
        # for debugging
        # gippy.Options.set_verbose(5)

    def open_image(self, source='landsat'):
        """ Open test image """
        filenames = [self.images[source]['img1'], self.images[source]['img2']]
        geoimg = alg.open_image(filenames, [1, 1])
        return geoimg

    def test_parse_args(self):
        """ Parse arguments """
        args = alg.parse_args('-i test1.tif -i test2.tif'.split(' '))
        self.assertEqual(len(args.input), 2)
        args = alg.parse_args('-i test.tif -b 1 5'.split(' '))
        self.assertEqual(args.bands[1], 5)
        args = alg.parse_args('-i test1.tif --close 0'.split(' '))
        self.assertEqual(args.close, 0)

    def test_open_image(self):
        """ Open 1 or 2 files to get two specific bands """
        for src in self.images:
            geoimg = self.open_image(source=src)
            self.assertEqual(geoimg.nbands(), 2)

    def test_process(self):
        """ Coastline extraction from two raster bands """
        for src in self.images:
            geoimg = self.open_image(source=src)
            # fout = os.path.join(self.testdir, 'process.geojson')
            geojson = alg.process(geoimg, bname='test_%s' % src, outdir=self.testdir)
            self.assertEqual(len(geojson['features']), self.images[src]['nfeat'])

    def test_main_with_cloudmask(self):
        """ Coastline extraction with cloud masking """
        # fout = os.path.join(self.testdir, 'process_cloud.geojson')
        fnames = self.images['landsat']
        geojson = alg.main([fnames['img1'], fnames['img2']], l8bqa=fnames['qimg'],
                           outdir=self.testdir, close=0, bname='test_landsat_cloud')
        self.assertEqual(len(geojson['features']), 1136)

    def test_main_with_coastmask(self):
        """ Coastline extraction with coast masking """
        # fout = os.path.join(self.testdir, 'process_coast.geojson')
        for src in self.images:
            fnames = [self.images[src]['img1'], self.images[src]['img2']]
            geojson = alg.main(fnames, coastmask=True,
                               outdir=self.testdir, bname='test_%s_coastmask' % src)
            self.assertEqual(len(geojson['features']), self.images[src]['nfeat_coast'])
