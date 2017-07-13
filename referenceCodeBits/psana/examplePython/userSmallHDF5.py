import numpy as np
import psana

ds = psana.DataSource('exp=xpptut15:run=54:smd')
cspad = psana.Detector('cspad')

cspad_sums = []
NUMEVENTS = 3
for idx, evt in enumerate(ds.events()):
     if idx >= NUMEVENTS: break
     calib = cspad.calib(evt)
     if calib is None: continue
     cspad_sums.append(np.sum(calib))

import h5py
h5out = h5py.File("userSmallData.h5", 'w')
h5out['cspad_sums'] = cspad_sums
h5out.close()
