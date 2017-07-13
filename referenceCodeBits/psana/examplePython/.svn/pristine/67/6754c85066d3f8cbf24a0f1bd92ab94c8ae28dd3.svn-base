import numpy as np
import math
import psana
import h5py
 
LASER_ON_EVR_CODE = 92

NUM_EVENTS = 10
 
ds = psana.DataSource('exp=xpptut15:run=54:smd')
 
chunkSizeSmallData = 2048

h5out = h5py.File("saved_data_for_xpptut15_run54_cspad_hproj.h5", 'w')
eventDataGroup = h5out.create_group('EventData')
evtSecDs = eventDataGroup.create_dataset('event_seconds',
  (0,), dtype='i4', chunks=(chunkSizeSmallData,), maxshape=(None,))
evtNanoDs = eventDataGroup.create_dataset('event_nanoseconds',
  (0,), dtype='i4', chunks=(chunkSizeSmallData,), maxshape=(None,))
evtFiducialsDs = eventDataGroup.create_dataset('event_fiducials',
  (0,), dtype='i4', chunks=(chunkSizeSmallData,), maxshape=(None,))
ebeamL3Ds = eventDataGroup.create_dataset('ebeam_L3',
  (0,), dtype='f4', chunks=(chunkSizeSmallData,), maxshape=(None,))
laserOnDs = eventDataGroup.create_dataset('laser_on',
  (0,), dtype='i1', chunks=(chunkSizeSmallData,), maxshape=(None,))
cspadHprojDs = None # will create once we see first cspad and know dimensions
 
cspad = psana.Detector('cspad')

nextDsIdx = -1
for evtIdx, evt in enumerate(ds.events()):
  if evtIdx >= NUM_EVENTS:
    break
  eventId = evt.get(psana.EventId)
  evr = evt.get(psana.EvrData.DataV4, psana.Source('evr0'))
  ebeam = evt.get(psana.Bld.BldDataEBeamV7, psana.Source('EBeam'))

  cspadImage = cspad.image(evt)
 
  # check for event that has everything we want to write
  if (cspadImage is None) or (eventId is None) or \
     (evr is None) or (ebeam is None):
    continue

  hproj = np.sum(cspadImage,0)

  if cspadHprojDs is None:
    mbPerEvent = (len(hproj) * hproj.dtype.itemsize)/float(1<<20)
    targetChunkMb = 16.0
    chunkSize = min(2048, max(1,int(math.floor(targetChunkMb/mbPerEvent))))
    cspadHprojDs = eventDataGroup.create_dataset('cspad_hproj',
                                                 (0,len(hproj)), dtype=cspadImage.dtype,
                                                 chunks=(chunkSize,len(hproj)),
                                                 maxshape=(None,len(hproj)),
                                                 compression='gzip',
                                                 compression_opts=1)

  nextDsIdx += 1
 
  evtSecDs.resize((nextDsIdx+1,))
  evtNanoDs.resize((nextDsIdx+1,))
  evtFiducialsDs.resize((nextDsIdx+1,))
  ebeamL3Ds.resize((nextDsIdx+1,))
  laserOnDs.resize((nextDsIdx+1,))
  cspadHprojDs.resize((nextDsIdx+1,len(hproj)))

  evtSecDs[nextDsIdx] = eventId.time()[0]
  evtNanoDs[nextDsIdx] = eventId.time()[1]
  evtFiducialsDs[nextDsIdx] = eventId.fiducials()
  ebeamL3Ds[nextDsIdx] = ebeam.ebeamL3Energy()
  laserOnDs[nextDsIdx] = evr.present(LASER_ON_EVR_CODE)
  cspadHprojDs[nextDsIdx,:] = hproj
 
summaryGroup = h5out.create_group('Summary')
summaryGroup.create_dataset('l3average', data = np.average(ebeamL3Ds[:]))
h5out.close()
