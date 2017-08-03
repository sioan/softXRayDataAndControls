#--------------------------------------------------------------------------
# File and Version Information:
#  $Id: README 2017-07-31 18:54:12Z sioan@SLAC.STANFORD.EDU $
#
# Description:
#  README file for package psanaXtcDataExtractor
#------------------------------------------------------------------------

Package author: Sioan Zohar
Brief description:
==================

Improves reusability of psana code between different user groups.

The typical user group comes with their own psana code.  The structure of this code is very similar between user groups.
A data source and set of detector objects are instantiated.   The detector objects and compression analysis are written to hd5 while iterating over the enumerated events.  The package provided here abstacts the abstract the analysis pipeline away from the data wrangling pipeline and into a config file and an analysisFunction libary.




Detailed Description
=====================
Since starting in 11/2016, I have written this same portion of code several dozen times.  This particular piece of code has been reduced to 67 lines of code.  Instead of detector objects and values being explicitly defined within the main analysis code, they are loaded from a configuration file into a dictionary.  The analysis done on the large data such as image and acqiris waveforms is stored in the analysisFunction.py file.  The desired function to be used on the large dataset is placed in the config file.

example execution

 run psanaXtcDataExtractor.py -e sxri0414 -r 79 -c test -hd5 test


to do 
====================

1) (finished 7/31/2017.) add in summarizing data capability. may not work with dict since it's initialized to zero
2) time tool background (for the opal images on the by kick)
3) (finished) fix peak finder to actually find peaks.  currently just looking at amplitude at a given spot.  small time jitter will introduce noise.  actually get the max.
4) (finished added some syntax to check working directory )make xtc extractor use the correct path. Initial package structure for importing analysisFunctions.py for local working directory and not python path using __init__.py

5) small data doesn't work with data source. Slow Andor breaks MPI data source.  This will need to be solved for this and upcoming Andor experiments.

6) have the config file generator create this __init__.py and conig file system.
