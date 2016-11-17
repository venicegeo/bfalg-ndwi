import unittest
import os
import requests
import json
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

    def setUp(self):
        """ Download all test images """
        self.img1 = download_image(self.img1url)
        self.img2 = download_image(self.img2url)
        self.qimg = download_image(self.qimgurl)

    def test_process(self):
        """ Extract coastline from two raster bands """
        geojson = alg.process(self.img1, self.img2)
        print(geojson.keys())
        #with open(os.path.join(self.testdir, img1.basename() + '.geojson'), 'w') as f:
        #    f.write(json.dumps(geojson))

    def test_process_with_cloudmask(self):
        """ Coastline extraction with cloud masking """
        geojson = alg.process(self.img1, self.img2, self.qimg)
        print(geojson.keys())

    def test_process_with_coastmask(self):
        """ Coastline extraction with coast masking """
        geojson = alg.process(self.img1, self.img2, coastmask=True)
        print(geojson.keys())