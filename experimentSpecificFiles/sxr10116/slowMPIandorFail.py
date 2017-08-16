from pylab import *
import psana
myDataSource = psana.MPIDataSource("exp=sxr10116:run=73")
smldata = myDataSource.small_data("test.h5")
myEnumeratedEvents = enumerate(myDataSource.events())
andorDetectorObject = psana.Detector('andor')

counter = 0 
while(True):
	
	counter = counter + 1
	if(counter%1000 == 1):
		print counter

	eventNumber,thisEvent = next(myEnumeratedEvents)

	if(andorDetectorObject.image(thisEvent) is not None):
		x = sum(andorDetectorObject.image(thisEvent))


		smldata.event(x)


smldata.close()


