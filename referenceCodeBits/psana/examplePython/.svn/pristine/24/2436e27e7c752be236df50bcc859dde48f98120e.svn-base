from psana import *
import numpy as np
ds = DataSource('exp=xpptut15:run=54:smd')
det = Detector('cspad')
for nevent,evt in enumerate(ds.events()):
    calib_array = det.calib(evt)
    np.savetxt('ndarray.txt',calib_array.reshape((-1)))
    break
