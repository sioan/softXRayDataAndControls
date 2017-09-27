history
import psana
from pylab import
from pylab import *
myDataSource = psana.MPIDataSource("exp=sxr10116:run=73")
psana.DetNames()
andorDetectorObject = psana.Detector('andor')
myEnumeratedEvents = enumerate(myDataSource.events())
eventNumber,thisEvent = next(myEnumeratedEvents)
andorDetectorObject(thisEvent)
andorDetectorObject.image(thisEvent)
eventNumber,thisEvent = next(myEnumeratedEvents)
andorDetectorObject.image(thisEvent)
eventNumber,thisEvent = next(myEnumeratedEvents)
andorDetectorObject.image(thisEvent)
eventNumber,thisEvent = next(myEnumeratedEvents)
andorDetectorObject.image(thisEvent)
eventNumber,thisEvent = next(myEnumeratedEvents)
andorDetectorObject.image(thisEvent)
eventNumber,thisEvent = next(myEnumeratedEvents)
andorDetectorObject.image(thisEvent)
eventNumber,thisEvent = next(myEnumeratedEvents)
andorDetectorObject.image(thisEvent)
eventNumber,thisEvent = next(myEnumeratedEvents)
zeros([5,5])
if i in enumeratedEvents:
    tempImage = andorDetectorObject.image(thisEvent)
    if(tempImage is not None):
           print i
for i in enumeratedEvents:
    tempImage = andorDetectorObject.image(thisEvent)
    if(tempImage is not None):
           print i
for eventNumber,thisEvent in enumeratedEvents:
    tempImage = andorDetectorObject.image(thisEvent)
    if(tempImage is not None):
           print i
for eventNumber,thisEvent in myEnumeratedEvents:
    tempImage = andorDetectorObject.image(thisEvent)
    if(tempImage is not None):
           print i
for eventNumber,thisEvent in myEnumeratedEvents:
    tempImage = andorDetectorObject.image(thisEvent)
    if(tempImage is not None):
           print eventNumber
history

