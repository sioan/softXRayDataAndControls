# run these commands in the "amoh1315" directory

# mpirun -n 2 python mpi_driver.py  exp=xpptut15:run=54 cspad -n 10
# in batch:
# bsub -q psanaq -n 2 -o %J.log -a mympi python mpi_driver.py exp=xpptut15:run=54

from MCP_Master import runmaster
from MCP_Client import runclient

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
assert size>1, 'At least 2 MPI ranks required'
numClients = size-1

import argparse
import ConfigParser
parser = argparse.ArgumentParser()
parser.add_argument("-r","--run", help="run number from DAQ")
parser.add_argument("-n","--noe",help="number of events, all events=0",default=-1, type=int)
parser.add_argument("-d","--delay",help="expected delay, in ns",default=1.0, type=float)

args = parser.parse_args()

# parse config file
pars = {}
#pars['updateEvents'] = config.getint('Update','updateEvents')
pars['updateEvents'] = 10
pars['live'] = 0
pars['expName'] = 'sxrm2316'

if rank==0:
    runmaster(numClients,pars,args)
else:
    runclient(args,pars)

MPI.Finalize()
