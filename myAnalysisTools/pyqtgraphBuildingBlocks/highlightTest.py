import sys, os
import numpy as np
import h5py
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from firstExampleClass import firstExampleClass as fec

from highlighter import highlighter as hl

app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.resize(800,800)	#this is what let's me open the window after it's been closed.
#view = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
view = hl()

mw.setCentralWidget(view)
mw.show()
mw.setWindowTitle('pyqtgraph example: ScatterPlot')

