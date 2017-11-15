from pylab import *
from hdf5_to_dict import hdf5_to_dict
from filterMasks import filterMasks

def makeEdges(dScatter,nBins):
	sScatter = sort(dScatter)
	mySize = 0.002*len(dScatter)
	myStart = mean(sScatter[:mySize])-std(sScatter[:mySize])
	myEnd = mean(sScatter[-mySize:])-std(sScatter[-mySize:])
	myRange = myEnd-myStart
	myBins = arange(myStart,myEnd,myRange/nBins)
	return myBins

experimentRunName = "sxri0414run60"
myFile = experimentRunName+".h5"
myHdf5Object = h5py.File("smallHdf5Data/"+myFile)
myDataDict = hdf5_to_dict(myHdf5Object)

xScatter = myDataDict['GMD'][myMask]
yScatter = myDataDict['acqiris2'][myMask]
eScatter = myDataDict['ebeam/photon_energy'][myMask]
tScatter = (2/.3*(myDataDict['delayStage']-myOffset)+timeToolSign*myDataDict['TSS_OPAL/pixelTime']/1000.0)[myMask]

xEdges = makeEdges(xScatter,50) 	#arange(0,0.0012,0.0012/50)	#size 
yEdges = makeEdges(yScatter,50)		#arange(0,1.0,0.9)			#arange(0,0.9,0.9/50)		#size 
eEdges = makeEdges(eScatter,50)		#arange(900,925,25/50.0)	#size
tEdges = makeEdges(tScatter,200)	#arange(min(tScatter),max(tScatter),25/50.0)

toBin = array([yScatter,xScatter,eScatter,tScatter]).transpose()
theEdges = (yEdges,xEdges,eEdges,tEdges)

#myHist,myEdges = histogramdd(toBin,theEdges,weights = yScatter/xScatter)
myHist,myEdges = histogramdd(toBin,theEdges,weights = diag(ones(4)))
