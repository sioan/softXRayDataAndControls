from pylab import *

def sxri0214run149(myDict):
	myMask = ones(len(myDict['ACQ1/amplitude'])).astype(bool)
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])>0)	#excluding bad time tool data
	myMask = myMask * (array(myDict['ACQ1']['amplitude'])>0.000001)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['ACQ1']['amplitude'])<0.000015)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['gmd']['milliJoulesPerPulse'])>0.00001)	#excluding bad gmd data
	myMask = myMask * (array(myDict['gmd']['milliJoulesPerPulse'])<0.0005)	#excluding bad gmd data
	
	myMask = myMask * (array(myDict['evr']['code_162'])==0)
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])<50)
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])>10)
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])<450)
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])>250)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])>930)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])<940)
	myMask = myMask * (array(myDict['ACQ2']['chopperState'])<0.49889787711650729)
	#myMask = myMask * (array(myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (array(myDict['gas_detector']['f_11_ENRC'])>1)

	return myMask

def sxri0214run142(myDict):
	#myMask = myMask.astype(bool)
	#arbKey = myDict.keys()[0]
	myMask = ones(len(myDict['ACQ1/amplitude'])).astype(bool)
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])>100)	#excluding bad time tool data
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])<350)	#excluding bad time tool data
	myMask = myMask * (array(myDict['acqiris2'])>0.002)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['acqiris2'])<0.90)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['GMD'])>0.00001)	#excluding bad gmd data
	myMask = myMask * (array(myDict['GMD'])<0.0012)	#excluding bad gmd data
	myMask = myMask * (array(myDict['evr']['code_162'])==0)	#get rid of bY kick
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])<50)
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])>10)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])>900)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])<930)
	#myMask = myMask * (array(myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (array(myDict['gas_detector']['f_11_ENRC'])>1)

	return myMask
