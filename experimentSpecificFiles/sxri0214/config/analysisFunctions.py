from pylab import *
import psana

def genericReturn(detectorObject,thisEvent):
	return detectorObject(thisEvent)

def genericSummaryZero(detectorObject,thisEvent,previousProcessing):
	return 0

def myZeroReturn(detectorObject,thisEvent,previousProcessing):
	return 0

def getTimeToolData(detectorObject,thisEvent):
	ttData = detectorObject.process(thisEvent)
	myDict = {}	
	if(ttData is None):
		
		myDict['amplitude'] = -99999
		myDict['pixelTime'] = -99999
		myDict['positionFWHM'] = -99999


	else:

		myDict['amplitude'] = ttData.amplitude()
		myDict['pixelTime'] = ttData.position_time()
		myDict['positionFWHM'] = ttData.position_fwhm()

	return myDict

def chopperState(detectorObject,thisEvent):
	myDict = {}

	for i in arange(4):
		myDict['CH'+str(i)] = -99999
	if (None not in [detectorObject(thisEvent)[0][0]]):
		for i in arange(4):
			tempWaveform = detectorObject(thisEvent)[0][i]
			myDict['CH'+str(i)] = mean(tempWaveform)
		  
	return myDict


def integrateAcqiris(detectorObject,thisEvent):
	myDict = {}

	myDict['scatterAPD'] = -99999
	if (None not in [detectorObject(thisEvent)[0][0]]):
		tempWaveform = detectorObject(thisEvent)[0][0]
		myDict['scatterAPD'] = -(sum(tempWaveform[4000:18000] - mean(tempWaveform[0:3000])))
		  
	return myDict

def getPeak(detectorObject,thisEvent):

	myWaveForm = -detectorObject(thisEvent)[0][0]

	myWaveForm -= mean(myWaveForm[:2500])

	x = arange(len(myWaveForm))[7500:10000]-8406
	myFit = polyfit(x, myWaveForm[7500:10000],3)

	p = poly1d(myFit)
	myMax = max(p(x))

	#return myFit[-1]	#placing a dictionary here also works
	return myMax	

def accumulateAverageWave(detectorObject,thisEvent,previousProcessing):

	myWaveForm = -detectorObject(thisEvent)[0][0]
	myWaveForm -= mean(myWaveForm)

	return (previousProcessing+myWaveForm)

def getWaveForm(detectorObject,thisEvent):
	if (None not in [detectorObject(thisEvent)[0][0]]):
		return detectorObject(thisEvent)[0][0]
	else:	
		return 0
	
def get(detectorObject,thisEvent):
	if (None not in [detectorObject(thisEvent)]):
		return detectorObject(thisEvent)
	else:
		return 0

def getRaw(detectorObject,thisEvent):
	if (None not in [detectorObject(thisEvent)]):
		return detectorObject(thisEvent)
	else:
		return 0

def getGMD(detectorObject,thisEvent):
	temp = detectorObject.get(thisEvent)
	if (None not in [temp]):
		return temp.milliJoulesPerPulse()
	else: 	
		return 0

def getEBeam(detectorObject,thisEvent):
	temp = detectorObject.get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0



