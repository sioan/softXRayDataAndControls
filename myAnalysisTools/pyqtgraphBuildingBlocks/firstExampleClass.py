import sys, os
import numpy as np
import h5py
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

class firstExampleClass(pg.PlotCurveItem):
	def __init__(self, *args, **kwds):
		self.data = np.random.normal(size=1000)
		pg.PlotCurveItem.__init__(self, *args, **kwds)
		self.setData(self.data) # update the plot
