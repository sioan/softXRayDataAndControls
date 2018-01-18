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
		

#function below returns these values
#['MONO_GRATING_1 (PGR1)','MONO_GRATING_2 (PGR2)','MONO_MIRROR_1 (SMR1)','MONO_MIRROR_2 (SMR2)']
def getMonoEncoderValues(detectorObject,thisEvent):
	return detectorObject.values(thisEvent)

def getAndorImageSummarizer(detectorObject,thisEvent,previousProcessing):
	
	#return detectorObject.image(thisEvent)
	tempImage = detectorObject.image(thisEvent)
	myDict= {}
	if(tempImage is not None):
		
		print("got image")
		myEventId = thisEvent.get(psana.EventId)
		myTime = myEventId.time()[0]
		myDict["sec"+str(myTime)] = tempImage		

		myFile = "AndorImages/run"+str(thisEvent.run())+"sec"+str(myTime)+".dat"
		savetxt(myFile,tempImage)
		

		try:
			previousProcessing.update(myDict)
		except AttributeError:
			print("creating first instance")
			previousProcessing = myDict
		except NameError:
			print("variable doesn't exist")
			#print("getAndorImageSummarizer is having an error")
	

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

"""
def accumulateAverageWave(detectorObject,thisEvent,previousProcessing):
	
	try: 
		dummy = previousProcessing
	except:
		previousProcessing = {}
	
	if(detectorObject(thisEvent)!=None):
		previousProcessing["a1"] += detectorObject(thisEvent)[0][1]

	myWaveForm = -detectorObject(thisEvent)[0][0]
	myWaveForm -= mean(myWaveForm[:2500])

	return (previousProcessing+myWaveForm)
"""

def getAcqirisData(detectorObject,thisEvent):
	myDict = {}

	myDict['MCPI0'] = 0
	myDict['diodeFluorescence'] = 0
	#if (None not in [detectorObject(thisEvent)]):
	if (None is not detectorObject(thisEvent)):
		tempWaveform = detectorObject(thisEvent)[0][1]
		myDict['diodeFluorescence'] = -(sum(tempWaveform[1150:1300] - mean(tempWaveform[600:750])))

		tempWaveform = detectorObject(thisEvent)[0][2]
		myDict['MCPI0'] = -(sum(tempWaveform[1200:1400] - mean(tempWaveform[600:800])))  
    
	return myDict

def getAcqiris2Data(detectorObject,thisEvent):
	myDict = {}

	myDict['MCPFluorescence'] = 0
	#if (None not in [detectorObject(thisEvent)]):
	if (None is not detectorObject(thisEvent)):
		tempWaveform = detectorObject(thisEvent)[0][1]
		myDict['MCPFluorescence'] = -(sum(tempWaveform[1180:1220] - mean(tempWaveform[600:640])))

	return myDict

def getAcqiris2Data_ring(detectorObject,thisEvent):
	myDict = {}

	myDict['MCPFluorescence'] = 0
	if (None not in [detectorObject(thisEvent)[0][0]]):
		tempWaveform = detectorObject(thisEvent)[0][1]
		myDict['MCPFluorescence'] = sum(np.abs((tempWaveform[1180:3220] - mean(tempWaveform[600:640]))))

	return myDict

def getWaveForm(detectorObject,thisEvent):
	if (None not in [detectorObject(thisEvent)[0][0]]):
		return detectorObject(thisEvent)[0][0]
	else:	
		return zeros(5000)
	
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
	myDict = {}

	myDict['milliJoulesPerPulse'] = 0
	myDict['milliJoulesAverage'] = 0
	temp = detectorObject.get(thisEvent)
	if (None not in [temp]):
		myDict['milliJoulesPerPulse'] = temp.milliJoulesPerPulse()
		myDict['milliJoulesAverage'] = temp.milliJoulesAverage()
	
	return myDict

def getEBeam(detectorObject,thisEvent):
	temp = detectorObject.get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0



