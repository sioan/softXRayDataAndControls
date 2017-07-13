from psana import *
ds = DataSource('exp=xpptut15:run=54:smd')

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
    if nevent==2: break

# now jump to the events in reverse order
ds = DataSource('exp=xpptut15:run=54:idx')
run = ds.runs().next()
for sec,nsec,fid in zip(reversed(seconds),reversed(nanoseconds),reversed(fiducials)):
    et = EventTime(int((sec<<32)|nsec),fid)
    evt = run.event(et)
    print evt.get(EventId).fiducials()
