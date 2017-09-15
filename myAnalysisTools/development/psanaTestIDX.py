#from pylab import *
from psana import *
#myExperiment = 'exp=xpptut15:run=54'
myExperiment = 'exp=sxrx22915:run=28'
ds = DataSource(myExperiment+':smd')
# LCLS uses 3 numbers to define an event.  In LCLS2 this will be one number.
seconds     = []
nanoseconds = []
fiducials   = []
 
# get some times of events (these could come from a saved "small data" file, for example)
for nevent,evt in enumerate(ds.events()):
	evtId = evt.get(EventId)
	seconds.append(evtId.time()[0])
	nanoseconds.append(evtId.time()[1])
	fiducials.append(evtId.fiducials())
	if nevent==200: break
	if (1==nevent%50):
		print nevent

print("going backwards")
# now that we have the times, jump to the events in reverse order
ds = DataSource(myExperiment+':idx')
run = ds.runs().next()

zippedTimes = zip(reversed(seconds),reversed(nanoseconds),reversed(fiducials))

for sec,nsec,fid in zippedTimes:
	et = EventTime(int((sec<<32)|nsec),fid)
	evt = run.event(et)
	if None == evt:
		continue
	print evt.get(EventId).fiducials()
