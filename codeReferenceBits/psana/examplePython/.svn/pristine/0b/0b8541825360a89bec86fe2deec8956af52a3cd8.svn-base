import numpy as np
from mpi4py import MPI
import math
import psana
import h5py
import time

startTime = time.time()

ds = psana.DataSource('exp=xpptut15:run=54:smd')
 
def hasCspad(evt, aliasMap):
    for key in evt.keys():
        if 'cspad' == aliasMap.alias(key.src()):
            return True
    return False
 
LASER_ON_EVR_CODE = 92
CSPAD_HPROJ_LEN = 1738
NUM_EVENTS = 120  # set to non-zero to stop early
RESIZE_GROW = 100  # how many events between collective resizes

currentDsetSize = 0
numResizes=0
 
chunkSizeSmallData = 2048

h5out = h5py.File("saved_data_for_xpptut15_run54_cspad_hproj.h5", 'w',
                  driver='mpio', comm=MPI.COMM_WORLD)
eventDataGroup = h5out.create_group('EventData')
evtSecDs = eventDataGroup.create_dataset('event_seconds',
  (currentDsetSize,), dtype='i4', chunks=(chunkSizeSmallData,), maxshape=(None,))
evtNanoDs = eventDataGroup.create_dataset('event_nanoseconds',
  (currentDsetSize,), dtype='i4', chunks=(chunkSizeSmallData,), maxshape=(None,))
evtFiducialsDs = eventDataGroup.create_dataset('event_fiducials',
  (currentDsetSize,), dtype='i4', chunks=(chunkSizeSmallData,), maxshape=(None,))
ebeamL3Ds = eventDataGroup.create_dataset('ebeam_L3',
  (currentDsetSize,), dtype='f4', chunks=(chunkSizeSmallData,), maxshape=(None,))
laserOnDs = eventDataGroup.create_dataset('laser_on',
  (currentDsetSize,), dtype='i1', chunks=(chunkSizeSmallData,), maxshape=(None,))
cspadHprojDs = eventDataGroup.create_dataset('cspadHproj',
                          (currentDsetSize,CSPAD_HPROJ_LEN), dtype='f4', 
                          chunks=(2000,CSPAD_HPROJ_LEN), maxshape=(None, CSPAD_HPROJ_LEN))
 
cspad = psana.Detector('cspad')
evr = psana.Detector('evr0')
ebeamdet = psana.Detector('EBeam')
 
histogram_bin_edges = [-500, -400, -200, -150, -100, -50, -25, 0, 5, 10, 15, 20, 25, 50, 100, 200, 500]
local_cspad_histogram = np.zeros((len(histogram_bin_edges)-1,), np.int64)

timeResize = 0.0
timeWriting = 0.0

 
nextDsIdx = -1
for evtIdx, evt in enumerate(ds.events()):
  if NUM_EVENTS > 0 and evtIdx >= NUM_EVENTS:
    break
  eventId = evt.get(psana.EventId)
  ecodes = evr.eventCodes(evt)
  ebeam = ebeamdet.get(evt)
 
  # check for event that has everything we want to write
  if (eventId is None) or (ecodes is None) or (ebeam is None) or \
     (not hasCspad(evt, ds.env().aliasMap())):
    continue

  nextDsIdx += 1
  
  if (nextDsIdx >= currentDsetSize):
    t0 = time.time()
    # collectively resize all the chunked datasets
    currentDsetSize += RESIZE_GROW
    numResizes += 1
    MPI.COMM_WORLD.Barrier()
    evtSecDs.resize((nextDsIdx+RESIZE_GROW,))
    evtNanoDs.resize((nextDsIdx+RESIZE_GROW,))
    evtFiducialsDs.resize((nextDsIdx+RESIZE_GROW,))
    ebeamL3Ds.resize((nextDsIdx+RESIZE_GROW,))
    laserOnDs.resize((nextDsIdx+RESIZE_GROW,))
    cspadHprojDs.resize((nextDsIdx+RESIZE_GROW,CSPAD_HPROJ_LEN))
    timeResize += time.time()-t0

  # only process this ranks events
  if nextDsIdx % MPI.COMM_WORLD.Get_size() != MPI.COMM_WORLD.Get_rank():
    continue
  t0 = time.time()
  # expensive per rank processing:
  cspadImage = cspad.image(evt)
  local_cspad_histogram += np.histogram(cspad.calib(evt), 
                               histogram_bin_edges)[0]
  cspadHproj = np.sum(cspadImage, 0)
 

  evtSecDs[nextDsIdx] = eventId.time()[0]
  evtNanoDs[nextDsIdx] = eventId.time()[1]
  evtFiducialsDs[nextDsIdx] = eventId.fiducials()
  ebeamL3Ds[nextDsIdx] = ebeam.ebeamL3Energy()
  laserOnDs[nextDsIdx] = LASER_ON_EVR_CODE in ecodes
  cspadHprojDs[nextDsIdx,:] = cspadHproj
  timeWriting += time.time()-t0

## finished processing, collectively form summary
# datasets, and get final historgram
summaryGroup = h5out.create_group('Summary')
summaryGroup.create_dataset('cspad_histogram_bins', 
                                data = histogram_bin_edges)
finalHistDs = summaryGroup.create_dataset('cspad_histogram_values', 
                             (len(local_cspad_histogram),), dtype='i8')
 
if MPI.COMM_WORLD.Get_rank()==0:
    finalHistogram = np.zeros_like(local_cspad_histogram)
    MPI.COMM_WORLD.Reduce(sendbuf=[local_cspad_histogram, MPI.INT64_T],
                          recvbuf=[finalHistogram, MPI.INT64_T],
                          op=MPI.SUM, root=0)
    finalHistDs[:] = local_cspad_histogram[:]
else:
    MPI.COMM_WORLD.Reduce(sendbuf=[local_cspad_histogram, MPI.INT64_T],
                          recvbuf=[None, MPI.INT64_T],
                          op=MPI.SUM, root=0)
     
h5out.close()

totalTime = time.time()-startTime
hz = evtIdx/totalTime
print "rnk=%3d evts=%4d time=%.2f resizes=%d time_per_resize=%.2f writing=%.2f Hz=%.2f" % \
    (MPI.COMM_WORLD.Get_rank(), evtIdx, totalTime, numResizes, timeResize/float(numResizes), timeWriting, hz)
