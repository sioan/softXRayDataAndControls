from pylab import *

def sxri0414run60(myDict):
	myMask = ones(len(myDict['acqiris2']['amplitude'])).astype(bool)
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])>0)	#excluding bad time tool data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])>0.002)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])<0.90)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['GMD'])>0.00001)	#excluding bad gmd data
	myMask = myMask * (array(myDict['GMD'])<0.0012)	#excluding bad gmd data
	myMask = myMask * (array(myDict['evr']['code_162'])==0)
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])<50)
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])>10)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])>900)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])<930)
	#myMask = myMask * (array(myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (array(myDict['gas_detector']['f_11_ENRC'])>1)

	return myMask

def sxri0414run63(myDict):
	#myMask = myMask.astype(bool)
	#arbKey = myDict.keys()[0]
	myMask = ones(len(myDict['acqiris2']['amplitude'])).astype(bool)
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])>100)	#excluding bad time tool data
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])<350)	#excluding bad time tool data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])>0.02)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])<0.8)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['GMD'])>0.00001)	#excluding bad gmd data
	myMask = myMask * (array(myDict['GMD'])<0.0007)	#excluding bad gmd data
	myMask = myMask * (array(myDict['evr']['code_162'])==0)	#get rid of bY kick
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])<50)
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])>10)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])>900)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])<930)
	#myMask = myMask * (array(myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (array(myDict['gas_detector']['f_11_ENRC'])>1)

	return myMask

def sxri0414run79(myDict):
	myMask = ones(len(myDict['acqiris2']['amplitude'])).astype(bool)
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])>200)	#excluding bad time tool data
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])<600)	#excluding bad time tool data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])>0.002)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])<0.90)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['GMD'])>0.00001)	#excluding bad gmd data
	myMask = myMask * (array(myDict['GMD'])<0.0008)	#excluding bad gmd data
	myMask = myMask * (array(myDict['evr']['code_162'])==0)	#get rid of bY kick
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])<50)
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])>10)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])>900)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])<930)
	#myMask = myMask * (array(myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (array(myDict['gas_detector']['f_11_ENRC'])>0.3)

	#startTime = 6075229887493736017
	#stopTime  = 6075229943926703401
	
	#tempMask = array([ (i<startTime or i > stopTime) for i in myDict['event_time']])
	#myMask = myMask * (array(myDict['event_time'])>6075229887493736017)
	#myMask = myMask * (array(myDict['event_time'])<6075229943926703401)

	#myMask = myMask * (array(myDict['delayStage'])<51.0)
	#myMask = myMask * (array(myDict['delayStage'])>49.4)

	#myMask = myMask * tempMask
	return myMask

def sxri0414run72(myDict):
	myMask = ones(len(myDict['acqiris2']['amplitude'])).astype(bool)
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])>200)	#excluding bad time tool data
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])<600)	#excluding bad time tool data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])>0.000)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])<0.550)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['GMD'])>0.00000)	#excluding bad gmd data
	myMask = myMask * (array(myDict['GMD'])<0.0015)	#excluding bad gmd data
	myMask = myMask * (array(myDict['evr']['code_162'])==0)	#get rid of bY kick
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])<50)
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])>10)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])>914)	#900 full range
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])<923) #930 full range
	#myMask = myMask * (array(myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (array(myDict['gas_detector']['f_11_ENRC'])>0.3)

	return myMask

def sxri0414run81(myDict):
	myMask = ones(len(myDict['acqiris2']['amplitude'])).astype(bool)
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])>200)	#excluding bad time tool data
	myMask = myMask * (array(myDict['TSS_OPAL']['pixelTime'])<600)	#excluding bad time tool data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])>0.002)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['acqiris2']['amplitude'])<0.90)	#excluding bad acqiris data
	myMask = myMask * (array(myDict['GMD'])>0.00001)	#excluding bad gmd data
	myMask = myMask * (array(myDict['GMD'])<0.002)	#excluding bad gmd data
	myMask = myMask * (array(myDict['evr']['code_162'])==0)	#get rid of bY kick
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])<50)
	myMask = myMask * (array(myDict['TSS_OPAL']['positionFWHM'])>10)
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])>910) #900 full range
	myMask = myMask * (array(myDict['ebeam']['photon_energy'])<920) #930 full range
	#myMask = myMask * (array(myDict['fiducials']%4==3)	#this has no effect on fourier components
	myMask = myMask * (array(myDict['gas_detector']['f_11_ENRC'])>0.3)

	return myMask
