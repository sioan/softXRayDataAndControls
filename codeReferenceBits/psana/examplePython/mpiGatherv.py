from psana import *
import numpy as np

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

ds = DataSource("exp=xpptut15:run=54:smd")
det = Detector('cspad')

intensities = []   # use a list instead of array because faster to append
for nevent,evt in enumerate(ds.events()):
    if nevent==5: break
    if nevent%size!=rank: continue
    intensities.append(det.raw(evt).sum())

# real Gatherv logic starts here

lengths = np.array(comm.gather(len(intensities))) # get list of lengths
mysend = np.array(intensities)
print 'Rank',rank,'sending',mysend
myrecv = None
if rank==0:
    myrecv = np.empty((sum(lengths)),mysend.dtype) # allocate receive buffer

comm.Gatherv(sendbuf=mysend, recvbuf=[myrecv, lengths])

if rank==0:
    start = 0
    # look in the receive buffer for the contribution from each rank
    for r,mylen in enumerate(lengths):
        print 'Rank 0 received',myrecv[start:start+mylen],'from rank',r
        start += mylen
