# bf-alg-ndwi

`bf-alg-ndwi` is a library and _command line interface_ (CLI) for running shoreline detection on a directory of input data using a _normalized difference water index_ (NDWI) algorithm. The algorithm performs several steps including masking (if Landsat 8 Pre-Collection Quality Assessment (BQA) mask is provided), NDWI calculation, thresholding, and vectorizing to create a GeoJSON output of the in-scene coastline.

## Installation

There are several system libraries that are prerequisites to installation. On a debian system:

```bash
$ apt-get install -y python-setuptools python-numpy python-dev libgdal-dev python-gdal swig git g++ libagg-dev libpotrace-dev
```

GDAL version 2.1.0 or higher is required, as is Potrace v1.14.

Also included is a Dockerfile that contains the necessary environment (see below for more).

Then, from this directory (containing this repo) install the Python requirements and `bfalg-ndwi`. The use of a virtual environment is recommended.

```bash
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ pip install .
```

## Usage

While `bfalg-ndwi` can be used as a Python library, the more common use is to use the _command line interface_ (CLI). Use the help switch (`-h` or `--help`) to display online help:

```bash
$ python bfalg_ndwi.py -h
usage: bfalg-ndwi [-h] -i INPUT [-b BANDS BANDS] [--outdir OUTDIR]
                  [--basename BASENAME] [--nodata NODATA] [--l8bqa L8BQA]
                  [--coastmask] [--minsize MINSIZE] [--close CLOSE]
                  [--simple SIMPLE] [--smooth SMOOTH] [--chunksize CHUNKSIZE]
                  [--verbose VERBOSE] [--version]

Beachfront Algorithm: NDWI (v1.1.4)

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input image (1 or 2 files) (default: None)
  -b BANDS BANDS, --bands BANDS BANDS
                        Band numbers for Green and NIR bands (default: [1, 1])
  --outdir OUTDIR       Save intermediate files to this dir (otherwise temp)
                        (default: )
  --basename BASENAME   Basename to give to output files (no extension,
                        defaults to first input filename (default: None)
  --nodata NODATA       Nodata value in input image(s) (default: 0)
  --l8bqa L8BQA         Landat 8 Quality band (used to mask clouds) (default:
                        None)
  --coastmask           Mask non-coastline areas (default: False)
  --minsize MINSIZE     Minimum coastline size (default: 100.0)
  --close CLOSE         Close line strings within given pixels (default: 5)
  --simple SIMPLE       Simplify using tolerance in map units (default: None)
  --smooth SMOOTH       Smoothing from 0 (none) to 1.33 (no corners (default:
                        0.0)
  --chunksize CHUNKSIZE
                        Chunk size (MB) to use when processing (default:
                        128.0)
  --verbose VERBOSE     0: Quiet, 1: Debug, 2: Info, 3: Warn, 4: Error, 5:
                        Critical (default: 2)
  --version             Print version and exit
```

If a single filename is provided via the INPUT argument, then `BANDS` needs to be provided to specify which bands in the file should be used, otherwise it defaults to `1, 1`, which means it would use the same band for both green and _near infrared_ (NIR). This example uses the 1st band in the file as the green band and the 5th as the NIR.

```bash
$ bfalg-ndwi -i test1.tif -b 1 5
```

If the `INPUT` parameter is provided twice for two filenames, then `BANDS` is the band number for the first file (green) and the second file (NIR). This example uses the second band from the test1.tif as the green band, the first band from test2.tif as the NIR band.

```bash
$ bfalg-ndwi -i test1.tif -i test2.tif -b 2 1
```

### Arguments

Input files are all that are absolutely required, but a more typical scenario would look like this:

```bash
$ bfalg-ndwi -i scene123.tif -b 1 2 --basename testrun --outdir scene123-output --coastmask
```

This will apply the included buffered coastline (`bfalg_ndwi/coastmask.shp`) to the image to mask out non-coastal regions. It will store all output files with the name `testrun` (+ additional tag and extension, e.g. `testrun.geojson`, `testrun_otsu.TIF`) in the directory `scene123-output`.

For Landsat 8, if the BQA band is available it can be provided, which will mask out the clouds from the scene.

```bash
$ bfalg-ndwi -i LC80080282016215LGN00_B1.TIF LC80080282016215LGN00_B5.TIF --l8bqa LC80080282016215LGN00_BQA.TIF --basename LC80080282016215LGN00 --outdir LC80080282016215LGN00_test --coastmask
```

The last three remaining parameters are tuning parameters involving the creation of the vector output.

- `minsize` (100): The minimum size a linestring should be before being filtered out. This corresponds to the potrace parameter `turdsize`, and is not the length of the line but rather some measure of the extent of it. The default of 10 will not filter out many lines. For Landsat, a value of 100 works well and removing false coasts, but may also remove islands or smaller incomplete shorelines.
- `close` (5): Linestrings will be closed if their two endpoints are within this number of pixels. The default is 5, and setting it to 0 will turn it off. This should not be set to a value much higher than 10.
- `simplify` (None): Simplification will not be done by default. If provided, it is in units of degrees, and is used to simplify and smooth the output. Simplification is heavily application and source imagery dependent, and is a lossy process. Consider starting points for RapidEye and PlanetScope data to be 0.00035, and for Landsat 8, 0.0007.

## NDWI Band Combinations

The traditional NDWI algorithm uses the green and NIR bands to calculate a normalized difference index:

```
NDWI = (green-NIR) / (green+NIR)
```

The band names, green and NIR, is what is referenced in the online help. However, other bands can work as well, or even better on some instruments. The Green band is a band that has a high water reflectance, while the NIR band is a band that has a very low water reflectance. The following bands are recommended.

| Sensor        | 'Green' band  | 'NIR' band  |
|---------------|---------------|-------------|
| Landsat 8     | 1 (Coastal)   | 5 (NIR)     |
| RapidEye      | 2 (Green)     | 4 (NIR)     |
| PlanetScope   | 2 (Green)     | 4 (NIR)     |
| Sentinel-2    | 3 (Green)     | 8 (NIR)     |

## Development

### Branches

The `develop` branch is the default branch and contains the latest accepted changes to the code base. Changes should be created in a branch and Pull Requests issues to the `develop` branch. Releases (anything with a version number) should issue a PR to `master`, then tagged with the proper version using `git tag`. Thus, the `master` branch will always contain the latest tagged release.

### Testing

Python nose is used for testing, and any new function added to the main library should have at least one corresponding test in the appropriate module test file in the `tests/` directory.

### Docker

A Dockerfile and a docker-compose.yml are included for ease of development. The built docker image provides all the system dependencies needed to run the library.

To build the Docker image use the included docker-compose tasks:

```bash
$ docker-compose build
```

This will build an image called `venicegeo/bfalg-ndwi` that can be run in interactive mode (opens a bash shell):

```bash
$ docker-compose run base
```

To run the tests on the created Docker image:

```bash
$ docker-compose run test
```
