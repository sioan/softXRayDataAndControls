#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python -i
from pylab import *
from scipy.interpolate import interp1d
import h5py
import argparse
from scipy.optimize import curve_fit
import pickle
import os
import math
from filterMasks import filterMasks

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
	for i in myhdf5Object:
		#print(str(myhdf5Object[i]))
		if ('dataset' in str(myhdf5Object[i])):
			#print("dataset is in"+str(myhdf5Object[i]))
			if ('Summarized' not in str(myhdf5Object[i])):
				replacementDictionary[i] = nan_to_num(myhdf5Object[i])
			else:
				x=1	
		else:
			replacementDictionary[i] = {}
			#print("dataset is not in"+str(myhdf5Object[i]))
			#print(i)
			replacementDictionary[i] = hdf5_to_dict(myhdf5Object[i])

	return replacementDictionary

def dictToScatterTable(myDict):

	#targetTable = copy.deepcopy(targetTableB)
	#correspondingKeys = copy.deepcopy(correspondingKeysB)
	
	targetTable = []
	correspondingKeys = []

	#make large table for each dictionary element
	for i in myDict:
		#print correspondingKeys
		#print dir(myDict[i])
		if('keys' not in dir(myDict[i])):
			if(len(targetTable)==0):
				targetTable = myDict[i]
				correspondingKeys = i
			else:
				targetTable = vstack([targetTable,myDict[i]])
				correspondingKeys = append(correspondingKeys,i)

		else:	#(there is a sub key)
			#print("Here be keys.  "+str(len(targetTable)))
			tempTable, tempKeys = dictToScatterTable(myDict[i])
			#print(str(len(targetTable))+", "+str(len(tempTable)))			
			if(len(targetTable)==0):
				targetTable =tempTable
				correspondingKeys = tempKeys

			else:
				
				targetTable = vstack([targetTable,tempTable])
				correspondingKeys = append(correspondingKeys,tempKeys)
		

	return targetTable,correspondingKeys

def chooseFromScatterTable(myTable,correspondingKeys,chosenKeys):

	temp = []

	for i in chosenKeys:
		myIndex = argmax(i==correspondingKeys)
		if len(temp) == 0:
			temp = 0+ myTable[myIndex]
		else:
			temp = vstack([temp,myTable[myIndex]])
	
	return temp

#get a nice gaussian when taking log of sxr0414. mean and median are much more similar. not so when distribution is lognormal
def getAllStats(x,axisToAverage,isLog=False):

	
	if(not isLog):
		toReturn = array([mean(x),median(x),std(x),len(x)])

	else:
		toReturn = array([exp(mean(log(x))),median(x),exp(std(log(x))),len(x)])

	return toReturn

#takes too long. not very efficient
def rollingStatistics(scatterData,axisToAverage,axisToBin,bins,m,isLog=False):
	
	stepSize = mean(list(set(diff(bins))))

	rebins = arange(bins[0],bins[-1]+2*stepSize,stepSize*1.0/m)

	movingStatistics = array([getAllStats([i[axisToAverage] for i in scatterData if (i[axisToBin]>j and i[axisToBin]<j+stepSize) ],axisToAverage,isLog) for j in rebins])

	myDict = {}
	myDict['x'] = rebins
	myDict['yMean'] = movingStatistics[:,0]
	myDict['yMedian'] = movingStatistics[:,1]
	myDict['standardDeviation'] = movingStatistics[:,2]
	myDict['counts'] = movingStatistics[:,3]


	notNanMask = True
	for i in myDict:		
		notNanMask *= array([not math.isnan(j) for j in myDict[i]])
	
	for i in myDict:		
		myDict[i] = myDict[i][notNanMask]

	
	return myDict

#to do list
#1) separate out mask section into directory and files. 
#2) add arg parser to go over battery of analysis and specified files. need to use the @ trick to get the interactive to work
#3) rolling statistics takes too long. how to speed up?

if __name__ == '__main__':
	


	currentWorkingDirectory = os.getcwd()

	h5FileName = sys.argv[1]
	experimentRunName = h5FileName.split("/")[1][:-3]

	f = h5py.File(currentWorkingDirectory+"/"+h5FileName,'r')
	myDict= hdf5_to_dict(f)
	f.close()

	myMask =  filterMasks.__dict__[experimentRunName](myDict)

	""""
	myMask = ones(len(myDict['acqiris2'])).astype(bool)
	myMask = myMask * (myDict['TSS_OPAL']['pixelTime']>0)	#excluding bad time tool data
	myMask = myMask * (myDict['acqiris2']>0.002)	#excluding bad acqiris data
	myMask = myMask * (myDict['acqiris2']<0.75)	#excluding bad acqiris data
	myMask = myMask * (myDict['GMD']>0.00001)	#excluding bad gmd data
	myMask = myMask * (myDict['GMD']<0.001)	#excluding bad gmd data
	myMask = myMask * (myDict['evr']['code_162']==0)
	myMask = myMask * (myDict['TSS_OPAL']['positionFWHM']<50)
	myMask = myMask * (myDict['TSS_OPAL']['positionFWHM']>10)
	myMask = myMask * (myDict['ebeam']['photon_energy']>900)
	myMask = myMask * (myDict['ebeam']['photon_energy']<930)
	#myMask = myMask * (myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (myDict['gas_detector']['f_11_ENRC']>1)
	"""

	myDict['normalizedAcqiris'] = myDict['acqiris2']/(1e-11+myDict['GMD'])	

	#time tool direction. need to abstract into config file
	myDict['estimatedTime'] = 2/.3*(myDict['delayStage']-49)+1*myDict['TSS_OPAL']['pixelTime']/1000.0	

	myDataMatrix,myCorrespondingKeys = dictToScatterTable(myDict)

	toBeBinned = myDataMatrix[:,myMask]

	
	myChosenKeys = ['normalizedAcqiris','estimatedTime']

	toBeBinned = chooseFromScatterTable(toBeBinned,myCorrespondingKeys,myChosenKeys)
	toBeBinned = toBeBinned.transpose()
	
	yEdges = arange(0,21,0.1)
	xEdges = arange(5.75,7.75,.01)

	y,x = toBeBinned.transpose()

	#def rollingStatistics(scatterData,axisToAverage,axisToBin,bins,m,isLog=False):
	myDataDictionary = rollingStatistics(toBeBinned,0,1,arange(0.5,21,.1),2,isLog=True)#very long wait time. not very efficient

	pickle.dump(myDataDictionary, open(currentWorkingDirectory+"/binnedData/"+experimentRunName+".pkl", "wb"))
	#temp = pickle.load(open(fileName[:-3]+".pkl","rb"))




