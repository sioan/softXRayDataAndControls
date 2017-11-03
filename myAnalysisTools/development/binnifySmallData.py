#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
from pylab import *
from scipy.interpolate import interp1d
import h5py
import argparse
from scipy.optimize import curve_fit
import pickle
import os
import math
sys.path.append(os.curdir)
from filterMasks import filterMasks
from config.bin_configuration import bin_configuration

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

def hdf5_to_dict(myhdf5Object):
	replacementDictionary = {}
	myList = []
	myhdf5Object.visit(myList.append)
	for i in myList:
		try:
			replacementDictionary[i] = array(myhdf5Object[i])
		except:
			pass
		

	return replacementDictionary

#to do list
#1) separate out mask section into directory and files. 
#2) add arg parser to go over battery of analysis and specified files. need to use the @ trick to get the interactive to work
#3) rolling statistics takes too long. how to speed up?

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

makeGraphableData(unBinnedDataDictionary,instructionObject):
	#instructionObject has the mode. raw binning, correlation, saturated correction correlation

	#instantiation
	unBinnedDataDictionary[''] = 

	
	graphableDataObject['x'] = xDataBinned
	graphableDataObject['y'] = yDataBinned
	graphableDataObject['yStandDev'] = yStandDev

	return graphableDataObject

def main(h5FileName):
	
	myBinCfg = bin_configuration()

	currentWorkingDirectory = os.getcwd()

	#h5FileName = sys.argv[1]
	experimentRunName = h5FileName.split("/")[1][:-3]

	f = h5py.File(currentWorkingDirectory+"/"+h5FileName,'r')
	myDict= hdf5_to_dict(f)
	f.close()

	#goal is to generate an h5 file for plotting
	#how to analyze?
		#1 brute division normalization and filtering
		#2 slope fitting. (to get scattering factor, reflectivitiy, fluorescence, etc...)
		#3 detector non-linearity corrected slope fitting
		#4 ridiculous, but fit raw data to decaying sinusoid.

	graphableData = makeGraphableData()

	yAxis = 'acqiris2'
	yAxisBy = 'GMD'
	keyToAverage = 'normalizedAcqiris'
	timeToolSign = 1
	
	xAxis = myBinCfg.xAxis
	correctedxAxis = 'estimatedTime'
	timeToolKeys = ['TSS_OPAL','pixelTime']

	myMask =  filterMasks.__dict__[experimentRunName](myDict)

	myDict[keyToAverage] = myDict[yAxis]/(1e-11+myDict[yAxisBy])

	#time tool direction. need to abstract into config file. also, milimeter to picosecond correction
	myOffset = min(myDict[xAxis])
	myDict[correctedxAxis] = 2/.3*(myDict[xAxis]-myOffset)+timeToolSign*myDict['TSS_OPAL']['pixelTime']/1000.0
	#myDict[correctedxAxis] = 2/.3*(myDict[xAxis]-49)+timeToolSign*myDict['TSS_OPAL']['pixelTime']/1000.0	

	#removing pre laser shot need to abstract into config file
	#laserMask = myDict[correctedxAxis] < 12.4
	#myMask *= laserMask 

	myDict[keyToAverage] = myDict[keyToAverage][myMask]
	myDict[correctedxAxis] = myDict[correctedxAxis][myMask]

	myDataDictionary = basicHistogram(myDict,keyToAverage,correctedxAxis,bins=arange(0.5,21,.1),isLog=True)#fast for debugging

	fileToExport = currentWorkingDirectory+"/binnedData/"+experimentRunName
	pickle.dump(myDataDictionary, open(fileToExport+".pkl", "wb"))
	
	exportData = h5py.File(fileToExport+'.h5', 'w')	
	for i in myDataDictionary:
		exportData.create_dataset(i, data=myDataDictionary[i], chunks=True, maxshape=(None,))

	#temp = pickle.load(open(experimentRunName+".pkl","rb"))

if __name__ == '__main__':
	myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
		
	myParser.add_argument('-f','--file', help='input file to bin')

	myArguments = myParser.parse_args()

	main(myArguments.file)
