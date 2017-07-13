from psana import *
ds = DataSource('exp=xpptut15:run=54:smd')
evr = Detector('evr0')
for nevent,evt in enumerate(ds.events()):
    if nevent==3: break
    ec = evr.eventCodes(evt)
    if ec is None:
        continue
    print ec
