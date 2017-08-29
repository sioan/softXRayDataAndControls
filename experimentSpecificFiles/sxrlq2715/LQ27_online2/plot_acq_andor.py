import numpy as np
import matplotlib.pyplot as plt

import psana

from psmon import publish
from psmon.plots import XYPlot, Image

psana.setOption('psana.calib-dir', '/reg/d/psdm/sxr/sxro5916/calib')
ds_str = 'shmem=psana.0:stop=no'
ds = psana.DataSource(ds_str)
I0 = psana.Detector('Acq01')
andor = psana.Detector('andor')
events = ds.events()
evt = events.next()
evt = events.next()
plt.figure()
plt.plot(I0.waveform(evt)[2])
f = plt.figure()
plt.plot(andor.image(evt)[0])
plt.show()


