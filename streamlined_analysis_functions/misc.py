from pylab import *
import psana
import IPython
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

def genericReturn(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	return detectorObject[selfName](thisEvent)

def genericSummaryZero(detectorObject,thisEvent,previousProcessing):
	return 0

def myZeroReturn(detectorObject,thisEvent,previousProcessing):
	return 0

def getPeak(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	if(None is detectorObject[selfName](thisEvent)):
		fit_results = {'amplitude':-9999.9,'uncertainty_cov':-9999.9}
		return fit_results
		

	myWaveForm = -detectorObject[selfName](thisEvent)[0][0]

	myWaveForm -= mean(myWaveForm[:2500])

	x = arange(len(myWaveForm))[7500:10000]-8406
	#myFit = polyfit(x, myWaveForm[7500:10000],3)
	#p = poly1d(myFit)
	#myMax = max(p(x))
	#return myMax	

	#IPython.embed()
	try:
		popt,pcov = curve_fit(peakFunction,x,myWaveForm[7500:10000])
		
		fit_results = {'amplitude':popt[2],'uncertainty_cov':pcov[2,2]}

	except RuntimeError:
		fit_results = {'amplitude':-9999.0,'uncertainty_cov':99999.0}


	return fit_results

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
	my_dict = {"joules":-999.0,"relative":-999.0}

	if (None not in [temp]):
		my_dict["joules"] = temp.milliJoulesPerPulse()
		my_dict["relative"] = temp.relativeEnergyPerPulse()
	else: 	
		pass

	return my_dict

def getEBeam(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	temp = detectorObject[selfName].get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0



