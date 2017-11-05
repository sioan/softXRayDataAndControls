#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/ipython -i
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
import IPython
from binnifySmallData import basicHistogram
from binnifySmallData import hdf5_to_dict

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

def removeNans(myDict):
	notNanMask = True
	for i in myDict:		
		notNanMask *= array([not math.isnan(j) for j in myDict[i]])
	
	for i in myDict:		
		myDict[i] = myDict[i][notNanMask]

	return myDict

def ftBinning(myDict,keyToAverage,keyToBin,isLog):
	tPi = 2 * 3.14159
	
	myList = array([myDict[keyToBin],myDict[keyToAverage]]).transpose()

	fStep = 1.0/(max(myDict[keyToBin]) - min(myDict[keyToBin]))
		
	#fAxis = arange(0,1000*fStep,fStep)

	fAxis = exp(arange(-log(1000*fStep),log(1000*fStep),log(1000*fStep)/1000.0))
	
	myFtValue = []
	myFtArtifact = []
	myCounter = 0

	#explicit projection onto sin and cos
	for f in fAxis:
		myCounter += 1
		if(myCounter%100==1):
			print(str(myCounter)+", ")
		myCovCos = cov(myDict[keyToAverage],cos(tPi*f*myDict[keyToBin]))
		myCovSin = cov(myDict[keyToAverage],sin(tPi*f*myDict[keyToBin]))
	
		myProjection = myCovCos[0,1]/(myCovCos[1,1]+1e-12)+1j*myCovSin[0,1]/(myCovSin[1,1]+1e-12)

		myCovCosArtifact = mean(cos(tPi*f*myDict[keyToBin]))
		myCovSinArtifact = mean(sin(tPi*f*myDict[keyToBin]))
		myArtifactProjection = myCovCosArtifact+1j*myCovSinArtifact

		
		myFtValue.append(myProjection)
		myFtArtifact.append(myArtifactProjection)		

	myFtValue = array(myFtValue)
	myFtArtifact = array(myFtArtifact)

	return fAxis,myFtValue, myFtArtifact
		
#plot(myData[0],(abs(array(myData[1]))),'.')




if __name__ == '__main__':
	


	currentWorkingDirectory = os.getcwd()

	h5FileName = sys.argv[1]
	experimentRunName = h5FileName.split("/")[1][:-3]

	f = h5py.File(currentWorkingDirectory+"/"+h5FileName,'r')
	myDict= hdf5_to_dict(f)
	f.close()

	keyToNormalize = 'acqiris2'
	keyToNormalizeBy = 'GMD'
	keyToAverage = 'normalizedAcqiris'
	timeToolSign = 1
	
	keyToBin = 'delayStage'
	correctedKeyToBin = 'estimatedTime'
	timeToolKeys = ['TSS_OPAL','pixelTime']

	myMask =  filterMasks.__dict__[experimentRunName](myDict)

	myDict[keyToAverage] = myDict[keyToNormalize]/(1e-11+myDict[keyToNormalizeBy])

	#IPython.embed()

	#time tool direction. need to abstract into config file. also, milimeter to picosecond correction
	myOffset = min(myDict[keyToBin])
	myDict[correctedKeyToBin] = (2/.3*(myDict[keyToBin]-myOffset)+timeToolSign*myDict['TSS_OPAL']['pixelTime']/1000.0)	

	#removing pre laser shot. correct for run 79.  should abstract into config for all data sets. (< 12.4 for runs 63 and 60)
	laserMask = myDict[correctedKeyToBin] > 9.65
	myMask *= laserMask 

	#adding sanity check reference oscillation
	#myDict[keyToAverage] += 25*sin(2*3.14159*5.9*myDict[correctedKeyToBin])/1.0

	#apply mask	
	myDict[keyToAverage] = myDict[keyToAverage][myMask]
	myDict[correctedKeyToBin] = myDict[correctedKeyToBin][myMask]

	myDataDictionary = basicHistogram(myDict,keyToAverage,correctedKeyToBin,bins=arange(-3.5,24,.1),isLog=True)#fast for debugging
	#IPython.embed()


	#subtract off linear trend and offset	
	myDict[keyToAverage]-=mean(myDict[keyToAverage])	
	myCovLinear = cov(myDict[keyToAverage],myDict[correctedKeyToBin])
	myDict[keyToAverage] -= myCovLinear[1,0]*1.0/myCovLinear[1,1]*(myDict[correctedKeyToBin] - mean(myDict[correctedKeyToBin]))

	
	myData = ftBinning(myDict,keyToAverage,correctedKeyToBin,isLog=True)#fast for debugging

	#pickle.dump(myDataDictionary, open(currentWorkingDirectory+"/binnedData/"+experimentRunName+".pkl", "wb"))
	#temp = pickle.load(open(experimentRunName+".pkl","rb"))




