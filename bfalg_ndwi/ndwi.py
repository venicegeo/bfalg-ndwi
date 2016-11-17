import os
import gippy
import gippy.algorithms as alg
import argparse
import json
import beachfront.mask as bfmask
import beachfront.process as bfproc
import beachfront.vectorize as bfvec


def process(img1, img2, qimg=None, coastmask=False):
    """ Process data from indir to outdir """

    geoimg = img1.add_band(img2[0])
    if qimg is not None:
        maskimg = bfmask.create_mask_from_bitmask(qimg)
        geoimg[0].add_mask(maskimg[0])

    # calculate NWDI
    geoimg.set_bandnames(['green', 'nir'])
    imgout = alg.indices(geoimg, ['ndwi'])

    # mask with coastline
    if coastmask:
        # open coastline vector
        fname = os.path.join(os.path.dirname(__file__), 'coastmask.shp')
        imgout = bfmask.mask_with_vector(imgout, (fname, ''))

    # calculate optimal threshold
    threshold = bfproc.otsu_threshold(imgout[0])

    # vectorize threshdolded (ie now binary) image
    coastline = bfvec.potrace(imgout[0] > threshold)

    # convert coordinates to GeoJSON
    return bfvec.to_geojson(coastline, source=geoimg.basename())


def open_from_directory(dirname=''):
    """ Open collection of files from a directory """
    # inspect directory for imagery, mask, take band ratio
    #fnames = glob.glob(os.path.join(indir, '*'))
    #geoimg = gippy.GeoImage(fnames[0:1], nodata=0)
    pass


def main():
    """ Parse command line arguments and call process() """
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description='Beachfront Algorithm: NDWI', formatter_class=dhf)

    parser.add_argument('--green', help='Green (or Blue or Coastal Band', required=True)
    parser.add_argument('--nir', help='NIR Band', required=True)
    parser.add_argument('--fout', help='Output filename for geojson', default='coastline.geojson')
    parser.add_argument('--outdir', help='Save intermediate files to this dir (otherwise temp)', default='')

    parser.add_argument('--qband', help='Quality band (used to mask clouds)')
    parser.add_argument('--coastmask', help='Mask non-coastline areas', default=False, action='store_true')

    args = parser.parse_args()

    band1 = gippy.GeoImage(args.green)
    band2 = gippy.GeoImage(args.nir)
    qband = args.qband if args.qband is None else gippy.GeoImage(args.qband)

    geojson = process(band1, band2, qband=qband, coastmask=args.coastmask)

    # save output
    with open(args.fout, 'w') as f:
        f.write(json.dumps(geojson))


if __name__ == "__main__":
    main()
