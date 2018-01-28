from pylab import *
import psana
from roiConfigReader import *
# from IPython import embed
# myReadInConfig = roiConfigReader("config/x229_ROI_V1.csv")
import ConfigParser
import numpy as np
config = ConfigParser.RawConfigParser()
config.read("config/test.cfg")

def genericEPICSReturn(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	if (None is detectorObject[selfName](thisEvent)):
		return -999999

def getGMD(detectorObject,thisEvent):
	myDict={}
	personalAlias = detectorObject['self']
	temp = detectorObject[personalAlias].get(thisEvent)
	if temp is None:
		myDict['relativeEnergyPerPulse'] = -999999.0
		myDict['rawAvgBkgd'] = -999999.0
		myDict['sumAllPeaksFiltBkgd'] = -999999.0
		myDict['sumAllPeaksRawBkgd'] = -999999.0
	else: 	
		myDict['relativeEnergyPerPulse'] = temp.relativeEnergyPerPulse()
		myDict['rawAvgBkgd'] = temp.rawAvgBkgd()
		myDict['sumAllPeaksFiltBkgd'] = temp.sumAllPeaksFiltBkgd()
		myDict['sumAllPeaksRawBkgd'] = temp.sumAllPeaksRawBkgd()
	return myDict

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
			if acqirisData is None:
				myDict[alias] = -99999.
			else:
				tempWaveform = acqirisData[0][i]
				myDict[alias] = (sum(tempWaveform[st:end] - mean(tempWaveform[bgst:bgend])))

	return myDict

def sumOverROI(detectorObject,thisEvent):
	
	myImage = detectorObject['pnccd'].image(thisEvent)
	
	myDict = {}

	if myImage is None:
		#myDict['ROI1'] = -9999999
		#myDict['ROI2'] = -9999999
		for i in myReadInConfig.roiDescription:
			myDict[myReadInConfig.roiDescription[i]] = -9999999
	
	else:
		#myDict['ROI1'] = sum(myImage[420:560,80:220])
		#myDict['ROI2'] = sum(myImage[420:560,1040:1100])
		for i in myReadInConfig.roiDescription:
			validRunStart = myReadInConfig.roiDescription[i]['validRunStart']
			validRunEnd = myReadInConfig.roiDescription[i]['validRunEnd']
			if(thisEvent.run() >= validRunStart and thisEvent.run() < validRunEnd):
				#myDict['ROI2'] = sum(myImage[rowStart:rowEnd,columnStart:columnEnd])
				rowStart = myReadInConfig.roiDescription[i]['upperLeftY']
				rowEnd = myReadInConfig.roiDescription[i]['lowerRightY']
				columnStart = myReadInConfig.roiDescription[i]['upperLeftX']
				columnEnd = myReadInConfig.roiDescription[i]['lowerRightX']
				myDict[i] = sum(myImage[rowStart:rowEnd,columnStart:columnEnd])
				#print([rowStart,rowEnd,columnStart,columnEnd])


	return myDict

def accumulatorROIImage(detectorObject,thisEvent,previousProcessing):


	myImage = detectorObject['pnccd'].image(thisEvent)
	#myGMD = detectorObject['GMD'].get(thisEvent)

	desiredSingleImageEventList = [100,1000]

	myEventID = thisEvent.get(psana.EventId)
	sec,nanosec = myEventID.time()

	#if(None in [myImage,myGMD]):
	if(None in [myImage]):
		return previousProcessing
	else:
		x=1	#some dummy else
	
	if (len(previousProcessing.keys())==0):
		y,x = histogram(myImage.flatten(),bins=arange(-200,4000,10))
		previousProcessing['acummulatedHistogramCounts'] = y
		previousProcessing['acummulatedHistogramBins'] = x 
		previousProcessing['accumulatedImage'] = myImage
		previousProcessing['sparseData'] = {}
		previousProcessing['sparseData']['Images'] = []
		previousProcessing['sparseData']['myEventID'] = []

		myMask = zeros(myImage.shape)
		for i in myReadInConfig.roiDescription:
			validRunStart = myReadInConfig.roiDescription[i]['validRunStart']
			validRunEnd = myReadInConfig.roiDescription[i]['validRunEnd']
			if(thisEvent.run() >= validRunStart and thisEvent.run() < validRunEnd):
				#myDict['ROI2'] = sum(myImage[rowStart:rowEnd,columnStart:columnEnd])
				rowStart = myReadInConfig.roiDescription[i]['upperLeftY']
				rowEnd = myReadInConfig.roiDescription[i]['lowerRightY']
				columnStart = myReadInConfig.roiDescription[i]['upperLeftX']
				columnEnd = myReadInConfig.roiDescription[i]['lowerRightX']
				#myDict[i] = sum(myImage[rowStart:rowEnd,columnStart:columnEnd])
				#print([rowStart,rowEnd,columnStart,columnEnd])
				myMask[rowStart:rowEnd,columnStart:columnEnd] =	myMask[rowStart:rowEnd,columnStart:columnEnd]+1
		previousProcessing['roiSanityCheck'] = myMask

	else:
		previousProcessing['acummulatedHistogramCounts']+=histogram(myImage.flatten(),bins=arange(-200,4000,10))[0]
		#previousProcessing['accumulatedImage'] += myImage/myGMD.milliJoulesPerPulse()
		previousProcessing['accumulatedImage'] += myImage

	if( nanosec<0.01*1e9 and sec%2==0):
		previousProcessing['sparseData']['Images'].append(myImage)
		previousProcessing['sparseData']['myEventID'].append(str(myEventID))


	return previousProcessing





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
	if(tempImage is not None):
		print("got image")
		myEventId = thisEvent.get(psana.EventId)
		myTime = myEventId.time()[0]
		myDict["sec"+str(myTime)] = tempImage		
		try:
			previousProcessing.update(myDict)
		except AttributeError:
			print("creating first instance")
			previousProcessing = myDict
		except NameError:
			print("variable doesn't exist")
			#print("getAndorImageSummarizer is having an error")
	

	return previousProcessing



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

def getDelay(detectorObject, thisEvent):
	selfName = detectorObject['self_name']

	# IPython.embed()

	if detectorObject[selfName].values(thisEvent) is None:
		myDictionary = {'DLS_PS': -999.0}
		return myDictionary

	DLS_PS = detectorObject[selfName].values(thisEvent)[0]
	return {'DLS_PS': DLS_PS}


def getPeakArea(detectorObject, thisEvent):
	selfName = detectorObject['self_name']

	if detectorObject[selfName](thisEvent) is None:
		myDictionary = {'trace': -999.0 * np.ones(200, dtype=np.float64), 'even_level': -999.0, 'odd_level': -999.0, 'pulse_area': -999.0}
		# 243 myDictionary = {'trace': -999.0 * np.ones(2000, dtype=np.float64), 'even_level': -999.0, 'odd_level': -999.0,
		# 				'pulse_area': -999.0}
		return myDictionary

	# evenAverage = averagePulseInstance.f['summary/nonMeaningfulCoreNumber0/APD/averageWave1']
	# oddAverage = averagePulseInstance.f['summary/nonMeaningfulCoreNumber0/APD/averageWave2']
	# n = averagePulseInstance.f['summary/nonMeaningfulCoreNumber0/APD/n']

	#traces = detectorObject[selfName](thisEvent)[0][3] #243 - laser diode
	traces = detectorObject[selfName](thisEvent)[0][1] #< 243 - APD 4mm


	even_level = mean(traces[8000:-6:2])
	odd_level = mean(traces[8001:-6:2])
	#even_level = mean(traces[12000:-6:2])
	#odd_level = mean(traces[12001:-6:2])

	even_trace = -traces[1160:1360:2] + even_level
	odd_trace = -traces[1161:1361:2] + odd_level
	# even_trace = traces[1000:3000:2] - even_level
	# odd_trace = traces[1001:3001:2] - odd_level

	iw_trace = np.zeros(even_trace.shape[0] * 2, dtype=np.float64)
	iw_trace[::2] = even_trace
	iw_trace[1::2] = odd_trace

	pulse_area = np.sum(iw_trace)

	myDictionary = {'trace': traces[1160:1360], 'even_level': even_level, 'odd_level': odd_level, 'pulse_area': pulse_area}
	# myDictionary = {'trace': traces[1000:3000], 'even_level': even_level, 'odd_level': odd_level,
	# 				'pulse_area': pulse_area}

	# IPython.embed()

	return myDictionary




def accumulateAverageWave(detectorObject, thisEvent, previousProcessing):
	selfName = detectorObject['self_name']

	# IPython.embed()

	if ('averageWave1' not in previousProcessing):
		print ("initializing accumulator")
		previousProcessing['averageWave1'] = 0.0
		previousProcessing['averageWave2'] = 0.0
		previousProcessing['n'] = 0
	# if ('averageWave2' not in previousProcessing):
	# 	print ("initializing accumulator")
	# 	previousProcessing['averageWave2'] = 0.0

	myWaveForm1 = -detectorObject[selfName](thisEvent)[0][1][0::2]
	myWaveForm2 = -detectorObject[selfName](thisEvent)[0][1][1::2]
	# myWaveForm1 -= mean(myWaveForm1[:2500])

	# Those are in 'summary/nonMeaningfulCoreNumber0/APD/averageWave1'!!
	# Those are in 'summary/nonMeaningfulCoreNumber0/APD/averageWave2'!!
	previousProcessing['averageWave1'] = (previousProcessing['averageWave1'] + myWaveForm1)
	previousProcessing['averageWave2'] = (previousProcessing['averageWave2'] + myWaveForm2)
	previousProcessing['n'] += 1

	return previousProcessing




def getDaqEncoder(detectorObject, thisEvent):
        selfName = detectorObject['self_name']

        # IPython.embed()

        if detectorObject[selfName].values(thisEvent) is None:
                myDictionary = {'encoder': -999.0}
                return myDictionary

        encoder_value = detectorObject[selfName].values(thisEvent)[0]
        return {'encoder': encoder_value}



def XanthesumOverROI(detectorObject,thisEvent):
	
	myImage = detectorObject['pnccd'].image(thisEvent)
	
	myDict = {}

	if myImage is None:
		#myDict['ROI1'] = -9999999
		#myDict['ROI2'] = -9999999
		for i in myReadInConfig.roiDescription:
			myDict[myReadInConfig.roiDescription[i]] = -9999999
	
	else:
		#myDict['ROI1'] = sum(myImage[420:560,80:220])
		#myDict['ROI2'] = sum(myImage[420:560,1040:1100])
		for i in myReadInConfig.roiDescription:
			validRunStart = myReadInConfig.roiDescription[i]['validRunStart']
			validRunEnd = myReadInConfig.roiDescription[i]['validRunEnd']
			if(thisEvent.run() >= validRunStart and thisEvent.run() < validRunEnd):
				#myDict['ROI2'] = sum(myImage[rowStart:rowEnd,columnStart:columnEnd])
				rowStart = myReadInConfig.roiDescription[i]['upperLeftY']
				rowEnd = myReadInConfig.roiDescription[i]['lowerRightY']
				columnStart = myReadInConfig.roiDescription[i]['upperLeftX']
				columnEnd = myReadInConfig.roiDescription[i]['lowerRightX']
				myDict[i] = sum(myImage[rowStart:rowEnd,columnStart:columnEnd])
				#print([rowStart,rowEnd,columnStart,columnEnd])

	#IPython.embed()
	return myDict


def accumulatorROIImage(detectorObject,thisEvent,previousProcessing):


	myImage = detectorObject['pnccd'].image(thisEvent)
	#myGMD = detectorObject['GMD'].get(thisEvent)

	desiredSingleImageEventList = [100,1000]

	#myEventID = thisEvent.get(psana.EventId)

	#if(None in [myImage,myGMD]):
	if(None in [myImage]):
		return previousProcessing
	else:
		x=1	#some dummy else
	
	if ('acummulatedHistogram' not in previousProcessing.keys()):
		y,x = histogram(myImage.flatten(),bins=arange(-200,4000,10))
		previousProcessing['acummulatedHistogramCounts'] = y
		previousProcessing['acummulatedHistogramBins'] = x 
		previousProcessing['accumulatedImage'] = myImage

		myMask = zeros(myImage.shape)
		for i in myReadInConfig.roiDescription:
			validRunStart = myReadInConfig.roiDescription[i]['validRunStart']
			validRunEnd = myReadInConfig.roiDescription[i]['validRunEnd']
			if(thisEvent.run() >= validRunStart and thisEvent.run() < validRunEnd):
				#myDict['ROI2'] = sum(myImage[rowStart:rowEnd,columnStart:columnEnd])
				rowStart = myReadInConfig.roiDescription[i]['upperLeftY']
				rowEnd = myReadInConfig.roiDescription[i]['lowerRightY']
				columnStart = myReadInConfig.roiDescription[i]['upperLeftX']
				columnEnd = myReadInConfig.roiDescription[i]['lowerRightX']
				#myDict[i] = sum(myImage[rowStart:rowEnd,columnStart:columnEnd])
				#print([rowStart,rowEnd,columnStart,columnEnd])
				myMask[rowStart:rowEnd,columnStart:columnEnd] =	myMask[rowStart:rowEnd,columnStart:columnEnd]+1
		previousProcessing['roiSanityCheck'] = myMask

	else:
		previousProcessing['acummulatedHistogramCounts']+=histogram(myImage.flatten(),bins=arange(-200,4000,10))[0]
		#previousProcessing['accumulatedImage'] += myImage/myGMD.milliJoulesPerPulse()
		previousProcessing['accumulatedImage'] += myImage

	return previousProcessing

