from pylab import *
import psana
import IPython

def getDelay(detectorObject, thisEvent):
        selfName = detectorObject['self_name']

        # IPython.embed()

        if detectorObject[selfName].values(thisEvent) is None:
                myDictionary = {'DLS_PS': -999.0}
                return myDictionary

        DLS_PS = detectorObject[selfName].values(thisEvent)[0]
        return {'DLS_PS': DLS_PS}


def genericReturn(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	x = detectorObject[selfName](thisEvent)
	if x is None:
		return -9999.0
	else:
		return x

def genericSummaryZero(detectorObject,thisEvent,previousProcessing):
	return 0

def myZeroReturn(detectorObject,thisEvent,previousProcessing):
	return 0

def getTimeToolData(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	ttData = detectorObject[selfName].process(thisEvent)
	myDict = {}	
	if(ttData is None):
		
		myDict['amplitude'] = -99999.0
		myDict['pixelTime'] = -99999.0
		myDict['positionFWHM'] = -99999.0


	else:

		myDict['amplitude'] = ttData.amplitude()
		myDict['pixelTime'] = ttData.position_time()
		myDict['positionFWHM'] = ttData.position_fwhm()

	return myDict

def getxtcavData(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	detectorObject[selfName]

def getpeakb(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	myDict = {}
	myDict['APDNOAP'] = -9999.0
	myDict['APDAP'] = -9999.0
	myDict['MCPI0'] = -9999.0
	
	myWaveForm = detectorObject[selfName].waveform(thisEvent)
	if any (None in [myWaveForm]):
		return myDict
	
	MCPI0ind = 1202
	APDNOAPind = 1208
	APDAPind = 1207
	MCPI0width = 40
	APDwidth = 100
	
	myWaveForm[0] -= mean(myWaveForm[0][:1000]) #small APD	
	myWaveForm[1] -= mean(myWaveForm[1][:1000]) #large APD
	myWaveForm[2] -= mean(myWaveForm[2][:1000]) #MCP
	myDict['APDAP'] = mean(myWaveForm[0][APDAPind-APDwidth:APDAPind+APDwidth])	
	myDict['APDNOAP'] = mean(myWaveForm[1][APDNOAPind-APDwidth:APDNOAPind+APDwidth])
	myDict['MCPI0'] = mean(myWaveForm[2][MCPI0ind-MCPI0width:MCPI0ind+MCPI0width])
	

	#IPython.embed()

	return myDict	

def getPeak(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	myWaveForm = -detectorObject[selfName](thisEvent)[0][0]

	myWaveForm -= mean(myWaveForm[:2500])

	x = arange(len(myWaveForm))[7500:10000]-8406
	myFit = polyfit(x, myWaveForm[7500:10000],3)

	p = poly1d(myFit)
	myMax = max(p(x))

	#return myFit[-1]	#placing a dictionary here also works
	return myMax	

def accumulateAverageWave(detectorObject,thisEvent,previousProcessing):
	selfName = detectorObject['self_name']

	myWaveForm = -detectorObject[selfName](thisEvent)[0][0]
	myWaveForm -= mean(myWaveForm[:2500])

	return (previousProcessing+myWaveForm)

def getWaveForm(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	if (None not in [detectorObject[selfName](thisEvent)[0][0]]):
		return detectorObject[selfName](thisEvent)[0][0]
	else:	
		return 0.0
	
def get(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	
	if (None not in [detectorObject[selfName](thisEvent)]):
		return detectorObject[selfName](thisEvent)
	else:
		return 0.0

def getRaw(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	if (None not in [detectorObject[selfName](thisEvent)]):
		return detectorObject[selfName](thisEvent)
	else:
		return 0.0

def getGMD(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	temp = detectorObject[selfName].get(thisEvent)
	if (None not in [temp]):
		return temp.milliJoulesPerPulse()
	else: 	
		return 0.0

def getEBeam(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	temp = detectorObject[selfName].get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0.0

def getSum(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	
	myImage = detectorObject[selfName].image(thisEvent)
	
	myDict = {}
	myDict['sum'] = -999.0
	if None is not myImage:
		myDict['sum'] = sum(myImage[500:620,720:850])
	#IPython.embed()

	return myDict



