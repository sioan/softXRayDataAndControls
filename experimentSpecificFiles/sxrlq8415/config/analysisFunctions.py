from pylab import *
import psana
import IPython
import h5py

######################################################
#######Using the eigen traces#########################
######################################################

try:
	f=h5py.File("eigen_traces_run192.h5")
	eigen_traces = f['summary/nonMeaningfulCoreNumber0/Acq01/ch1/eigen_wave_forms']
except:
	print("eigen_traces_run192.h5")
	pass


def use_acq_svd_basis(detectorObject, thisEvent):
	selfName = detectorObject['self_name']
	my_results = {}

	if(None is detectorObject[selfName](thisEvent)):
		#fit_results = {'amplitude':popt[2],'uncertainty_cov':pcov[2,2]}
		return None
		
	#x = detectorObject[selfName](thisEvent)[1][0]
	for i in arange(len(detectorObject[selfName](thisEvent)[0])):
		y = detectorObject[selfName](thisEvent)[0][i]
		weightings = dot(eigen_traces,y)
		residuals = y-dot(weightings,eigen_traces)
		variance = dot(eigen_traces,residuals)**2
		#approximation in line above comes from eigen_traces is orthogonal matrix, 
		#so dot (eigen_traces.transpose(),eigen_traces) is diagonal. 
		#missing something with number of points and degrees of freedom
		my_results["ch"+str(i)] = {"weightings":weightings,"variance":variance}

	return my_results

######################################################
#######Creating the acqiris eigen basis###############
######################################################
def svd_update(eigen_system,new_vector,config_parameters):
	
	try:
		reconstructed_system = dot(eigen_system['eigen_weightings'], eigen_system['eigen_wave_forms'])
		reconstructed_system = vstack([reconstructed_system,new_vector])

		
		singular_values,svd_lsv = eig(dot(reconstructed_system,reconstructed_system.transpose()))
		
		new_weightings = dot(svd_lsv,diag(singular_values))
		new_eigen_vectors = dot(pinv(new_weightings),reconstructed_system)[:config_parameters["eigen_basis_size"]]

		eigen_system = {'eigen_weightings':new_weightings,'eigen_wave_forms':new_eigen_vectors}
	
	except TypeError:
		if ((None is new_vector) and (len(eigen_system['eigen_weightings'])>1)):
			pass
		else:
			eigen_system['eigen_weightings'] = [1]
			eigen_system['eigen_wave_forms'] = new_vector

	except ValueError:
		
		if (1==len(eigen_system['eigen_weightings'])):
			eigen_system['eigen_weightings'] = array([[1,0],[0,1]])
			eigen_system['eigen_wave_forms'] = vstack([eigen_system['eigen_wave_forms'],new_vector])
	
	return eigen_system

def make_acq_svd_basis(detectorObject,thisEvent,previousProcessing):
	selfName = detectorObject['self_name']
	config_parameters = {"thresh_hold":0.05,"waveform_mask":arange(1200,1230),"eigen_basis_size":25,"offset_mask":arange(300)}

	eigen_system = {}
	
	##############################
	#### initializing arrays #####
	##############################
	if None is detectorObject[selfName](thisEvent):
		return None

	for i in arange(len(detectorObject[selfName](thisEvent)[0])):

		try:
			eigen_system["ch"+str(i)] = previousProcessing["ch"+str(i)]
		except (KeyError,TypeError) as e:
			try:
				y =  detectorObject[selfName](thisEvent)[0][i]			
				y -= mean(y[config_parameters['offset_mask']])			
				eigen_system["ch"+str(i)]= {'eigen_wave_forms':y,'eigen_weightings':[1]}
			except (KeyError,TypeError) as e:
				eigen_system["ch"+str(i)] = {'eigen_wave_forms':None,'eigen_weightings':None}

	##############################
	###main part of calculation###
	##############################
	new_eigen_system = {}
	for i in arange(len(detectorObject[selfName](thisEvent)[0])):

		
		new_eigen_system["ch"+str(i)] = svd_update(eigen_system["ch"+str(i)],detectorObject[selfName](thisEvent)[0][i],config_parameters)
		

	return new_eigen_system

######################################################
#######End of eigen basis generation##################
######################################################

