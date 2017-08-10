from pylab import *
import h5py
f = h5py.File("sxr10116run73.h5",'r')
#f = h5py.File("sxrx24615run21.h5",'r')
array(f)
#array(f['acqiris2'])
#array(f['acqiris2']).shape
array(f[f.keys()[0]])
array(f['andor']['1'])
