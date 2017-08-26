#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python -i
from pylab import *
from scipy.interpolate import interp1d
import h5py
import argparse
from scipy.optimize import curve_fit

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

#==================
#final product




#==================

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

"""
def main(filename):
	global myDict

	fileName = 'sxri0414run60.h5'

	f = h5py.File(fileName,'r')
	myDict= hdf5_to_dict(f)
	f.close()

	

	myMask = loadtxt("myMask.dat")
	myMask = myMask.astype(bool)
	#chosenKeys = ['GMD','acqiris']
	myMask = myMask * (myDict['TSS_OPAL']['pixelTime']<0)
	myMask = myMask * (myDict['fiducials']%4==1)	#this has no effect on fourier components

	myDict['normalizedAcqiris'] = myDict['acqiris2']/myDict['GMD']
	myDict['estimatedTime'] = 2/.3*(myDict['delayStage']-49)+0*myDict['TSS_OPAL']['pixelTime']/1000.0

	myDataMatrix,myCorrespondingKeys = dictToScatterTable(myDict)

	toBeBinned = myDataMatrix[:,myMask==False]
	
	myChosenKeys = ['normalizedAcqiris','estimatedTime']

	toBeBinned = chooseFromScatterTable(toBeBinned,myCorrespondingKeys,myChosenKeys)
	toBeBinned = toBeBinned.transpose()

	#binEdgesDictionary = makeBinEdgesDictionary


	#binEdges = (arange(0,.0014,.0014/20.0),arange(0,1,1/20.0),arange(-1,4,.015))
	#binEdges = (arange(0,2*.0014,.0014),arange(0,2*1,1),arange(-1,20,.10))
	#binEdges = (arange(0,2*.0014,.0014),arange(0,2*1,1),arange(-1,20,.10))
	binEdges = (arange(0,4000,3000),arange(-1,20,.05))

	myWeights = 0+toBeBinned[:,0]
	

	myBinCount = histogramdd(toBeBinned,bins=binEdges)

	myBinAverage = histogramdd(toBeBinned,bins=binEdges,weights=myWeights)

	myBin2Moment = histogramdd(toBeBinned,bins=binEdges,weights=myWeights**2)
	myBin2StanError = (myBin2Moment[0] - myBinAverage[0]**2)**0.5/myBinCount[0]**0.5

	plot(myBinCount[1][1][:-1],(myBinAverage[0][0]/myBinCount[0][0])[::-1])
	show()
"""

