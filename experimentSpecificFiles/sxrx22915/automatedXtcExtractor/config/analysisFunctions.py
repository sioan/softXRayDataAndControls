from pylab import *
import psana
from roiConfigReader import *
myReadInConfig = roiConfigReader("config/x229_ROI_V1.csv")

def get_projection(detectorObject,thisEvent):
	myImage = detectorObject['TSS_OPAL'].raw(thisEvent)
	if None == myImage:
		return (zeros(1024))
	else:
		return sum(myImage[370:],axis=0)


def integrateAcqiris(detectorObject,thisEvent):
	myDict = {}

	#myDict['MCP'] = -99999
	acqirisData = detectorObject['acq01'](thisEvent)
	if any (None in acqirisData):
		myDict['MCP'] = -99999
	
	else:
		tempWaveform = acqirisData[0][2]
		myDict['MCP'] = -(sum(tempWaveform[1100:3000] - mean(tempWaveform[250:750])))

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

def getGMD(detectorObject,thisEvent):
	temp = detectorObject['GMD'].get(thisEvent)
	if (None not in [temp]):
		return temp.milliJoulesPerPulse()
	else: 	
		return 0

def GetZPX(detectorObject,thisEvent):
	temp = detectorObject['ZPX'](thisEvent)
	if (None not in [temp]):
		return temp
	else: 	
		return -999999

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
