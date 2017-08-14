from pylab import *

myData=loadtxt("subset.csv",skiprows=2,usecols=(3,4,5),delimiter=',')

delayScanRanges = array([[0,21682],[21682,44864],[44864,67638],[67638,88798],[88798,111936],[111936,135092],[135092,158246],[158246,180945],[158246,180945]])

delayScanRanges=vstack([delayScanRanges,array([[180945,204068],[204068,227122],[227122,-1]])])

xEdges = arange(40.0,54.006,(54.006-40.0)/150)	#timing
yEdges = arange(600,900,1)	#intensity apd/gmd

#myData[:,1]/(myData[:,0]+1e-9)

np.histogram2d(myData[:,2],myData[:,1]/(myData[:,0]+1e-9), bins=(xEdges, yEdges))
