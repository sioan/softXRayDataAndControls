from pylab import *
import psana
import IPython
from scipy.optimize import curve_fit

def genericReturn(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	return detectorObject[selfName](thisEvent)

def get_projection(detectorObject,thisEvent):
	#IPython.embed()
	myImage = detectorObject['timeToolOpal'].raw(thisEvent)
	if None == myImage:
		return (zeros(1024))
	else:
		return sum(myImage[370:],axis=0)

def genericSummaryZero(detectorObject,thisEvent,previousProcessing):
	return 0

def myZeroReturn(detectorObject,thisEvent,previousProcessing):
	return 0

def getTimeToolData(detectorObject,thisEvent):
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

def peakFunction(x,a,x0,offset):
	return a*(x-x0)**2+offset

def getPeak(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	if(None is detectorObject[selfName](thisEvent)):
		fit_results = {'amplitude':popt[2],'uncertainty_cov':pcov[2,2]}
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
		fit_results = {'amplitude':-9999,'uncertainty_cov':99999}


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



