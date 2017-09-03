#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python -i
from pylab import *
from scipy.interpolate import interp1d
import h5py
import argparse
from scipy.optimize import curve_fit
import pickle

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

#this is being abstracted from previous attempts to analyze SXRI0414.  how to abstract the approaches taken so far. they are
#1) the brute force standard deviation and mean.  (original provided by h5 file by pi.  gives the slow oscillation without much effort.)
#2) the elegant filtering using glue to get rid of zeros.
#3) and projection onto calibration curve gave nice slow oscillations.
#4) parsing the different scans.  didn't give oscillations. nice scans. fiducials odd vs even do correspond to event code 141

#4) binning acqiris/gmd for different delay stages (this is important. close to brute force)/. result is 2d. gona fit this data. want to understand maths of 
#fitting binned data.  This wasn't brute, but projection onto acqiris vs gmd calibration using calibration i0 as errorless x. not correct. but total least squares has fudge factor for weighting different detectors.
#5) making stage of acqiris vs gmd images for different delays. result is 3d data set.  too sparse in this case... yes?.  Used image j dynamic z_profiler to get delay axis. not intended result since each pixel is a count, not a normalized acqiris/gmd

#6) filtered on odd/even fiducials. should be the same event code as 141.  (the time tool bimodal distribution becomes a single mode when filtering on).  

#combo of brute force and fiducial filtering get's the oscillations.  parsing the different scans doesn't yield the oscillations.

#how to 3d and 2d data sets, abstracting is almost intuitive, but still needs some thought.  parsing each delay stage scan. the result is.... that's binned... into big time buckets. roughly equal length. so it's a 3d data set? yes. acqiris/gmd, delay stage, and big time buckets that correspond to human experienced time needed to finish one of the scans.  that becomes a 3d cube. if broken up into acqiris, gmd, delay stage, and scan #, that becomes a 4d cube.
  

#histogramdd. that should bin is as desired.  but how to get it into a format other programs like glue or imagej can use?  how to to make it so imagej's dynamic profiler can work on it without discounting weighting from 

#which way to plot? Which way to sum? Which slice or projection?  along which axis?

#turner normalize on event by event. silke normalizes averaged over several events.
#tim subtracts laser off shots
#filter on bad time tool amplitudes.

#notes from josh for sxri. doesn't belong here, needs to find a home.
#x-value (time in ps) = x-value (position of stage in mm) * 2 / c0
#where c0 should be 0.299792458 (speed of light in mm/ps)

#normalized acqiris is log normal distributed.  i.e. the histogram of log(normalizedAcqiris) is gaussian distributed.


#==================
#final product




#==================

#popt, pcov = curve_fit(normalDistribution, x[1][:-1], x[0],p0=[2000,6.5,7]) 
def normalDistribution(x,a,mu,s):
	return a*exp(-(x-mu)**2/(2.0*s**2))

def averageShiftedHistogram(x,binStart,binStop,binIncrement,myWeights,m):
	
	myCounts = array([])
	myBins = array([])
	
	
	for i in arange(0,binIncrement,binIncrement*1.0/m):
		myHistogram = histogram(x,bins=arange(binStart+i,binStop+i,binIncrement),weights=myWeights)
		myCounts = append(myCounts,myHistogram[0])
		myBins = append(myBins,myHistogram[1][:-1])

	sortedIndex = argsort(myBins)
	return myCounts[sortedIndex],myBins[sortedIndex]

def lognorm(x,a,mode,s):

	#a,mu,s = p

	mu = log(mode)+s**2
	return a*(1.0/(s*x*2*3.14159)*exp(-(log(x)-mu)**2/(2*s**2)))

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
	#myKernel = stats.gaussian_kde(toBeBinned[:,0])

	#movingMean = array([	median([i[0] for i in scatterData if (i[1]>j and i[1]<j+.1) ]) for j in arange(.5,21,.025)])
	#movingMedian = array([	median([i[0] for i in scatterData if (i[1]>j and i[1]<j+.1) ]) for j in arange(.5,21,.025)])
	
	stepSize = mean(list(set(diff(bins))))

	rebins = arange(bins[0],bins[-1]+2*stepSize,stepSize*1.0/m)

	movingStatistics = array([getAllStats([i[axisToAverage] for i in scatterData if (i[axisToBin]>j and i[axisToBin]<j+stepSize) ],axisToAverage,isLog) for j in rebins])

	myDict = {}
	myDict['x'] = rebins
	myDict['yMean'] = movingStatistics[:,0]
	myDict['yMedian'] = movingStatistics[:,1]
	myDict['standardDeviation'] = movingStatistics[:,2]
	myDict['counts'] = movingStatistics[:,3]
	

	#return rebins,movingStatistics
	return myDict


