from pylab import *
import psana
import IPython
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter



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
		win_c = argmax(abs(filtered_signal))
		initial_guess = [1,win_c,filtered_signal[win_c]]
		try:
			popt,pcov = curve_fit(peakFunction,arange(win_c-4,win_c+5),abs(filtered_signal[win_c-4:win_c+5]), p0=initial_guess)
		
		
			myDict = {'time_pixel':popt[1],'uncertainty_cov':pcov[1,1]}
		except (RuntimeError,ValueError):
			myDict = {'time_pixel':-999,'uncertainty_cov':-999}

		#IPython.embed()

		return myDict

def get_projection(detectorObject,thisEvent):
	#IPython.embed()
	selfName = detectorObject['self_name']
	myImage = detectorObject[selfName].raw(thisEvent)
	if None == myImage:
		return (zeros(1024))
	else:
		return sum(myImage[370:],axis=0)

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
