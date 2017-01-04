# bf-alg-ndwi

bf-alg-ndwi is a library and a CLI for running shoreline detection on a directory of input data using an NDWI algorithm. The algorithm performs several steps including masking (if Landsat and BQA mask is provided), band ratioing, thresholding, and vectorizing to create a GeoJSON output of the in-scene coastline.

### Creating a Deploy Package

Docker can be used to create a deploy package.  First the docker image must be built, and then the package command can be called. 

  $ docker-compose build
  $ docker-compose run package

  $ optionally test package on basic Linux image
  $ docker-compose run testpackage

All necessary files will be put into the deploy directory, which will then be packaged up into a deploy.zip file. Copy to the target machine and unzip.

	$ unzip deploy.zip

There are two environment variables that need to be set prior to calling the CLI.

	$ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PWD/lib
	$ export PYTHONPATH=$PYTHONPATH:$PWD/lib/python2.7/dist-packages
  $ export GDAL_DATA=$PWD/share/gdal


### NDWI

In the examples and the online help the band names 'green' and 'nir' are used for the bands. However, the bands need not strictly be green and nir, these are just the most common bands used to calculate NDWI.  NDWI is calculated per pixel as the difference between the two bands divided by the sum of the two bands:

```
NDWI = (green-nir) / (green+nir)
```


### Usage

Call the bfalg-ndwi CLI:

```
$ python bfalg_ndwi.py -h
usage: ndwi.py [-h] -i INPUT [-b BANDS BANDS] [--outdir OUTDIR] [--fout FOUT]
               [--l8bqa L8BQA] [--coastmask] [--version]

Beachfront Algorithm: NDWI (v0.1.1)

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input image (1 or 2 files) (default: None)
  -b BANDS BANDS, --bands BANDS BANDS
                        Band numbers for Green and NIR bands (default: [1, 1])
  --outdir OUTDIR       Save intermediate files to this dir (otherwise temp)
                        (default: )
  --fout FOUT           Output filename for geojson (default:
                        coastline.geojson)
  --l8bqa L8BQA         Landat 8 Quality band (used to mask clouds) (default:
                        None)
  --coastmask           Mask non-coastline areas (default: False)
  --version             Print version and exit
```

The INPUT parameter can either take 1 filename, or two by providing INPUT twice.  If two filenames are passed, and BANDS is not provided, then it will use the first band from each of those files for the 'green' and 'nir' bands. If BANDS is provided then it will use those bands instead.  This example uses the second band from the test1.tif as the green band, the first band from test2.tif as the nir band.

  $ python bfalg-ndwi -i test1.tif -i test2.tif -b 2 1

If a single filename is provided, then BANDS needs to be provided to specify which bands in the file should be used, otherwise it defaults to '1, 1', which means it would use the same band for both green and nir. This example uses the 1st band in the file as the green band and the 5th as the nir.

  $ python bfalg-ndwi -i test1.tif -b 1 5


### Branches
The 'develop' branch is the default branch and contains the latest accepted changes to the code base. Changes should be created in a branch and Pull Requests issues to the 'develop' branch. Releases (anything with a version number) should issue a PR to 'master', then tagged with the proper version using `git tag`. Thus, the 'master' branch will always contain the latest tagged release.

### Testing
Python nose is used for testing, and any new function added to the main library should have at least one corresponding test in the appropriate module test file in the tests/ directory.

### Docker
A Dockerfile and a docker-compose.yml are included for ease of development. The built docker image provides all the system dependencies needed to run the library. The library can also be tested locally, but all system dependencies must be installed first, and the use of a virtualenv is recommended.

To build the docker image use the included docker-compose tasks:

    $ docker-compose build

Which will build an image called that can be run

    # this will run the image in interactive mode (open bash script)
    $ docker-compose run bash

    # this willl run the tests using the locally available image
    $ docker-compose run test

Additionally, if a package had previously been created (see above), the testpackage command can be used to test it on a base Linux image. Note this is different then the test which uses a system (the image built to create the package) where dependencies have been conventionally installed.
