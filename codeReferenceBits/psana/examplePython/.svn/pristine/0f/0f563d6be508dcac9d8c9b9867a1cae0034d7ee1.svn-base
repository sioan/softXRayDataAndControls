from psana import *
ds  = DataSource('exp=xpptut15:run=54:idx') # run online/offline

det = Detector('cspad') # simple detector interface

from mpi4py import MPI # large-scale parallelization
rank = MPI.COMM_WORLD.Get_rank()
size = MPI.COMM_WORLD.Get_size()

img = None
for run in ds.runs():
    times = run.times()
    mylength = len(times)//size
    mytimes= times[rank*mylength:(rank+1)*mylength]
    for n,t in enumerate(mytimes):
        evt = run.event(t) # random access
        if img is None:
            img = det.image(evt) # many complex run-dependent calibrations
        else:
            img += det.image(evt)
        if n>5: break

import numpy as np
img_all = np.empty_like(img)
MPI.COMM_WORLD.Reduce(img,img_all)

if rank==0:
    from pypsalg.AngularIntegrationM import *  # algorithms
    ai = AngularIntegratorM()
    ai.setParameters(img_all.shape[0],img_all.shape[1],
                     mask=np.ones_like(img_all))
    bins,intensity = ai.getRadialHistogramArrays(img_all)

    from psmon import publish # real time plotting
    from psmon.plots import Image
    publish.local = True
    img = Image(0,"CsPad",img_all)
    publish.send('image',img)

MPI.Finalize()
