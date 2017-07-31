from pylab import *
import psana

def getPeak(detectorObject,thisEvent):

	myWaveForm = -detectorObject(thisEvent)[0][0]

	myWaveForm -= mean(myWaveForm[:2500])

	myFit = polyfit(arange(len(myWaveForm))[7500:10000]-8406, myWaveForm[7500:10000],3)

	

	return myFit[-1]

def getWaveForm(detectorObject,thisEvent):
	return detectorObject(thisEvent)[0][0]
	
def get(detectorObject,thisEvent):
	return detectorObject(thisEvent)

def getRaw(detectorObject,thisEvent):
	return detectorObject(thisEvent)

def getGMD(detectorObject,thisEvent):
	
	temp = detectorObject.get(thisEvent)
	if(temp is None):
		print("bad event")
		return None

	else:
		return temp.milliJoulesPerPulse()

def getEBeam(detectorObject,thisEvent):
	temp = detectorObject.get(thisEvent)
	return temp.ebeamPhotonEnergy()
