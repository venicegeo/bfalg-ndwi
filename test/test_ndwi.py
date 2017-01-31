import unittest
import os
import requests
from gippy import GeoImage
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
    return GeoImage(fout)


class TestNDWI(unittest.TestCase):
    """ Test masking functions """

    # cirrus
    img1url = 'http://landsat-pds.s3.amazonaws.com/L8/008/028/LC80080282016215LGN00/LC80080282016215LGN00_B1.TIF'
    img2url = 'http://landsat-pds.s3.amazonaws.com/L8/008/028/LC80080282016215LGN00/LC80080282016215LGN00_B5.TIF'
    qimgurl = 'http://landsat-pds.s3.amazonaws.com/L8/008/028/LC80080282016215LGN00/LC80080282016215LGN00_BQA.TIF'

    testdir = os.path.dirname(__file__)

    def setUp(self):
        """ Download all test images """
        self.img1 = download_image(self.img1url)
        self.img2 = download_image(self.img2url)
        self.qimg = download_image(self.qimgurl)

    def open_image(self):
        """ Open test image """
        filenames = [self.img1.filename(), self.img2.filename()]
        geoimg = alg.open_image(filenames, [1, 1])
        return geoimg

    def test_parse_args(self):
        """ Parse arguments """
        args = alg.parse_args('-i test1.tif -i test2.tif'.split(' '))
        self.assertEqual(len(args.input), 2)
        args = alg.parse_args('-i test.tif -b 1 5'.split(' '))
        self.assertEqual(args.bands[1], 5)

    def test_open_image(self):
        """ Open 1 or 2 files to get two specific bands """
        geoimg = self.open_image()
        self.assertEqual(geoimg.nbands(), 2)

    def test_process(self):
        """ Coastline extraction from two raster bands """
        geoimg = self.open_image()
        # fout = os.path.join(self.testdir, 'process.geojson')
        fout = ''
        geojson = alg.process(geoimg, fout=fout)
        self.assertEqual(len(geojson['features']), 100)

    def test_main_with_cloudmask(self):
        """ Coastline extraction with cloud masking """
        # fout = os.path.join(self.testdir, 'process_cloud.geojson')
        fout = ''
        geojson = alg.main([self.img1.filename(), self.img2.filename()], l8bqa=self.qimg.filename(), outdir=self.testdir,  fout=fout)
        self.assertEqual(len(geojson['features']), 454)

    def test_main_with_coastmask(self):
        """ Coastline extraction with coast masking """
        # fout = os.path.join(self.testdir, 'process_coast.geojson')
        fout = ''
        geojson = alg.main([self.img1.filename(), self.img2.filename()], coastmask=True, fout=fout)
        self.assertEqual(len(geojson['features']), 95)