def rollingStatisticsOptimized(scatterData,axisToAverage,axisToBin,bins,m,isLog=False):

	
	stepSize = mean(list(set(diff(bins))))

	rebins = arange(bins[0],bins[-1]+2*stepSize,stepSize*1.0/m)
	myDict={}
	myDict['x'] = rebins
	myDict['yMean'] = {}
	myDict['standardDeviation'] = {}
	myDict['counts'] = {}

	for i in rebins:
		myDict['yMean'][str(i)] = 0
		myDict['standardDeviation'][str(i)] = 0
		myDict['counts'][str(i)] = 0

	#sortedIndex = scatterDataDummy[:,axisToBin]
	#scatterData = scatterDataDummy[sortedIndex]

		for i in scatterData:
			print i[axisToAverage]

	

	#return rebins,movingStatistics
	return myDict


#to do list
#1) add arg parser to go over battery of analysis and specified files. need to use the @ trick to get the interactive to work
#2) config file for which h5 files to compare
#3) wrap matplotlib for redundant plotting
#4) try and see if pyqtgraph image of 2dhistogram gives nice data. see the CLIexample.py in myAnalysis qt subdirectory
#5) rolling covariance
#6) rolling statistics takes too long. how to speed up?

if __name__ == '__main__':
	
	#print(sys.argv)	
	#print("parsing arguments")
	#myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
		
	
	#myParser.add_argument('-f','--fileName',help='fileName',default="None")
	
	#myArguments = myParser.parse_args()

	#main(myArguments.filename)
	#main("temp")

	#fileName = 'sxri0414run60'
	fileName = sys.argv[1]

	f = h5py.File(fileName,'r')
	myDict= hdf5_to_dict(f)
	f.close()

	

	#myMask = loadtxt("myMaskRun60.dat")	#it's a positive mask.  keeping data that is good
	#myMask = myMask.astype(bool)
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

	#when regulator is 1, not normalized by gmd. low oscilations present. disappear at meaningul normaization
	myDict['normalizedAcqiris'] = myDict['acqiris2']/(1e-11+myDict['GMD'])	

	#time tool direction. need to abstract into config file
	myDict['estimatedTime'] = 2/.3*(myDict['delayStage']-49)+1*myDict['TSS_OPAL']['pixelTime']/1000.0	

	myDataMatrix,myCorrespondingKeys = dictToScatterTable(myDict)

	toBeBinned = myDataMatrix[:,myMask]
	#toBeBinned = array([i[::-1] for i in toBeBinned.transpose()])
	#toBeBinned = toBeBinned[::-1]
	
	myChosenKeys = ['normalizedAcqiris','estimatedTime']

	toBeBinned = chooseFromScatterTable(toBeBinned,myCorrespondingKeys,myChosenKeys)
	toBeBinned = toBeBinned.transpose()
	
	yEdges = arange(0,21,0.1)
	xEdges = arange(5.75,7.75,.01)

	y,x = toBeBinned.transpose()
	
	H, xedges, yedges = np.histogram2d(log(y), x, bins=(xEdges, yEdges))	#try to get least processing done before showing image. use averaged shifted histogram
	import pyqtgraph as pg
	#pg.image(H.transpose(), title="Simplest possible image example")

	#def rollingStatistics(scatterData,axisToAverage,axisToBin,bins,m,isLog=False):
	myDataDictionary = rollingStatistics(toBeBinned,0,1,arange(0.5,21,.1),1,isLog=True)	#very long wait time. not very efficient

	pickle.dump(myDataDictionary, open( fileName[:-3]+".pkl", "wb"))
	temp = pickle.load(open(fileName[:-3]+".pkl","rb"))

	#plot(
	#plot(max(x[0])-x[0],x[1][:,0])
	#plot(max(x[0])-x[0],x[1][:,1])
	#show()




