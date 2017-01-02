import os
import tempfile
import sys
import argparse
import json
import logging
from traceback import format_exc

import gippy
import gippy.algorithms as alg
import beachfront.mask as bfmask
import beachfront.process as bfproc
import beachfront.vectorize as bfvec
from bfalg_ndwi.version import __version__

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def parse_args(args):
    """ Parse arguments for the NDWI algorithm """
    desc = 'Beachfront Algorithm: NDWI (v%s)' % __version__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)

    parser.add_argument('-i', '--input', help='Input image (1 or 2 files)', required=True, action='append')
    parser.add_argument('-b', '--bands', help='Band numbers for Green and NIR bands', default=[1, 1], nargs=2)

    parser.add_argument('--outdir', help='Save intermediate files to this dir (otherwise temp)', default='')
    parser.add_argument('--fout', help='Output filename for geojson', default='coastline.geojson')

    parser.add_argument('--l8bqa', help='Landat 8 Quality band (used to mask clouds)')
    parser.add_argument('--coastmask', help='Mask non-coastline areas', default=False, action='store_true')
    parser.add_argument('--version', help='Print version and exit', action='version', version=__version__)

    return parser.parse_args(args)


def open_image(filenames, bands, mask=None):
    """ Take in 1 or two filenames and two band numbers to create single 2-band (green, nir) image """
    try:
        if len(filenames) == 2:
            band1 = gippy.GeoImage(filenames[0]).select([bands[0]])
            band2 = gippy.GeoImage(filenames[1]).select([bands[1]])
            geoimg = band1.add_band(band2[0])
        else:
            geoimg = gippy.GeoImage(filenames[0]).select(bands)
        geoimg.set_bandnames(['green', 'nir'])
        if mask is not None:
            geoimg[0].add_mask(mask == 1)
        return geoimg
    except Exception, e:
        logger.error('bfalg_ndwi error opening input: %s' % str(e))
        from traceback import format_exc
        logger.error(format_exc())


def process(geoimg, coastmask=False, outdir='', fout=''):
    """ Process data from indir to outdir """
    bname = geoimg.basename()
    if outdir is None:
        outdir = tempfile.mkdtemp()
    prefix = os.path.join(outdir, bname)

    # calculate NWDI
    imgout = alg.indices(geoimg, ['ndwi'], filename=prefix + '_ndwi.tif')

    # mask with coastline
    if coastmask:
        # open coastline vector
        fname = os.path.join(os.path.dirname(__file__), 'coastmask.shp')
        fout = prefix + '_coastmask.tif'
        imgout = bfmask.mask_with_vector(imgout, (fname, ''), filename=fout)

    # calculate optimal threshold
    threshold = bfproc.otsu_threshold(imgout[0])

    # debug - save thresholded image
    # imgout2 = gippy.GeoImage.create_from(imgout, filename=prefix + '_thresh.tif', dtype='byte')
    # (imgout[0] > threshold).save(imgout2[0])

    # vectorize threshdolded (ie now binary) image
    coastline = bfvec.potrace(imgout[0] > threshold)

    # convert coordinates to GeoJSON
    geojson = bfvec.to_geojson(coastline, source=geoimg.basename())

    # write geojson output file
    if fout == '':
        fout = prefix + '_coastline.geojson'
    elif not os.path.isabs(fout):
        fout = os.path.join(outdir, fout)
    with open(fout, 'w') as f:
        f.write(json.dumps(geojson))

    return geojson


def main():
    """ Parse command line arguments and call process() """
    args = parse_args(sys.argv[1:])

    # landsat cloudmask
    if args.l8bqa is not None:
        try:
            maskimg = bfmask.create_mask_from_bitmask(gippy.GeoImage(args.l8bqa))
        except Exception, e:
            logger.error('bfalg_ndwi error creating cloudmask: %s' % str(e))
            logger.error(format_exc())

    geoimg = open_image(args.filenames, args.bands, mask=maskimg[0])

    try:
        process(geoimg, coastmask=args.coastmask, outdir=args.outdir)
        logger.info('bfalg_ndwi complete: %s' % os.path.abspath(args.fout))
    except Exception, e:
        logger.error('bfalg_ndwi error: %s' % str(e))
        logger.error(format_exc())


if __name__ == "__main__":
    main()
