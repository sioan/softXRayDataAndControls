from pylab import *
import psana


#Live data during beamtime
#dsource = psana.MPIDataSource('exp=sxr22915:run=104:smd:dir=/reg/d/ffb/sxr/sxro5916/xtc:live')
#After beamtime
dsource = psana.MPIDataSource("exp=sxrx22915:run=104:smd")

#smldata = dsource.small_data('run104.h5')
smldata = dsource.small_data('run104c.h5')
f = open("manualWriteRun104.dat","w")
psana.DetNames()

kbFluorescenceMontior=psana.Detector("Acq02")
imagingDetectorObject = psana.Detector("pnccd")

#xSampleAxis = psana.Detector("SXR:RCI:MZM:SMP:x.RBV")

enumeratedEvents = enumerate(dsource.events())
eventNumber,myEvent = next(enumeratedEvents)

MCP = kbFluorescenceMontior(myEvent)[0][3]

myImage = imagingDetectorObject.image(myEvent)
referenceRoiIntensity = np.sum(myImage[420:560,1030:1185])	#could be these values [420:560,80:230] instead 

timeStart,timeEnd = [1130,1250]

pulseArea = sum(MCP[timeStart:timeEnd])
myFiducials = myEvent.get(psana.EventId).fiducials()

toSave = array([pulseArea,referenceRoiIntensity])
toSaveAcquiris= MCP[timeStart:timeEnd]

myCounter = 0
for eventNumber,myEvent in enumeratedEvents:
	#if eventNumber > 790:
	#	break
	
	#FEEGasDetEnergy = FEEGasDetEnergyDetector.get(myEvent)
	#FEEGasDetEnergy_f_11_ENC = FEEGasDetEnergy.f_11_ENRC()
	#FEEGasDetEnergy_f_12_ENC = FEEGasDetEnergy.f_12_ENRC()
	#FEEGasDetEnergy_f_21_ENC = FEEGasDetEnergy.f_21_ENRC()
	#FEEGasDetEnergy_f_22_ENC = FEEGasDetEnergy.f_22_ENRC()
	
	myImage = imagingDetectorObject.image(myEvent)
	MCP = kbFluorescenceMontior(myEvent)[0][3]

	if any([None is k for k in [kbFluorescenceMontior(myEvent),myImage]]):
		print '*** bad event',nevt
		continue





	pulseArea = sum(MCP[timeStart:timeEnd]-mean(MCP[:1100]))
	myFiducials = myEvent.get(psana.EventId).fiducials()

	
	referenceRoiIntensity = np.sum(myImage[420:560,1030:1185])	#could be these values [420:560,80:230] instead 

	myCounter = myCounter + 1

	myDictionary = {}
	myDictionary["pulseArea"] = pulseArea
	#myDictionary["fiducials"] = myFiducials
	myDictionary["referenceRoiIntensity"] = referenceRoiIntensity
	#myDictionary["testCounter"] = myCounter
	#myDictionary["eventNumber"] = eventNumber

	smldata.event(myDictionary)
	if (eventNumber%100 == 0):
		print eventNumber
		print myDictionary

	myString = str(eventNumber)+"	"+str(pulseArea)+"	"+str(referenceRoiIntensity)+"\n"
	f.writelines(myString)
	#temp = array([pulseArea,referenceRoiIntensity,myFiducials])
	#temp = array([pulseArea,attenuation,myFiducials,referenceRoiIntensity])
	#toSave = vstack([toSave,temp])
	#toSaveAcquiris=vstack([toSaveAcquiris,MCP[timeStart:timeEnd]])
	#toSaveAcquirisi0=vstack([toSaveAcquirisi0,i0mcp[timeStart:timeEnd]])


smldata.save()
smldata.close()
