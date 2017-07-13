import numpy as np
import psana
import h5py
 
NUM_EVENTS_TO_WRITE=3
 
ds = psana.DataSource('exp=xpptut15:run=54:smd')
 
h5out = h5py.File("userLargeData.h5", 'w')
smallDataSet = h5out.create_dataset('cspad_sums',(0,), dtype='f8', 
                                    chunks=(2048,), maxshape=(None,))
largeDataSet = h5out.create_dataset('cspads',(0,32,185,388), dtype='f4', 
                                    chunks=(12,32,185,388), 
                                    maxshape=(None,32,185,388))

cspad = psana.Detector('cspad')
 
for idx, evt in enumerate(ds.events()):
    if idx > NUM_EVENTS_TO_WRITE: break
    calib = cspad.calib(evt)
    if calib is None: continue
    smallDataSet.resize((idx+1,))
    largeDataSet.resize((idx+1,32,185,388))
    smallDataSet[idx] = np.sum(calib)
    largeDataSet[idx,:] = calib[:]    
 
h5out.close()