def getDelay(detectorObject, thisEvent):
        selfName = detectorObject['self_name']

        # IPython.embed()

        if detectorObject[selfName].values(thisEvent) is None:
                myDictionary = {'DLS_PS': -999.0}
                return myDictionary

        DLS_PS = detectorObject[selfName].values(thisEvent)[0]
        return {'DLS_PS': DLS_PS}


def genericReturn(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	x = detectorObject[selfName](thisEvent)
	if x is None:
		return -9999.0
	else:
		return x

def genericSummaryZero(detectorObject,thisEvent,previousProcessing):
	return 0

def myZeroReturn(detectorObject,thisEvent,previousProcessing):
	return 0

def getTimeToolData(detectorObject,thisEvent):
	IPython.embed()

	#print thisEvent.get(psana.EventId).fiducials()
	
	selfName = detectorObject['self_name']
	ttData = detectorObject[selfName].process(thisEvent)
	myDict = {}	
	if(ttData is None):
		
		myDict['amplitude'] = -99999
		myDict['pixelTime'] = -99999
		myDict['positionFWHM'] = -99999


	else:

		myDict['amplitude'] = ttData.amplitude()
		myDict['pixelTime'] = ttData.position_time()
		myDict['positionFWHM'] = ttData.position_fwhm()

	return myDict

def getxtcavData(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	detectorObject[selfName]

def getpeakb(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	myDict = {}
	myDict['APDNOAP'] = -9999.0
	myDict['APDAP'] = -9999.0
	myDict['MCPI0'] = -9999.0
	
	myWaveForm = detectorObject[selfName].waveform(thisEvent)
	if any (None in [myWaveForm]):
		return myDict
	
	MCPI0ind = 1202
	APDNOAPind = 1208
	APDAPind = 1207
	MCPI0width = 1
	APDwidth = 2
	
	myWaveForm[0] -= mean(myWaveForm[0][:1000]) #small APD	
	myWaveForm[1] -= mean(myWaveForm[1][:1000]) #large APD
	myWaveForm[2] -= mean(myWaveForm[2][:1000]) #MCP
	myDict['APDNOAP'] = mean(myWaveForm[1][APDNOAPind-APDwidth:APDNOAPind+APDwidth])
	myDict['APDAP'] = mean(myWaveForm[0][APDAPind-APDwidth:APDAPind+APDwidth])
	myDict['MCPI0'] = mean(myWaveForm[2][MCPI0ind-MCPI0width:MCPI0ind+MCPI0width])
	
	return myDict	
def getSum(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	
	myImage = detectorObject[selfName].image(thisEvent)
	
	myDict = {}
	myDict['sum'] = -999.0
	if None is not myImage:
		myDict['sum'] = sum(myImage)
	
	return myDict
	


def getPeak(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	myWaveForm = -detectorObject[selfName](thisEvent)[0][0]

	myWaveForm -= mean(myWaveForm[:2500])

	x = arange(len(myWaveForm))[7500:10000]-8406
	myFit = polyfit(x, myWaveForm[7500:10000],3)

	p = poly1d(myFit)
	myMax = max(p(x))

	#return myFit[-1]	#placing a dictionary here also works
	return myMax	

def accumulateAverageWave(detectorObject,thisEvent,previousProcessing):
	selfName = detectorObject['self_name']

	myWaveForm = -detectorObject[selfName](thisEvent)[0][0]
	myWaveForm -= mean(myWaveForm[:2500])

	return (previousProcessing+myWaveForm)

def getWaveForm(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	if (None not in [detectorObject[selfName](thisEvent)[0][0]]):
		return detectorObject[selfName](thisEvent)[0][0]
	else:	
		return 0
	
def get(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	
	if (None not in [detectorObject[selfName](thisEvent)]):
		return detectorObject[selfName](thisEvent)
	else:
		return 0

def getRaw(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	if (None not in [detectorObject[selfName](thisEvent)]):
		return detectorObject[selfName](thisEvent)
	else:
		return 0

def getGMD(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	temp = detectorObject[selfName].get(thisEvent)
	if (None not in [temp]):
		return temp.milliJoulesPerPulse()
	else: 	
		return 0.0

def getEBeam(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	temp = detectorObject[selfName].get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0



