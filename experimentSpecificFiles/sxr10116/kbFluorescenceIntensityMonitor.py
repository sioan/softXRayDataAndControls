from pylab import *
import psana

dsource = psana.DataSource("exp=sxr10116:run=3")
psana.DetNames()

kbFluorescenceMontior=psana.Detector("Acq02")
FEEGasDetEnergyDetector  = psana.Detector('FEEGasDetEnergy')
GasAttenuator  = psana.Detector('GATT:FEE1:310:R_ACT')

#xSampleAxis = psana.Detector("SXR:RCI:MZM:SMP:x.RBV")

enumeratedEvents = enumerate(dsource.events())
eventNumber,myEvent = next(enumeratedEvents)

attenuation = GasAttenuator(myEvent)
dummy,PD1,PD2,MCP = kbFluorescenceMontior(myEvent)[0]

FEEGasDetEnergy = FEEGasDetEnergyDetector.get(myEvent)
FEEGasDetEnergy_f_11_ENC = FEEGasDetEnergy.f_11_ENRC()
FEEGasDetEnergy_f_12_ENC = FEEGasDetEnergy.f_12_ENRC()
FEEGasDetEnergy_f_21_ENC = FEEGasDetEnergy.f_21_ENRC()
FEEGasDetEnergy_f_22_ENC = FEEGasDetEnergy.f_22_ENRC()

timeStart,timeEnd = 1160,2700

pulseArea = sum(MCP[timeStart:timeEnd])

toSave = array([pulseArea,attenuation,FEEGasDetEnergy_f_11_ENC,FEEGasDetEnergy_f_12_ENC,FEEGasDetEnergy_f_21_ENC,FEEGasDetEnergy_f_22_ENC])

for eventNumber,myEvent in enumeratedEvents:
	
	

	attenuation = GasAttenuator(myEvent)
	dummy,PD1,PD2,MCP = kbFluorescenceMontior(myEvent)[0]

	FEEGasDetEnergy = FEEGasDetEnergyDetector.get(myEvent)
	FEEGasDetEnergy_f_11_ENC = FEEGasDetEnergy.f_11_ENRC()
	FEEGasDetEnergy_f_12_ENC = FEEGasDetEnergy.f_12_ENRC()
	FEEGasDetEnergy_f_21_ENC = FEEGasDetEnergy.f_21_ENRC()
	FEEGasDetEnergy_f_22_ENC = FEEGasDetEnergy.f_22_ENRC()

	pulseArea = sum(MCP[timeStart:timeEnd])

	temp = array([pulseArea,attenuation,FEEGasDetEnergy_f_11_ENC,FEEGasDetEnergy_f_12_ENC,FEEGasDetEnergy_f_21_ENC,FEEGasDetEnergy_f_22_ENC])
	toSave = vstack([toSave,temp])


	#print eventNumber

savetxt("sxr10116Run3.txt")


