# auto_xtc_hdf5_converter

This package separates the science analysis from the psana overhead when converting xtc to hdf5 files.

## Quick Start

</pre>$ PATH ="$PATH:/reg/g/psdm/sw/hutch/sxd/auto_xtc_hdf5_converter" </pre>

navigate to a directory where you'd like to do the analysis.

</pre>$ analysisDetectorConfigGenerator.py -e xpptut15 -r 280 </pre>

this line of code generates a config directory with files analysis.cfg and analysisFunctions.py.


</pre>$ psanaXtcDataExtractor.py -e xpptut15 -r 280 -t </pre>

this line converts the xtc file to an hdf5 file called xpptut15run280.h5.

### More involved quick start

The example above only gets a small portion of the xtc data. to get more data, the analysis.cfg and analysisFunctions.py files in the config directory need to be edited. (instructions forth coming)

### Usage

usage: psanaXtcDataExtractor.py [-h] [-e EXP] [-r RUN] [-c CONFIGFILE]
                                [-hd5 HD5FILE] [-t] [-td TTDEVICE]
                                [-tc TTCODE] [-s START] [-f FINAL]

Abstracts data analysis into user functions

optional arguments:

  -h, --help            show this help message and exit

  -e EXP, --exp EXP     the experiment name

  -r RUN, --run RUN     the run number to use when running offline

  -c CONFIGFILE, --configFile CONFIGFILE
                        the config file to read from

  -hd5 HD5FILE, --hd5File HD5FILE
                        extension of the small data file to write to.
                        typically a,b or c

  -t, --testSample      only take a small set of data for testing

  -td TTDEVICE, --ttDevice TTDEVICE
                        device to use for getting time tool

  -tc TTCODE, --ttCode TTCODE
                        event code to identify by kick

  -s START, --start START
                        skips until starting event reached

  -f FINAL, --final FINAL
                        up to final event

