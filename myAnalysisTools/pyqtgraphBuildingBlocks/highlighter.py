import sys, os
import numpy as np
import h5py
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

class highlighter(pg.GraphicsLayoutWidget):
	def __init__(self, *args, **kwds):
		pg.GraphicsLayoutWidget.__init__(self, *args, **kwds)

		self.w1 = self.addPlot()
		self.n = 300
		self.s1 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
		self.pos = np.random.normal(size=(2,self.n), scale=1e-5)
		self.spots = [{'pos': self.pos[:,i], 'data': 1} for i in range(self.n)] + [{'pos': [0,0], 'data': 1}]

		self.s1.addPoints(self.spots)
		self.w1.addItem(self.s1)

		self.r1a = pg.ROI([-1e-5,-1e-5], [1e-5,1e-5])
		self.w1.addItem(self.r1a)
		## handles scaling horizontally around center
		self.r1a.addScaleHandle([1, 0.5], [0.5, 0.5])
		self.r1a.addScaleHandle([0, 0.5], [0.5, 0.5])

		self.r1a.addScaleHandle([1, 0.5], [0.5, 0.5])
		self.r1a.addScaleHandle([0, 0.5], [0.5, 0.5])

		## handles scaling vertically from opposite edge
		self.r1a.addScaleHandle([0.5, 0], [0.5, 1])
		self.r1a.addScaleHandle([0.5, 1], [0.5, 0])

		## handles scaling both vertically and horizontally
		self.r1a.addScaleHandle([1, 1], [0, 0])
		self.r1a.addScaleHandle([0, 0], [1, 1])

		self.lastClicked = []

		self.r1a.sigRegionChangeFinished.connect(self.updateROI)

	def updateROI(self,roi):
		for p in self.lastClicked:
			p.resetPen()

		rLim = np.array([[roi.x(),roi.y()],[(roi.size()).x(),(roi.size()).y()]])
		r = np.array([[i.viewPos().x(),i.viewPos().y()] for i in self.s1.points()])

   
		self.r=np.array([0,0])
		self.lastClicked = []
		for i in self.s1.points():
			x = i.viewPos().x()
			y = i.viewPos().y()
			if (x>rLim[0][0] and x <(rLim[0][0]+rLim[1][0])):
				if (y>rLim[0][1] and y <(rLim[0][1]+rLim[1][1])):
					r = np.vstack([r,[x,y]])
					i.setPen('b', width=2)
					self.lastClicked.append(i)

		print(r.shape)
