import os
import glob
import gippy
import gippy.algorithms as alg
import argparse
import json
import beachfront.mask as bfmask
import beachfront.process as bfproc
import beachfront.vectorize as bfvec
from version import __version__


def process(img1, img2, qimg=None, coastmask=False, save=False):
    """ Process data from indir to outdir """

    geoimg = img1.add_band(img2[0])
    if qimg is not None:
        fout = geoimg.basename() + '_cloudmask.tif' if save else ''
        maskimg = bfmask.create_mask_from_bitmask(qimg, filename=fout)
        geoimg.add_mask(maskimg[0] == 1)

    # calculate NWDI
    geoimg.set_bandnames(['green', 'nir'])
    fout = geoimg.basename() + '_ndwi.tif' if save else ''
    imgout = alg.indices(geoimg, ['ndwi'], filename=fout)

    # mask with coastline
    if coastmask:
        # open coastline vector
        fname = os.path.join(os.path.dirname(__file__), 'coastmask.shp')
        fout = geoimg.basename() + '_coastmask.tif' if save else ''
        imgout = bfmask.mask_with_vector(imgout, (fname, ''), filename=fout)

    # calculate optimal threshold
    threshold = bfproc.otsu_threshold(imgout[0])

    # save thresholded image
    if save:
        fout = geoimg.basename() + '_thresh.tif'
        imgout2 = gippy.GeoImage.create_from(imgout, filename=fout, dtype='byte')
        (imgout[0] > threshold).save(imgout2[0])

    # vectorize threshdolded (ie now binary) image
    coastline = bfvec.potrace(imgout[0] > threshold)

    # convert coordinates to GeoJSON
    geojson = bfvec.to_geojson(coastline, source=geoimg.basename())
    if save:
        fout = geoimg.basename() + '_coastline.geojson'
        with open(fout, 'w') as f:
            f.write(json.dumps(geojson))
    return geojson


def open_from_directory(dirin='', ext='.TIF'):
    """ Open collection of files from a directory """
    # inspect directory for imagery, mask, take band ratio
    fnames = glob.glob(os.path.join(dirin, '*%s' % ext))
    prefix = os.path.commonprefix(fnames)
    print(prefix)
    # geoimg = gippy.GeoImage(fnames[0:1], nodata=0)


def main():
    """ Parse command line arguments and call process() """
    desc = 'Beachfront Algorithm: NDWI (v%s)' % __version__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)

    parser.add_argument('--b1', help='Green (or Blue or Coastal Band)', required=True)
    parser.add_argument('--b2', help='NIR Band', required=True)
    parser.add_argument('--fout', help='Output filename for geojson', default='coastline.geojson')
    parser.add_argument('--outdir', help='Save intermediate files to this dir (otherwise temp)', default='')

    parser.add_argument('--qband', help='Quality band (used to mask clouds)')
    parser.add_argument('--coastmask', help='Mask non-coastline areas', default=False, action='store_true')
    parser.add_argument('--version', help='Print version and exit', action='version', version=__version__)

    args = parser.parse_args()

    band1 = gippy.GeoImage(args.b1)
    band2 = gippy.GeoImage(args.b2)
    qband = args.qband if args.qband is None else gippy.GeoImage(args.qband)

    geojson = process(band1, band2, qband=qband, coastmask=args.coastmask)

    # save output
    with open(args.fout, 'w') as f:
        f.write(json.dumps(geojson))


if __name__ == "__main__":
    main()
