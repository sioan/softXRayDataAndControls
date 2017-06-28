from pylab import *
import h5py
f =h5py.File("run104.h5","r")
pulseArea  = list(f['pulseArea'])

