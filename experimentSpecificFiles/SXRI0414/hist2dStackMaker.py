from pylab import *
from scipy.interpolate import interp1d
import h5py

from dataAnalysisFlowWorking import *


if __name__ == '__main__':


	
	#####################
	###load file#########

	f = h5py.File("sxri0414run60.h5",'r')
	array(f)

	###########################
	###convert to dict#########
	myDict = hdf5_to_dict(f)
	#filter master with graphical interactive tool
	#remove stuff not meaningful
	#filter on by kicks
	print("loading mask")
	myMask = loadtxt("myMask.dat")
	myMask = myMask.astype(bool)

	print("defining bin sizes")
	nAcqirisBins = 101
	acqMax = 0.65
	acqirisEdges = arange(0,acqMax,acqMax/nAcqirisBins)
	
	nGmdBins = 100	
	gmdEdges = arange(0,.0014,.0014/nGmdBins)
	my2dHist = histogram2d(myDict['acqiris2'],myDict['GMD'],bins=[acqirisEdges,gmdEdges])

	#imshow(my2dHist[0][::-1,:],cmap='magma',clim=(0,500))

	myMax = max(array(f['delayStage']))
	myMin = min(array(f['delayStage']))
	#delayScanStep = (myMax - myMin)/100.0
	delayScanStep = .015

	delayScanRange = arange(myMin,myMax,delayScanStep)

	#######
	#scanRanges = [24845,49568,74291,99013,123736,148459,173182,197905,222627,247350]
	print("loading glu mask")

	myMask = loadtxt("myMask.dat")
	myMask = myMask.astype(bool)

	isEven=0
	tempMask = array([bool(j%2+isEven) for j in array(f['fiducials']) ])
	myMask=myMask*tempMask

	mySize = len(f['acqiris2'][myMask])
	################################################
	##### note mySubset is 
	mySubset = array([f['acqiris2'][myMask],f['GMD'][myMask],f['delayStage'][myMask]])
	
	myData = [0,0,0]
	
	exportedImageStack = h5py.File('run60ImageStack.h5', 'w')

	for i in arange(myMin,myMax,delayScanStep):
		print(str(i))
		acqirisSubSet = array([mySubset[0,j] for j in arange(mySize) if ((mySubset[2][j] < i+delayScanStep) and (mySubset[2][j] > i))])
		gmdSubSet = array([mySubset[1,j] for j in arange(mySize) if ((mySubset[2][j] < i+delayScanStep) and (mySubset[2][j] > i))])
		#x = array([j for j in arange(mySize) if ((mySubset[2][j] < i+delayScanStep) and (mySubset[2][j] > i))])
		#x = array([j for j in arange(mySize) if ((mySubset[2][j] < 50) and (mySubset[2][j] > 49.8))])
		
		my2dHist = histogram2d(acqirisSubSet,gmdSubSet,bins=[acqirisEdges,gmdEdges])
	
		exportedImageStack.create_dataset(str('delayStage'+str(i)), data=my2dHist[0], chunks=True, maxshape=(None,None,))
		


	exportedImageStack.close()










