# -*- coding: utf-8 -*-
"""
Example demonstrating a variety of scatter plot features.
"""



## Add path to library (just for examples; you do not need this)
#import initExample

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

## Make all plots clickable  This is relying on global variables.  Makes code order matter.
## need to find way to suppress this.
lastClicked = []
def clicked(plot, points):
    global lastClicked
    for p in lastClicked:
        p.resetPen()
		#print("test")
    #print("clicked points", points)

    for p in points:
        p.setPen('b', width=2)
        print(p.viewPos())

    lastClicked = points




app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.resize(800,800)
view = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
mw.setCentralWidget(view)
mw.show()
mw.setWindowTitle('pyqtgraph example: ScatterPlot')

## create four areas to add plots
w1 = view.addPlot()

print("Generating data, this takes a few seconds...")

## There are a few different ways we can draw scatter plots; each is optimized for different types of data:


## 1) All spots identical and transform-invariant (top-left plot). 
## In this case we can get a huge performance boost by pre-rendering the spot 
## image and just drawing that image repeatedly.

n = 300
s1 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
pos = np.random.normal(size=(2,n), scale=1e-5)
spots = [{'pos': pos[:,i], 'data': 1} for i in range(n)] + [{'pos': [0,0], 'data': 1}]
s1.addPoints(spots)
w1.addItem(s1)
s1.sigClicked.connect(clicked)

##################################################
################add ROI###########################

r1a = pg.ROI([-1e-5,-1e-5], [1e-5,1e-5])
w1.addItem(r1a)
## handles scaling horizontally around center
r1a.addScaleHandle([1, 0.5], [0.5, 0.5])
r1a.addScaleHandle([0, 0.5], [0.5, 0.5])

## handles scaling vertically from opposite edge
r1a.addScaleHandle([0.5, 0], [0.5, 1])
r1a.addScaleHandle([0.5, 1], [0.5, 0])

## handles scaling both vertically and horizontally
r1a.addScaleHandle([1, 1], [0, 0])
r1a.addScaleHandle([0, 0], [1, 1])

def updateROI(roi):
    global lastClicked
    for p in lastClicked:
        p.resetPen()

    #print("[{},{}],[{},{}]".format(roi.x(),roi.y(),(roi.size()).x(),(roi.size()).y()))
    #r = np.array([roi.x(),roi.y()],[(roi.size()).x(),(roi.size()).y()])
    rLim = np.array([[roi.x(),roi.y()],[(roi.size()).x(),(roi.size()).y()]])
    r = np.array([[i.viewPos().x(),i.viewPos().y()] for i in s1.points()])

    #myMask = np.array([(i>rLim[0][0])for i in r[:,0]])
    #r = r[myMask] 

    #myMask = np.array([(i>rLim[0][1])for i in r[:,1]])
    #r = r[myMask] 

    #myMask = np.array([(i<rLim[0][0]+rLim[1][0])for i in r[:,0]])
    #r = r[myMask] 

    #myMask = np.array([(i<rLim[0][1]+rLim[1][1])for i in r[:,1]])
    #r = r[myMask] 

    r=np.array([0,0])
    lastClicked = []
    for i in s1.points():
        x = i.viewPos().x()
        y = i.viewPos().y()
        if (x>rLim[0][0] and x <(rLim[0][0]+rLim[1][0])):
            if (y>rLim[0][1] and y <(rLim[0][1]+rLim[1][1])):
                r = np.vstack([r,[x,y]])
                i.setPen('b', width=2)
                lastClicked.append(i)

    print(r.shape)

#
 		#print("test")
    #print("clicked points", points)

#    for p in points:
#       p.setPen('b', width=2)
#       print(p.viewPos())

    #lastClicked = s1.points


    return 

r1a.sigRegionChangeFinished.connect(updateROI)

###################################################

## 2) Spots are transform-invariant, but not identical (top-right plot). 
## In this case, drawing is almsot as fast as 1), but there is more startup 
## overhead and memory usage since each spot generates its own pre-rendered 
## image.



## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


