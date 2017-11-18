from pylab import *
import h5py
import psana

myDataSource = psana.MPIDataSource("exp=sxrx22915:run=200:smd")
myEnumeratedEvents = enumerate(myDataSource.events())
for eventNumber,thisEvent in myEnumeratedEvents:
    if eventNumber > 200: break
myPnccdDetectorObject = psana.Detector("pnccd")
f = h5py.File("mySparseImages.h5")



for eventNumber,thisEvent in myEnumeratedEvents:
	if eventNumber > 3000: break
	
	if eventNumber%1000==1:
		print eventNumber                         
		myImage  = myPnccdDetectorObject.image(thisEvent)
		if (None is not myImage):
			f.create_dataset(str(eventNumber), data=array(myImage,dtype=float))

	else: continue

	
