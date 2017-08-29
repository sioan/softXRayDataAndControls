# run these commands in the "amoh1315" directory

# mpirun -n 2 python mpi_driver.py  exp=xpptut15:run=54 cspad -n 10
# in batch:
# bsub -q psanaq -n 2 -o %J.log -a mympi python mpi_driver.py exp=xpptut15:run=54

from master import runmaster
from client import runclient
import signal

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
assert size>1, 'At least 2 MPI ranks required'
numClients = size-1

import cfg

# Catch ctrl-C
def signal_handler(signal, fame):
    print 'Correlation plotting terminated.'
    sys.exit()
signal.signal(signal.SIGINT, signal_handler)

cfg = cfg.get_cfg()

if rank==0:
    runmaster(numClients, cfg)
else:
    runclient(cfg)

MPI.Finalize()
