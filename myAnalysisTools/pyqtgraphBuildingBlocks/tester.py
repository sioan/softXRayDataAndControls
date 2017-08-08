import sys, os
import numpy as np
import h5py
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from firstExampleClass import firstExampleClass as fec

pg.mkQApp()


plt = pg.plot()
plt.setWindowTitle('pyqtgraph example: HDF5 big data')
plt.enableAutoRange(False, False)
plt.setXRange(0, 500)

curve = fec()
#curve.setHDF5(f['data'])
plt.addItem(curve)

