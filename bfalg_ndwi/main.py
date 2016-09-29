import argparse
from beachfront.process import threshold
from beachfront.vectorize import vectorize


def process(indir, outdir):
    """ Process data from indir to outdir """
    # inspect directory for imagery, mask, take band ratio
    imgth = threshold(img)
    coastline = beachfront.vectorize(imgth)
    return coastline


def main():
    """ Parse command line arguments and call process() """
    # argument parsing
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description='Extract Coastline from image data', formatter_class=dhf)
    parser.add_argument('--indir', help='Input directory', default='data/input')
    parser.add_argument('--outdir', help='Output directory', default='data/output')

    args = parser.parse_args()

    return process(args.indir, args.outdir)


if __name__ == "__main__":
    main()
