import h5py
from pylab import *
f = h5py.File("amox25715run22.h5")
f['VMI/peakCoordinate']
r = array(f['VMI/peakCoordinate'])[20]
myList
myList = []
f.visit(myList.append)
f
history
myList
history

