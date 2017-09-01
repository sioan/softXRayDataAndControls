from pylab import *
import psana

def getAndorImage(detectorObject,thisEvent):
	
	return detectorObject.image(thisEvent)
	#tempImage = detectorObject.image(thisEvent)
	#if(tempImage is not None):
	#	return tempImage
	#return zeros([512,2048])
	#else:
	#	return array([[0,0],[0,0]])



def getAndorImageSummarizer(detectorObject,thisEvent,previousProcessing):
	
	#return detectorObject.image(thisEvent)
	tempImage = detectorObject.image(thisEvent)
	myDict= {}

	try:
		if(type(previousProcessing) != dict):
			previousProcessing = {}
	except NameError:
		previousProcessing = {}

	if(tempImage is not None):
		print("got image")
		myEventId = thisEvent.get(psana.EventId)
		myTime = myEventId.time()[0]
		myDict["sec"+str(myTime)] = tempImage		
		
		previousProcessing.update(myDict)
	
	return previousProcessing

def genericReturn(detectorObject,thisEvent):
	return detectorObject(thisEvent)

def getAndorImageSum(detectorObject,thisEvent,previousProcessing):
	return 0

def getEvr(detectorObject,thisEvent):
	return detectorObject(thisEvent)

def getEvrSummary(detectorObject,thisEvent,previousProcessing):
	return 0

def getPeak(detectorObject,thisEvent):
	#return 0
	
	if(detectorObject(thisEvent)==None):
		return 0

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
	myWaveForm -= mean(myWaveForm[:2500])

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