if __name__ == '__main__':
	
	#print(sys.argv)	
	#print("parsing arguments")
	#myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
		
	
	#myParser.add_argument('-f','--fileName',help='fileName',default="None")
	
	#myArguments = myParser.parse_args()

	#main(myArguments.filename)
	#main("temp")

	fileName = 'sxri0414run63.h5'

	f = h5py.File(fileName,'r')
	myDict= hdf5_to_dict(f)
	f.close()

	

	myMask = loadtxt("myMask.dat")	#it's a positive mask.  keeping data that is good
	myMask = myMask.astype(bool)
	#chosenKeys = ['GMD','acqiris']
	#myMask = [myDict]
	myMask = myMask * (myDict['TSS_OPAL']['pixelTime']>0)	#excluding bad time tool data
	myMask = myMask * (myDict['acqiris2']>0.002)	#excluding bad acqiris data
	#myMask = myMask * (myDict['acqiris2']<0.75)	#excluding bad acqiris data
	myMask = myMask * (myDict['GMD']>0.00001)	#excluding bad gmd data
	#myMask = myMask * (myDict['GMD']<0.001)	#excluding bad gmd data
	#myMask = myMask * (myDict['fiducials']%4==3)	#this has no effect on fourier components
	

	myDict['normalizedAcqiris'] = myDict['acqiris2']/(1e-11+myDict['GMD'])	#when regulator is 1, not normalized by gmd. low oscilations present. disappear at meaningul normaization
	myDict['estimatedTime'] = 2/.3*(myDict['delayStage']-49)+1*myDict['TSS_OPAL']['pixelTime']/1000.0	#time tool direction. need to abstract into config file

	myDataMatrix,myCorrespondingKeys = dictToScatterTable(myDict)

	toBeBinned = myDataMatrix[:,myMask]
	
	myChosenKeys = ['normalizedAcqiris','estimatedTime']

	toBeBinned = chooseFromScatterTable(toBeBinned,myCorrespondingKeys,myChosenKeys)
	toBeBinned = toBeBinned.transpose()

	#binEdgesDictionary = makeBinEdgesDictionary


	#binEdges = (arange(0,.0014,.0014/20.0),arange(0,1,1/20.0),arange(-1,4,.015))
	#binEdges = (arange(0,2*.0014,.0014),arange(0,2*1,1),arange(-1,20,.10))
	#binEdges = (arange(0,2*.0014,.0014),arange(0,2*1,1),arange(-1,20,.10))
	
	#####################
	####brute average###
	#binEdges = (arange(0,4000,3001),arange(-1,20,.1))
	binEdges = (arange(0,4000,3001),arange(-0.05,20,.1))		#bin size.  need to abstract it into config file. 
	#0.1 see's low frequency oscillations. That's the delay stage step. 
	#0.0125 see's multiple harmonics at 10.5 THZ, 20.5 THz and 30.5 THz (are units correct?) in bin count.  
	#what's the physical interpretation?  Lame interpretation.  Due to sub delayStage resolution binning.  Would normally give sharp spikes
	#that alias between the binning frequency and delayStage.  the time tool partially smears that away, but it's still present.

	myWeights = 0+toBeBinned[:,0]
	

	myBinCount = histogramdd(toBeBinned,bins=binEdges)

	myBinAverage = histogramdd(toBeBinned,bins=binEdges,weights=myWeights)[0][0]/myBinCount[0][0]

	myBin2Moment = histogramdd(toBeBinned,bins=binEdges,weights=myWeights**2)[0][0]/myBinCount[0][0]
	myBin2StanError = abs(myBin2Moment - myBinAverage**2)**0.5/myBinCount[0][0]**0.5

	subplot(231)
	#plot(myBinCount[1][1][:-1][::-1],myBinAverage,'.')
	plot(binEdges[1][:-1][::-1],myBinAverage,'.')
	#errorbar(myBinCount[1][1][:-1][::-1],myBinAverage,yerr=myBin2StanError)

	subplot(232)
	plot(myBinCount[1][1][:-1][::-1],(myBinCount[0][0])[::-1],'.')

	subplot(234)
	myFFT = (abs(fft(nan_to_num(myBinAverage[51:]))))
	#myFFT = log(abs(fft(myBinCount[0][0][51:])))	#this shows intensity response in fourier domain is an artifact.
	myFFT = myFFT[:int(len(myFFT)/2)]
	semilogy(arange(len(myFFT))*1.0/20,myFFT)

	subplot(235)
	#myFFT = log(abs(fft(myBinAverage[51:])))
	myFFT = (abs(fft(myBinCount[0][0][51:])))	#this shows intensity response in fourier domain is an artifact.  is present even when mask is all true
	myFFT = myFFT[:int(len(myFFT)/2)]
	semilogy(arange(len(myFFT))*1.0/20,myFFT)

	tempAverage = 0 + myBinAverage
	
	###############################
	#####fitting distribution###### 
	#abstracting different analysis types using histogramdd with different parameters

	binEdges = (arange(0,3000,30),arange(-0.05,20,.1))		#bin size.  need to abstract it into config file. 
	#0.1 see's low frequency oscillations. That's the delay stage step. 
	#0.0125 see's multiple harmonics at 10.5 THZ, 20.5 THz and 30.5 THz (are units correct?) in bin count.  
	#what's the physical interpretation?  Lame interpretation.  Due to sub delayStage resolution binning.  Would normally give sharp spikes
	#that alias between the binning frequency and delayStage.  the time tool partially smears that away, but it's still present.

	myWeights = 0+toBeBinned[:,0]
	

	myBinCount = histogramdd(toBeBinned,bins=binEdges)

	myBinAverage = histogramdd(toBeBinned,bins=binEdges,weights=myWeights)[0][0]/myBinCount[0][0]

	myBin2Moment = histogramdd(toBeBinned,bins=binEdges,weights=myWeights**2)[0][0]/myBinCount[0][0]
	myBin2StanError = abs(myBin2Moment - myBinAverage**2)**0.5/myBinCount[0][0]**0.5

	#actual fitting starts here.
	#mu = log(mode)+s**2  and
	#variance = (exp(s**2)-1)*exp(2*mu+s**2) for initial guess. variance doesn't solve well
	
	#def lognorm(x,p):
	#a,mu,s = p
	myModes = []
	myModeError = []
	mySigma = []
	for thisBin in arange(myBinCount[0].shape[1]):
		#initGuess = array([1,7.6,1])		
		maxBinCountIndex= argmax(myBinCount[0][1:,thisBin])
		myMode =	myBinCount[0][1:,thisBin][maxBinCountIndex]
		
		initGuess = array([sum(myBinCount[0][1:,thisBin]),myMode,1])
		popt, pcov = curve_fit(lognorm, binEdges[0][1:-1][::1], myBinCount[0][1:,thisBin],p0=initGuess)
		#plot(binEdges[0][1:-1][::1],lognorm(binEdges[0][1:-1][::1],*popt))
		myModes = append(myModes,popt[1])
		myModeError = append(myModeError,pcov[1,1])
		mySigma = append(mySigma,popt[2])

	subplot(233)
	#errorbar(myBinCount[1][1][:-1][::-1],myModes,yerr=myModeError)
	plot(myBinCount[1][1][:-1][::-1],myModes,'.')

	subplot(236)
	#errorbar(myBinCount[1][1][:-1][::-1],myModes,yerr=myModeError)
	#plot(myBinCount[1][1][:-1][::-1],mySigma,'.')
	myFFT = (abs(fft(myModes[10:])))	#this shows intensity response in fourier domain is an artifact.  is present even when mask is all true
	myFFT = myFFT[:int(len(myFFT)/2)]
	semilogy(arange(len(myFFT))*1.0/20,myFFT)
	show()

