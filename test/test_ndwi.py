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


class TestMain(unittest.TestCase):
    """ Test masking functions """

    # cirrus
    img1url = 'http://landsat-pds.s3.amazonaws.com/L8/008/028/LC80080282016215LGN00/LC80080282016215LGN00_B1.TIF'
    img2url = 'http://landsat-pds.s3.amazonaws.com/L8/008/028/LC80080282016215LGN00/LC80080282016215LGN00_B5.TIF'
    qimgurl = 'http://landsat-pds.s3.amazonaws.com/L8/008/028/LC80080282016215LGN00/LC80080282016215LGN00_BQA.TIF'

    testdir = os.path.dirname(__file__)

    save = False

    def setUp(self):
        """ Download all test images """
        self.img1 = download_image(self.img1url)
        self.img2 = download_image(self.img2url)
        self.qimg = download_image(self.qimgurl)

    def test_process(self):
        """ Extract coastline from two raster bands """
        geojson = alg.process(self.img1, self.img2, save=self.save)
        self.assertEqual(len(geojson['features']), 55)

    def test_process_with_cloudmask(self):
        """ Coastline extraction with cloud masking """
        geojson = alg.process(self.img1, self.img2, self.qimg, save=self.save)
        self.assertEqual(len(geojson['features']), 1650)

    def _test_process_with_coastmask(self):
        """ Coastline extraction with coast masking """
        geojson = alg.process(self.img1, self.img2, coastmask=True, save=self.save)
        print(len(geojson['features']))

    def _test_open_from_directory(self):
        """ Open files from directory """
        alg.open_from_directory(os.path.dirname(__file__))
