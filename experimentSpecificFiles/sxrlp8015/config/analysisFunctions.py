def getEBeam(detectorObject,thisEvent):
	temp = detectorObject.get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0

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
