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
from hdf5_to_dict import hdf5_to_dict
import csv

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

#In depth description
#====================



#to do list
#1) separate out mask section into directory and files. 
#2) add arg parser to go over battery of analysis and specified files. need to use the @ trick to get the interactive to work
#3) rolling statistics takes too long. how to speed up?

#y0 is normalization. parameters aren't correct yet.  this is an averaging stage.... just to bin without averaging is duplicating large volumes of data. how to make a binnable data ob
#def regressionBasedI0Normalization(myDict,xAxis,y,y0,normalizationFunction):

	

#	myBinnedData = [normalizationFunction(y[i],y0[i],normalizationFunction for i in )]
	

def removeNans(myDict):
	notNanMask = True
	for i in myDict:		
		notNanMask *= array([not math.isnan(j) for j in myDict[i]])
	
	for i in myDict:		
		myDict[i] = myDict[i][notNanMask]

	return myDict

def basicHistogram(myDict,keyToAverage,xAxis,bins,isLog):#fast for debugging

	myDataDictionary = {}

	if(isLog):
		myDataDictionary['x'] = bins[:-1]
		myDataDictionary['counts'] = histogram(myDict[xAxis],bins)[0]

		myDataDictionary['yMean'] = histogram(myDict[xAxis],bins,weights = log(myDict[keyToAverage]))[0]
		myDataDictionary['yMean']/= myDataDictionary['counts']
		
		myDataDictionary['y2ndMoment'] = histogram(myDict[xAxis],bins,weights = log(myDict[keyToAverage])**2)[0]
		myDataDictionary['y2ndMoment']/= myDataDictionary['counts']

		myDataDictionary['standardDeviation'] = (myDataDictionary['y2ndMoment']-myDataDictionary['yMean'])**0.5
		myDataDictionary['standardDeviation'] = exp(myDataDictionary['standardDeviation'])

		myDataDictionary['yMean'] = exp(myDataDictionary['yMean'])

		#myDataDictionary['yMean'] = exp(myDataDictionary['yMean'])
		#myDataDictionary['standardDeviation'] = exp(myDataDictionary['standardDeviation'])
	
	else:
		myDataDictionary['x'] = bins[:-1]
		myDataDictionary['counts'] = histogram(myDict[xAxis],bins)[0]

		myDataDictionary['yMean'] = histogram(myDict[xAxis],bins,weights = myDict[keyToAverage])[0]
		myDataDictionary['yMean']/= myDataDictionary['counts']
	
		myDataDictionary['y2ndMoment'] = histogram(myDict[xAxis],bins,weights = myDict[keyToAverage]**2)[0]
		myDataDictionary['y2ndMoment']/= myDataDictionary['counts']

		myDataDictionary['standardDeviation'] = (myDataDictionary['y2ndMoment']-myDataDictionary['yMean'])**0.5

	del myDataDictionary['y2ndMoment']

	myDataDictionary = removeNans(myDataDictionary)

	return myDataDictionary

def makeGraphableData(unBinnedDataDictionary,instructionObject):
	#instructionObject has the mode. raw binning, correlation, saturated correction correlation

	#instantiation
	unBinnedDataDictionary[''] = 0

	
	graphableDataObject['x'] = xDataBinned
	graphableDataObject['y'] = yDataBinned
	graphableDataObject['yStandDev'] = yStandDev

	return graphableDataObject

def load_h5_file(file_name):

	if ('None'!=file_name):
		f = h5py.File(os.getcwd()+"/"+arg_dict['confg_file'],'r')
		this_dict= hdf5_to_dict(f)
		f.close()

	return this_dict

def main(arg_dict):
	
	data_dict = load_h5_file(arg_dict['data_file'])
	config_dict = load_h5_file(arg_dict['confg_file'])
	filter_dict = load_h5_file(config_dict['filter_file'])	#raw mask? instructions for generating mask?
	
	

	yAxis = 'acqiris2'
	yAxisBy = 'GMD'
	keyToAverage = 'normalizedAcqiris'
	timeToolSign = 1
	
	xAxis = myBinCfg.xAxis
	correctedxAxis = 'estimatedTime'
	timeToolKeys = ['TSS_OPAL','pixelTime']

	myMask =  filterMasks.__dict__[experimentRunName](myDict)

	myDict[keyToAverage] = myDict[yAxis]/(1e-11+myDict[yAxisBy])	#the I vs I0 normalization. doesn't belong here

	#time tool direction. need to abstract into config file. also, milimeter to picosecond correction
	
	data_dict[correctedxAxis] = 2/.3*(data_dict[xAxis])+timeToolSign*myDict['TSS_OPAL']['pixelTime']/1000.0
	#myDict[correctedxAxis] = 2/.3*(myDict[xAxis]-49)+timeToolSign*myDict['TSS_OPAL']['pixelTime']/1000.0	

	#removing pre laser shot need to abstract into config file
	#laserMask = myDict[correctedxAxis] < 12.4
	#myMask *= laserMask 

	myDict[keyToAverage] = myDict[keyToAverage][myMask]
	myDict[correctedxAxis] = myDict[correctedxAxis][myMask]

	myDataDictionary = basicHistogram(myDict,keyToAverage,correctedxAxis,bins=arange(0.5,21,.1),isLog=True)#fast for debugging

	fileToExport = currentWorkingDirectory+"/binnedData/"+experimentRunName
	#pickle.dump(myDataDictionary, open(fileToExport+".pkl", "wb"))
	
	#while testing so not overwriting old data
	#exportData = h5py.File(fileToExport+'.h5', 'w')	
	#for i in myDataDictionary:
	#	exportData.create_dataset(i, data=myDataDictionary[i], chunks=True, maxshape=(None,))

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
