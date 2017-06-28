from pylab import *
import psana

dsource = psana.DataSource("exp=sxr10116:run=24")
psana.DetNames()

exitSlitOpal=psana.Detector("EXS_OPAL")
getEnergy = psana.Detector("SIOC:SYS0:ML00:AO627")


enumeratedEvents = enumerate(dsource.events())

eventNumber,myEvent = next(enumeratedEvents)

myImage = exitSlitOpal.image(myEvent)
myEnergy = getEnergy(myEvent)

monoExitSlitYagSpectrum = sum(myImage,axis=1)
myEnergyList = array([myEnergy])


for eventNumber,myEvent in enumeratedEvents:
	
	#myImage = exitSlitOpal.image(myEvent)
	myEnergy = getEnergy(myEvent)

	#monoExitSlitYagSpectrum = vstack([monoExitSlitYagSpectrum,sum(myImage,axis=1)])
	myEnergyList = append(myEnergyList,myEnergy)

	
	#print eventNumber


