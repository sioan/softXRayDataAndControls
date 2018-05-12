import psana
#from mpi4py import MPI
import os

ds=psana.DataSource('shmem=psana.0:stop=no')


import numpy as np
os.system("hostname")
for i in np.arange(3):
	print(i)


##############################
####this is command line######
#`which mpirun` --oversubscribe -H daq-amo-mon03,daq-amo-mon04,daq-amo-mon05,daq-amo-mon06 -n 4 ./counter.sh
