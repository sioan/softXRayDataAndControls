#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
from pylab import *
from scipy.interpolate import interp1d
import h5py
import argparse
from scipy.optimize import curve_fit
import pickle
import os
import math
import IPython
sys.path.append(os.curdir)
#from filterMasks import filterMasks
from lib.hdf5_to_dict import hdf5_to_dict
from lib.analysis_library import *

#--------------------------------------------------------------------------
# File and Version Information:
#  $Id: README 2017-08-06 18:54:12Z sioan@SLAC.STANFORD.EDU $
#
# Description:
#  README file for data analysis
#------------------------------------------------------------------------

#Package author: Sioan Zohar

#Brief description:
#==================
#takes an hdf5 files turns it into applies a mask, turns it into dictionary, and bins it according to a config file or parameters
#the idea is to iterate this same code on different data sets using one config file or to test out analysis approaches by evaluating one data set and
#many config files iterating over different config files.  Testing different analysis techniques (that are abstracted into different configurations of identical code)
#is important for understanding why somes analysis techniques gives the expected result and some give unexpceted results.

	
def main(argd):
	
	data_dict = load_h5_file(argd['data_file'])
	config_dict = load_h5_file(argd['confg_file'])
	#filter_dict = load_h5_file(config_dict['filter_file'])	#raw mask? instructions for generating mask?
	filter_mask =  filterMasks.__dict__[argd['data_file'][:-3]](data_dict)

	the_bins = config_dict['bin_range']

	filt_data_dict = apply_filter(data_dict,filter_mask)
	
	binned_data = basic_histogram(filt_data_dict,argd['dependent_variable'],argd['bin_axes'],bins=the_bins,isLog=True)

	cov_binned_data = array([covariance_by_bin(i,i+binSize) for i in myBins])

	fileToExport = currentWorkingDirectory+"/binnedData/"+experimentRunName
	#pickle.dump(myDataDictionary, open(fileToExport+".pkl", "wb"))
	#temp = pickle.load(open(experimentRunName+".pkl","rb"))
	IPython.embed()


if __name__ == '__main__':
	myParser = argparse.ArgumentParser(description='bin and analyze along binned values')
		
	myParser.add_argument('-f','--data_file',type=str, help='hdf5 input file to analyze',default='None')
	myParser.add_argument('-b','--bin_axes',nargs='+',type=str,help='axes along which to bin',default='None') #delay_stage,ebeam
	myParser.add_argument('-i','--independent_variable',nargs='+', type=str,help='same as axes along which to bin',default='None') #gmd
	myParser.add_argument('-d','--dependent_variable', nargs='+',type=str,help='axes with weight/response variables',default='None') #acqiris
	myParser.add_argument('-m','--model_type', type=str,help='division, polynomial regression, multivariate regression. can be custom from library',default='None')
	myParser.add_argument('-p','--regression_order', type=str,help='the largest order polynomial in the regression ',default='None')
	myParser.add_argument('-c','--config_file', type=str,help='input configuration file with preset parameters',default='None')
	myParser.add_argument('-l','--library', type=str,help='allows for customized analysis models',default='None')
	myParser.add_argument('-s','--saved_config_name', type=str,help='save the current configuration for quick loading',default='None')

	myArguments = myParser.parse_args()

	if (None is not myArguments.saved_config_name):
		f = h5py.File(myArguments.saved_config_name+".h5",'w')
		for i in myArguments.__dict__:
			f.create_dataset(i, data=array(myArguments.__dict__[i],dtype=str))
		f.close()


	#to read this use 
	#from pylab import *
	#import h5py
	#f = h5py.File("firstSavedConfig.h5")
	#for i in f:
		#print(array(f[i]))

	main(myArguments.__dict__)
