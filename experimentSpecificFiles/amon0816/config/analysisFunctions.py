from pylab import *

def getEBeam(detectorObject,thisEvent):
	temp = detectorObject.get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0

def getPeak(detectorObject,thisEvent):

	if( detectorObject(thisEvent) is None):
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

	if( detectorObject(thisEvent) is None):
		return 0

	myWaveForm = -detectorObject(thisEvent)[0][0]
	myWaveForm -= mean(myWaveForm[:2500])

	return (previousProcessing+myWaveForm)
