# auto_xtc_hdf5_converter

#usage: psanaXtcDataExtractor.py [-h] [-e EXP] [-r RUN] [-c CONFIGFILE]
#                                [-hd5 HD5FILE] [-t] [-td TTDEVICE]
#                                [-tc TTCODE] [-s START] [-f FINAL]

#Abstracts data analysis into user functions

#optional arguments:
#  -h, --help            show this help message and exit
#  -e EXP, --exp EXP     the experiment name
#  -r RUN, --run RUN     the run number to use when running offline
#  -c CONFIGFILE, --configFile CONFIGFILE
#                        the config file to read from
#  -hd5 HD5FILE, --hd5File HD5FILE
#                        extension of the small data file to write to.
#                        typically a,b or c
#  -t, --testSample      only take a small set of data for testing
#  -td TTDEVICE, --ttDevice TTDEVICE
#                        device to use for getting time tool
#  -tc TTCODE, --ttCode TTCODE
#                        event code to identify by kick
#  -s START, --start START
#                        skips until starting event reached
#  -f FINAL, --final FINAL
#                        up to final event

