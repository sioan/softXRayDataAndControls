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
