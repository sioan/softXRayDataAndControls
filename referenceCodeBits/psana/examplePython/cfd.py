from psana import *
from pypsalg import find_edges
ds = DataSource('exp=amotut13:run=206')
det = Detector('AmoETOF.0:Acqiris.0')

for nevent,evt in enumerate(ds.events()):
    waveforms,times = det.raw(evt)
    # find edges for channel 0
    # parameters: baseline, threshold, fraction, deadtime, leading_edges
    edges = find_edges(waveforms[0],0.0,-0.05,1.0,5.0,True)
    # pairs of (amplitude,sampleNumber)
    print edges
    break

import matplotlib.pyplot as plt
plt.plot(waveforms[0])
plt.show()
