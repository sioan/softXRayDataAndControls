from pylab import *
import psana
import IPython
import h5py

fileName = "regressionReferenceBasis/sxri0214run149.h5"
referenceHdf5 = h5py.File(fileName ,'r')
referenceWave = referenceHdf5['summary']['nonMeaningfulCoreNumber0']['ACQ1']['averageWave0']
referenceWave -= mean(referenceWave)
refWaveSelfDot = dot(referenceWave,referenceWave)

def integrateAcqiris(detectorObject,thisEvent):
	myDict = {}
	AcqAlias = detectorObject['self_name']	
	y,x = detectorObject[AcqAlias](thisEvent)
	

	if (None is y):
		myDict['MCP'] = -99999.0
	else:
		myDict['MCP'] = sum(y[0,4720:5220]-mean(y[0,0:4000]))
				
	

	return myDict

def chopperState(detectorObject,thisEvent):
	myDict = {}
	chopperAlias = detectorObject['self_name']
	y,x = detectorObject[chopperAlias](thisEvent)

	if (None is y):
		myDict['chopperState']=-999999.0
	else:
		myDict['chopperState']= mean(y[0])	#justify with boiler plate view analysis. this is painful. how to streamline?
		#idea: put a commented flag here that tells the "to be written" script to bring up data

	return myDict

def genericReturn(detectorObject,thisEvent):
	myDict = {}
	genericDetectorAlias = detectorObject['self_name']
	genericValue = detectorObject[genericDetectorAlias](thisEvent)
	
	if(genericValue is None):
		myDict[genericDetectorAlias] = -9999.0
		
	else:
		myDict[genericDetectorAlias] = genericValue

	return myDict

def getGMD(detectorObject, thisEvent):
	myAlias = detectorObject['self_name']
	temp = detectorObject[myAlias].get(thisEvent)
	myDict = {}
	if(temp is None):

		myDict['milliJoulesPerPulse'] = -99999.0
	else:
		myGmdValue = temp.milliJoulesPerPulse()
		myDict['milliJoulesPerPulse'] = myGmdValue

	return myDict


def regressAgainstAverageWave(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	myDict = {}
	myDict['amplitude'] = -99999.0
	if None is detectorObject[selfName](thisEvent):
		pass

	else:
		myWaveForm = -detectorObject[selfName](thisEvent)[0][0]
		myWaveForm-=mean(myWaveForm)

		myDict['amplitude'] = dot(myWaveForm,referenceWave)/refWaveSelfDot

	return myDict

def getPeak(detectorObject,thisEvent):

	selfName = detectorObject['self_name']

	myWaveForm = -detectorObject[selfName](thisEvent)[0][0]

	myWaveForm -= mean(myWaveForm[-1000:-100])

	x = arange(len(myWaveForm))[7500:10000]-8406
	myFit = polyfit(x, myWaveForm[7500:10000],3)

	p = poly1d(myFit)
	myMax = max(p(x))

	#return myFit[-1]	#placing a dictionary here also works
	return myMax	

def accumulateAverageWave(detectorObject,thisEvent,previousProcessing):

	selfName = detectorObject['self_name']

	#IPython.embed()

	if('averageWave0' not in previousProcessing):
		print ("initializing accumulator")
		previousProcessing['averageWave0']=0.0
		previousProcessing['averageWave1']=0.0

	myWaveForm0 = -detectorObject[selfName](thisEvent)[0][0]
	myWaveForm0 -= mean(myWaveForm0[:2500])

	myWaveForm1 = -detectorObject[selfName](thisEvent)[0][1]
	myWaveForm1 -= mean(myWaveForm1[:2500])

	previousProcessing['averageWave0'] = (previousProcessing['averageWave0']+myWaveForm0)
	previousProcessing['averageWave1'] = (previousProcessing['averageWave1']+myWaveForm1)

	return previousProcessing

def getWaveForm(detectorObject,thisEvent):

	selfName = detectorObject['self_name']

	if (None not in [detectorObject[selfName](thisEvent)[0][0]]):
		return detectorObject[selfName](thisEvent)[0][0]
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

def getTimeToolData(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	ttData = detectorObject[selfName].process(thisEvent)
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

