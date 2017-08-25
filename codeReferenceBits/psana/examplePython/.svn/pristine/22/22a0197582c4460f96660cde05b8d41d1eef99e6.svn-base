from psana import *
ds = DataSource('exp=xpptut15:run=59:smd')

ebeamDet = Detector('EBeam')

for nevent,evt in enumerate(ds.events()):
    ebeam = ebeamDet.get(evt)
    if ebeam is None: continue
    print ebeam.ebeamPhotonEnergy()
    break
