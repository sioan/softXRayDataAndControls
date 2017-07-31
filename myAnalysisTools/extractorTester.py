from pylab import *
import h5py
f = h5py.File("sxri0414.h5")
array(f)
array(f['acqiris2'])
array(f['acqiris2']).shape

