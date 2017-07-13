#run this with: mpirun -n 2 python mpiGather.py
from psana import *
import numpy as np
ds = DataSource('exp=xpptut15:run=54:smd')
det = Detector('cspad')

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

intensity = []
for nevent,evt in enumerate(ds.events()):
    if nevent%size!=rank: continue # different ranks look at different events
    img = det.image(evt)
    intensity.append(img.sum())
    if nevent>=3: break

allIntensities = comm.gather(intensity) # get intensities from all ranks
if rank==0:
    allIntensities = np.concatenate((allIntensities[:])) # put in one long list
    print allIntensities

MPI.Finalize()
