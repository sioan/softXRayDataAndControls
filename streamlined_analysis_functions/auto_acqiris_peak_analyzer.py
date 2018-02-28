from pylab import *
import psana
import IPython
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter



def peakFunction(x,a,x0,offset):
	return a*(x-x0)**2+offset

def generic_acqiris_analyzer(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	fit_results = {}

	if(None is detectorObject[selfName](thisEvent)):
		#fit_results = {'amplitude':popt[2],'uncertainty_cov':pcov[2,2]}
		return None
		
	x = detectorObject[selfName](thisEvent)[1][0]
	for i in arange(len(detectorObject[selfName](thisEvent)[0])):

		y = detectorObject[selfName](thisEvent)[0][i]


		smoothed_wave = convolve(y,[1,1,1,1,1,1],mode='same')
		initial_peak = argmax(smoothed_wave)	#how to hardcode
		initial_height = smoothed_wave[initial_peak]
		peak_width = 4	############################## tunable parameter

		y_small = y[initial_peak-peak_width:initial_peak+peak_width] - mean(y[:])
		x_small = x[initial_peak-peak_width:initial_peak+peak_width]

		#IPython.embed()
		try:
			popt,pcov = curve_fit(peakFunction,x_small,y_small,p0=[0.0,initial_peak,initial_height])
		
			fit_results['ch'+str(i)] = {"position":popt[1],'amplitude':popt[2],'position_var':pcov[1,1],'amplitude_var':pcov[2,2]}

		except (RuntimeError,TypeError) as e:
			fit_results = None

	return fit_results



