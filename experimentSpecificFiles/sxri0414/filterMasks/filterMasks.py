from pylab import *

def sxri0414run60(myDict):
	#myMask = myMask.astype(bool)
	myMask = ones(len(myDict['acqiris2'])).astype(bool)
	myMask = myMask * (myDict['TSS_OPAL']['pixelTime']>0)	#excluding bad time tool data
	myMask = myMask * (myDict['acqiris2']>0.002)	#excluding bad acqiris data
	myMask = myMask * (myDict['acqiris2']<0.75)	#excluding bad acqiris data
	myMask = myMask * (myDict['GMD']>0.00001)	#excluding bad gmd data
	myMask = myMask * (myDict['GMD']<0.001)	#excluding bad gmd data
	myMask = myMask * (myDict['evr']['code_162']==0)
	myMask = myMask * (myDict['TSS_OPAL']['positionFWHM']<50)
	myMask = myMask * (myDict['TSS_OPAL']['positionFWHM']>10)
	myMask = myMask * (myDict['ebeam']['photon_energy']>900)
	myMask = myMask * (myDict['ebeam']['photon_energy']<930)
	#myMask = myMask * (myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (myDict['gas_detector']['f_11_ENRC']>1)

	return myMask

def sxri0414run63(myDict):
	#myMask = myMask.astype(bool)
	myMask = ones(len(myDict['acqiris2'])).astype(bool)
	myMask = myMask * (myDict['TSS_OPAL']['pixelTime']>0)	#excluding bad time tool data
	myMask = myMask * (myDict['acqiris2']>0.002)	#excluding bad acqiris data
	myMask = myMask * (myDict['acqiris2']<0.75)	#excluding bad acqiris data
	myMask = myMask * (myDict['GMD']>0.00001)	#excluding bad gmd data
	myMask = myMask * (myDict['GMD']<0.001)	#excluding bad gmd data
	myMask = myMask * (myDict['evr']['code_162']==0)
	myMask = myMask * (myDict['TSS_OPAL']['positionFWHM']<50)
	myMask = myMask * (myDict['TSS_OPAL']['positionFWHM']>10)
	myMask = myMask * (myDict['ebeam']['photon_energy']>900)
	myMask = myMask * (myDict['ebeam']['photon_energy']<930)
	#myMask = myMask * (myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (myDict['gas_detector']['f_11_ENRC']>1)

	return myMask
