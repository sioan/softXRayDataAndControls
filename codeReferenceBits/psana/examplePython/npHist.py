from psana import *
import numpy as np
ds = DataSource('exp=xpptut15:run=54:smd')
det = Detector('cspad')

pixel0_vals = []
for nevent,evt in enumerate(ds.events()):
    if nevent>=4: break
    calib_array = det.calib(evt)
    pixel0_vals.append(calib_array[0,0,0])
hist,bin_edges = np.histogram(pixel0_vals,bins=5,range=(-5.0,5.0))

import matplotlib.pyplot as plt
plt.bar(bin_edges[:-1],hist)
plt.show()
