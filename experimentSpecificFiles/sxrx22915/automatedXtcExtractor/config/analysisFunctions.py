from pylab import *
import psana


def integrateAcqiris(detectorObject,thisEvent):
	myDict = {}

	myDict['MCP'] = -99999
	acqirisData = detectorObject['acq01'](thisEvent)
	if (None not in acqirisData):
		tempWaveform = acqirisData[0][0]
		myDict['MCP'] = -(sum(tempWaveform[1190:1220] - mean(tempWaveform[0:1190])))

	return myDict

def sumOverROI(detectorObject,thisEvent):
	
	myImage = detectorObject['pnccd'].image(thisEvent)
	
	myDict = {}

	if myImage is None:
		myDict['ROI1'] = -9999999
		myDict['ROI2'] = -9999999
	
	else:
		myDict['ROI1'] = sum(myImage[420:560,80:220])
		myDict['ROI2'] = sum(myImage[420:560,1040:1100])


	return myDict

def getGMD(detectorObject,thisEvent):
	temp = detectorObject['GMD'].get(thisEvent)
	if (None not in [temp]):
		return temp.milliJoulesPerPulse()
	else: 	
		return 0

def accumulatorROIImage(detectorObject,thisEvent,previousProcessing):


	myImage = detectorObject['pnccd'].image(thisEvent)
	myGMD = detectorObject['GMD'].get(thisEvent)

	if(None in [myImage,myGMD]):
		return previousProcessing
	else:
		x=1	#some dummy else
	
	if ('acummulatedHistogram' not in previousProcessing.keys()):
		y,x = histogram(myImage.flatten(),bins=arange(-200,4000,10))
		previousProcessing['acummulatedHistogramCounts'] = y
		previousProcessing['acummulatedHistogramBins'] = x 
		previousProcessing['accumulatedImage'] = myImage

	else:
		previousProcessing['acummulatedHistogramCounts']+=histogram(myImage.flatten(),bins=arange(-200,4000,10))[0]
		previousProcessing['accumulatedImage'] += myImage/myGMD.milliJoulesPerPulse()

	return previousProcessing
