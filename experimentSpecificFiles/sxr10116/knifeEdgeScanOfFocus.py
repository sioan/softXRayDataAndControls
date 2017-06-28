from pylab import *
import psana
from scipy.signal import savgol_filter

dsource = psana.DataSource("exp=sxr10116:run=40")
psana.DetNames()

xRayDiodeDownstreamSampleAcq01=psana.Detector("Acq01")
xSampleAxis = psana.Detector("SXR:RCI:MZM:GRD:x.RBV")
ySampleAxis = psana.Detector("SXR:RCI:MZM:GRD:y.RBV")

enumeratedEvents = enumerate(dsource.events())
eventNumber,myEvent = next(enumeratedEvents)


timeStart,timeEnd = 8800,9400

myTrace = xRayDiodeDownstreamSampleAcq01(myEvent)[0][0]
pulseArea = sum(myTrace[timeStart:timeEnd])
myxPosition = xSampleAxis(myEvent)
myyPosition = ySampleAxis(myEvent)

toSave = array([myxPosition,myyPosition,pulseArea])

for eventNumber,myEvent in enumeratedEvents:
	
	myTrace = xRayDiodeDownstreamSampleAcq01(myEvent)[0][0]
	pulseArea = mean(myTrace[timeStart:timeEnd])-mean(myTrace[0:timeStart])
	myxPosition = xSampleAxis(myEvent)
	myyPosition = ySampleAxis(myEvent)

	temp = [myxPosition,myyPosition,pulseArea]
	toSave = vstack([toSave,temp])

	if(eventNumber%100==1): print eventNumber


