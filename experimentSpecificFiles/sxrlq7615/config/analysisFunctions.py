from pylab import *
import psana
#from IPython import embed

def integrateAcqiris(detectorObject,thisEvent):
	myDict = {}
	AcqAlias = detectorObject['self_name']	
	y,x = detectorObject[AcqAlias](thisEvent)
	

	if (None is y):
		myDict['MCP'] = -99999
	else:
		myDict['MCP'] = sum(y[0,4720:5220]-mean(y[0,0:4000]))
				
	

	return myDict

def genericReturn(detectorObject,thisEvent):
	myDict = {}
	genericDetectorAlias = detectorObject['self_name']
	genericValue = detectorObject[genericDetectorAlias](thisEvent)
	
	if(genericValue is None):
		myDict[genericDetectorAlias] = -9999
		
	else:
		myDict[genericDetectorAlias] = genericValue

	return myDict

def getGMD(detectorObject, thisEvent):
	myAlias = detectorObject['self_name']
	temp = detectorObject[myAlias].get(thisEvent)
	myGmdValue = temp.milliJoulesPerPulse()
	myDict = {}
	if(myGmdValue is None):
		myDict['milliJoulesPerPulse'] = -99999
	else:
		myDict['milliJoulesPerPulse'] = myGmdValue

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

#def getGMD(detectorObject,thisEvent):
#	temp = detectorObject.get(thisEvent)
#	if (None not in [temp]):
#		return temp.milliJoulesPerPulse()
#	else: 	
#		return 0

def getEBeam(detectorObject,thisEvent):
	temp = detectorObject.get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0


