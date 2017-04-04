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
import tempfile
import sys
import argparse
import json
import logging

import gippy
import gippy.algorithms as alg
import beachfront.mask as bfmask
import beachfront.process as bfproc
import beachfront.vectorize as bfvec
from bfalg_ndwi.version import __version__

logger = logging.getLogger(__name__)

# defaults
defaults = {
    'minsize': 100.0,
    'close': 5,
    'coastmask': False,
    'simple': None,
}


def parse_args(args):
    """ Parse arguments for the NDWI algorithm """
    desc = 'Beachfront Algorithm: NDWI (v%s)' % __version__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)

    parser.add_argument('-i', '--input', help='Input image (1 or 2 files)', required=True, action='append')
    parser.add_argument('-b', '--bands', help='Band numbers for Green and NIR bands', default=[1, 1], nargs=2, type=int)

    parser.add_argument('--outdir', help='Save intermediate files to this dir (otherwise temp)', default='')
    h = 'Basename to give to output files (no extension, defaults to first input filename'
    parser.add_argument('--basename', help=h, default=None)

    parser.add_argument('--l8bqa', help='Landat 8 Quality band (used to mask clouds)')
    parser.add_argument('--coastmask', help='Mask non-coastline areas', default=defaults['coastmask'], action='store_true')
    parser.add_argument('--minsize', help='Minimum coastline size', default=defaults['minsize'], type=float)
    parser.add_argument('--close', help='Close line strings within given pixels', default=defaults['close'], type=int)
    parser.add_argument('--simple', help='Simplify using tolerance in map units', default=None, type=float)
    h = '0: Quiet, 1: Debug, 2: Info, 3: Warn, 4: Error, 5: Critical'
    parser.add_argument('--verbose', help=h, default=2, type=int)
    parser.add_argument('--version', help='Print version and exit', action='version', version=__version__)

    return parser.parse_args(args)


def open_image(filenames, bands):
    """ Take in 1 or two filenames and two band numbers to create single 2-band (green, nir) image """
    try:
        if len(filenames) == 2:
            logger.info('Opening %s' % filenames[0], action='Open file', actee=filenames[0], actor=__name__)
            logger.info('Opening %s' % filenames[1], action='Open file', actee=filenames[1], actor=__name__)
            logger.debug('Opening %s (band %s) and %s (band %s)' %
                         (filenames[0], bands[0], filenames[1], bands[1]))
            geoimg = gippy.GeoImage(filenames[0]).select([bands[0]])
            band2 = gippy.GeoImage(filenames[1]).select([bands[1]])
            geoimg.add_band(band2[0])
        else:
            logger.info('Opening %s' % filenames[0], action='Open file', actee=filenames[0], actor=__name__)
            logger.debug('Opening %s using bands %s and %s' % (filenames[0], bands[0], bands[1]))
            geoimg = gippy.GeoImage(filenames[0]).select(bands)
        geoimg.set_bandnames(['green', 'nir'])
        return geoimg
    except Exception, e:
        logger.error('bfalg_ndwi error opening input: %s' % str(e))
        raise SystemExit()


def process(geoimg, coastmask=defaults['coastmask'],
            minsize=defaults['minsize'], close=defaults['close'], simple=defaults['simple'], outdir='', bname=None):
    """ Process data from indir to outdir """
    if bname is None:
        bname = geoimg.basename()
    if outdir is None:
        outdir = tempfile.mkdtemp()
    prefix = os.path.join(outdir, bname)

    # calculate NWDI
    fout = prefix + '_ndwi.tif'
    logger.info('Saving NDWI to file %s' % fout, action='Save file', actee=fout, actor=__name__)
    imgout = alg.indices(geoimg, ['ndwi'], filename=fout)

    # mask with coastline
    if coastmask:
        # open coastline vector
        fname = os.path.join(os.path.dirname(__file__), 'coastmask.shp')
        fout_coast = prefix + '_coastmask.tif'
        imgout = bfmask.mask_with_vector(imgout, (fname, ''), filename=fout_coast)

    # calculate optimal threshold
    threshold = bfproc.otsu_threshold(imgout[0])
    logger.debug("Otsu's threshold = %s" % threshold)

    # debug - save thresholded image
    if logger.level <= logging.DEBUG:
        fout = prefix + '_thresh.tif'
        logger.debug('Saving thresholded image as %s' % fout)
        logger.info('Saving threshold image to file %s' % fout, action='Save file', actee=fout, actor=__name__)
        imgout2 = gippy.GeoImage.create_from(imgout, filename=fout, dtype='byte')
        (imgout[0] > threshold).save(imgout2[0])

    # vectorize threshdolded (ie now binary) image
    coastline = bfvec.potrace(imgout[0] > threshold, minsize=minsize, close=close)

    # convert coordinates to GeoJSON
    geojson = bfvec.to_geojson(coastline, source=geoimg.basename())

    # write geojson output file
    fout = prefix + '.geojson'
    logger.info('Saving GeoJSON to file %s' % fout, action='Save file', actee=fout, actor=__name__)
    with open(fout, 'w') as f:
        f.write(json.dumps(geojson))

    if simple is not None:
        fout = bfvec.simplify(fout, tolerance=simple)

    return geojson


def main(filenames, bands=[1, 1], l8bqa=None, coastmask=defaults['coastmask'], minsize=defaults['minsize'],
         close=defaults['close'], simple=defaults['simple'], outdir='', bname=None):
    """ Parse command line arguments and call process() """
    geoimg = open_image(filenames, bands)
    if geoimg is None:
        logger.critical('bfalg-ndwi error opening input file %s' % ','.join(filenames))
        raise SystemExit()

    if bname is None:
        bname = geoimg[0].basename()

    logger.info('bfalg-ndwi start: %s' % bname)

    # landsat cloudmask
    if l8bqa is not None:
        logger.debug('Applying landsat quality mask %s to remove clouds' % l8bqa)
        try:
            fout_cloud = os.path.join(outdir, '%s_cloudmask.tif' % bname)
            logger.info('Opening %s BQA file' % l8bqa, action='Open file', actee=l8bqa, actor=__name__)
            maskimg = bfmask.create_mask_from_bitmask(gippy.GeoImage(l8bqa), filename=fout_cloud)
            geoimg.add_mask(maskimg[0] == 1)
        except Exception, e:
            logger.critical('bfalg-ndwi error creating cloudmask: %s' % str(e))
            raise SystemExit()

    try:
        geojson = process(geoimg, coastmask=coastmask, minsize=minsize, close=close,
                       simple=simple, outdir=outdir, bname=bname)
        logger.info('bfalg-ndwi complete: %s' % bname)
        return geojson
    except Exception, e:
        logger.critical('bfalg-ndwi error: %s' % str(e))
        raise SystemExit()


def cli():
    args = parse_args(sys.argv[1:])
    logger.setLevel(args.verbose * 10)
    main(args.input, bands=args.bands, l8bqa=args.l8bqa, coastmask=args.coastmask, minsize=args.minsize,
         close=args.close, simple=args.simple, outdir=args.outdir, bname=args.basename)


if __name__ == "__main__":
    cli()
