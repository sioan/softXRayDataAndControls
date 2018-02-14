from pylab import *
import psana

def integrateAcqiris(detectorObject,thisEvent):
	myDict = {}
	AcqAlias = detectorObject['self']	
	acqirisData = detectorObject[AcqAlias](thisEvent)
	for i in range(4):
		if config.has_option(AcqAlias, "Ch"+str(i)+"Alias"):
			alias = config.get(AcqAlias, "Ch"+str(i)+"Alias")
			st = config.getint(AcqAlias, "Ch"+str(i)+"Start")
			end = config.getint(AcqAlias, "Ch"+str(i)+"End")
			bgst = config.getint(AcqAlias, "Ch"+str(i)+"Bgstart")
			bgend = config.getint(AcqAlias, "Ch"+str(i)+"Bgend")
			if any (None in acqirisData):
				myDict[alias] = -99999
			else:
				tempWaveform = acqirisData[0][i]
				myDict[alias] = (sum(tempWaveform[st:end] - mean(tempWaveform[bgst:bgend])))

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


