#run this with: mpirun -n 2 python mpiReduce.py
from psana import *
import numpy as np
ds = DataSource('exp=xpptut15:run=54:smd')
det = Detector('cspad')

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

img = None
for nevent,evt in enumerate(ds.events()):
    if nevent%size!=rank: continue # different ranks look at different events
    if img is None:
        img = det.image(evt).astype(np.double)
    else:
        img += det.image(evt)
    if nevent>=6: break

imgsum = np.empty_like(img)
comm.Reduce(img,imgsum) # sum the image across all ranks
print 'Rank',rank,'sum:',img.sum()
if rank==0: print 'Total sum:',imgsum.sum()

MPI.Finalize()  # important to avoid crashes
