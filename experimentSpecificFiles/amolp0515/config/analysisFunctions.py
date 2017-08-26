from pylab import *

def getEBeam(detectorObject,thisEvent):
	temp = detectorObject.get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0


def getPnccdImage(detectorObject,thisEvent):

	myImage = detectorObject.image(thisEvent)
	#print(str(myImage))
	if(myImage is None):
		return 0
	elif(myImage is not  None):
		#print("valid Image")
		x = 1
		return sum(myImage)	#needs from pylab import * so sum is the numpy type as opposed to the built python sum

def genericReturn(detectorObject,thisEvent):
	return detectorObject(thisEvent)

def getRawImage(detectorObject,thisEvent):

	myImage = detectorObject.raw(thisEvent)
	#print(str(myImage))
	if(myImage is None):
		myImage = 0
	elif(myImage is not  None):
		print("valid Image")


	return myImage

def accumulateRawImage(detectorObject,thisEvent,previousProcessing):

	myImage = detectorObject.raw(thisEvent)
	if(myImage is None):
		myImage = 0
	elif(myImage is not  None):
		print("valid Image")

	return (previousProcessing+myImage)
