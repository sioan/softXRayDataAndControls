import psana
import numpy as np
for i in np.arange(3):
	print(i)


##############################
####this is command line######
#`which mpirun` --oversubscribe -H daq-amo-mon02,daq-amo-mon03,daq-amo-mon04,daq-amo-mon05,daq-amo-mon06 -n 4 ./counter.sh
