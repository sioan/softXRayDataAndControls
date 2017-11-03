description of files found in this directory

analysisFunctions.py 
contains functions whose arguments are (1) the event and (2) a dictionary of detector objects and returns a dictionary containing results from custom user analysis.  In simple cases, this is as trivial as just returning the detector object "get" method operating on the event.  In more sophisticated analyses, the functions may return results from image or waveform processing.

analysis.cfg 
contains the daq, psana, and this wrappers alias, together with the name of a function that points to the definition in analysisFunction.py.

bin_configuration.py
instructions how to bin the data

filterMask.py
instructions how to filter the data before binning


