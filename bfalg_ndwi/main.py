import os
import gippy
import gippy.algorithms as alg
import argparse
import glob
import json
from beachfront.mask import mask_with_wfs
from beachfront.process import otsu_threshold
from beachfront.vectorize import vectorize


def process(indir, outdir):
    """ Process data from indir to outdir """
    # inspect directory for imagery, mask, take band ratio
    fnames = glob.glob(os.path.join(indir, '*')
    geoimg = gippy.GeoImage(fnames, nodata=0)
    # set bandnames
    # geoimg.set_bandnames()

    # calculate NDVI 
    imgout = alg.indices(geoimg, ['ndvi'])

    # mask with coastline
    imgout = mask.mask_with_wfs(imgout, wfsurl, layer)
   
    # calculate threshold and vectorize thersholded image
    threshold = threshold(imgout[0])
    coastline = beachfront.vectorize(imgout[0] > threshold)
    return coastline


def main():
    """ Parse command line arguments and call process() """
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description='Extract Coastline from image data', formatter_class=dhf)
    parser.add_argument('--indir', help='Input directory', default='data/input')
    parser.add_argument('--outdir', help='Output directory', default='data/output')
    parser.add_argument('--fout', help='Output filename for coast geojson', default='coastline.geojson')

    args = parser.parse_args()

    geojson = process(args.indir, args.outdir)
    with open(args.fout, 'w') as f:
        f.write(json.dump(geojson))


if __name__ == "__main__":
    main()
