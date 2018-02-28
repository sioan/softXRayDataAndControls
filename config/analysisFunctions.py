from pylab import *
import psana
import IPython
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

def genericReturn(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	return detectorObject[selfName](thisEvent)

svd_size = 16
eigen_background = {}
#for i in [60,63,72,71,79,81,82]:
#	eigen_background[str(i)] = loadtxt("eigen_backgrounds/eigen_background_run"+str(i)+".dat")
try:
	eigen_background["60"] = loadtxt("eigen_backgrounds/eigen_background_run60.dat")
	eigen_background["63"] = loadtxt("eigen_backgrounds/eigen_background_run63.dat")
	eigen_background["71"] = loadtxt("eigen_backgrounds/eigen_background_run71.dat")
	eigen_background["72"] = loadtxt("eigen_backgrounds/eigen_background_run72.dat")
	eigen_background["79"] = loadtxt("eigen_backgrounds/eigen_background_run79.dat")
	eigen_background["81"] = loadtxt("eigen_backgrounds/eigen_background_run81.dat")
	eigen_background["82"] = loadtxt("eigen_backgrounds/eigen_background_run82.dat")
except: pass


def peakFunction(x,a,x0,offset):
	return a*(x-x0)**2+offset

def svd_atm_analysis(detectorObject,thisEvent):
	v = eigen_background[str(thisEvent.run())]
	#IPython.embed()
	myImage = detectorObject['timeToolOpal'].raw(thisEvent)
	if None == myImage:
		myDict = {"time_pixel":-999.0,"uncertainty_cov":-999.0}
		return myDict
	else:
		my_projection = sum(myImage[370:],axis=0)
		background_subtracted = my_projection - dot(dot(my_projection,v[:svd_size].transpose()),v[:svd_size])

		#initial guess. win_c = window cneter. 25 is empirical drop width
		filtered_signal = savgol_filter(background_subtracted,25,2,1)
		win_c = argmin(filtered_signal)
		initial_guess = [1,win_c,filtered_signal[win_c]]
		try:
			popt,pcov = curve_fit(peakFunction,arange(win_c-4,win_c+5),filtered_signal[win_c-4:win_c+5], p0=initial_guess)
		
		
			myDict = {'time_pixel':popt[1],'uncertainty_cov':pcov[1,1]}
		except (RuntimeError,ValueError):
			myDict = {'time_pixel':-999,'uncertainty_cov':-999}

		#IPython.embed()

		return myDict

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
		
		myDict['amplitude'] = -99999.0
		myDict['pixelTime'] = -99999.0
		myDict['positionFWHM'] = -99999.0


	else:

		myDict['amplitude'] = ttData.amplitude()
		myDict['pixel_position'] = ttData.position_pixel()
		myDict['pixelTime'] = ttData.position_time()
		myDict['positionFWHM'] = ttData.position_fwhm()

	return myDict

def generic_acqiris_analyzer(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	fit_results = {}

	if(None is detectorObject[selfName](thisEvent)):
		#fit_results = {'amplitude':popt[2],'uncertainty_cov':pcov[2,2]}
		return None
		
	x = detectorObject[selfName](thisEvent)[1][0]
	for i in arange(len(detectorObject[selfName](thisEvent)[0])):

		y = detectorObject[selfName](thisEvent)[0][i]

		initial_peak = argmax(convolve(abs(y),[1,1,1,1,1,1]),mode='same')
	
		

		#myFit = polyfit(x, myWaveForm[7500:10000],3)
		#p = poly1d(myFit)
		#myMax = max(p(x))
		#return myMax	

		y_small = y[initial_peak-10:initial_peak+10]
		x_small = x[initial_peak-10:initial_peak+10]

		#IPython.embed()
		try:
			popt,pcov = curve_fit(peakFunction,x_small,y_small,p0=[0.0,initial_peak,y[initial_peak]])
		
			fit_results['ch'+str(i)] = {"position":popt[1],'amplitude':popt[2],'position_var':pcov[1,1],'amplitude_var':pcov[2,2]}

		except RuntimeError:
			fit_results = None}


	return fit_results

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



