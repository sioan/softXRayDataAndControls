eventNumber,myEvent = next(enumeratedEvents)


#FEEGasDetEnergy = FEEGasDetEnergyDetector.get(myEvent)
#FEEGasDetEnergy_f_11_ENC = FEEGasDetEnergy.f_11_ENRC()
#FEEGasDetEnergy_f_12_ENC = FEEGasDetEnergy.f_12_ENRC()
#FEEGasDetEnergy_f_21_ENC = FEEGasDetEnergy.f_21_ENRC()
#FEEGasDetEnergy_f_22_ENC = FEEGasDetEnergy.f_22_ENRC()

myImage = imagingDetectorObject.image(myEvent)

#if any([None is k for k in [kbFluorescenceMontior(myEvent),myImage]]):
	#print '*** bad event',nevt
	#continue

MCP = kbFluorescenceMontior(myEvent)[0][3]



pulseArea = sum(MCP[timeStart:timeEnd]-mean(MCP[:1100]))
myFiducials = myEvent.get(psana.EventId).fiducials()


referenceRoiIntensity = np.sum(myImage[420:560,1030:1185])	#could be these values [420:560,80:230] instead 

myCounter = myCounter + 1

myDictionary = {}
myDictionary["pulseArea"] = pulseArea
myDictionary["fiducials"] = myFiducials
myDictionary["referenceRoiIntensity"] = referenceRoiIntensity
myDictionary["testCounter"] = myCounter
myDictionary["eventNumber"] = eventNumber

subplot(211)
imshow(myImage)
subplot(212)
plot(MCP)
print eventNumber
print myDictionary
show()

#smldata.event(myDictionary)
if (eventNumber%100 == 0):
	print eventNumber
