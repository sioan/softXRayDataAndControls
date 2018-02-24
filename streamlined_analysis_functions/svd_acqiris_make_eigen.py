from pylab import *
import psana
import IPython
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

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


def make_acq_svd_basis_v1(detectorObject,thisEvent,previousProcessing):
	
	thresh_hold = 0.05
	waveform_window = [1200,1230]
	eigen_basis_size = 25
	selfName = detectorObject['self_name']
	
	if (0==len(previousProcessing.keys())):
		eigen_wave_forms = {'ch0':array([]),'ch1':array([]),'ch2':array([]),'ch3':array([])}	#how to make auto sensing size?
	else:
		eigen_wave_forms = previousProcessing

	if(None is detectorObject[selfName](thisEvent)):
		#fit_results = {'amplitude':popt[2],'uncertainty_cov':pcov[2,2]}
		return eigen_wave_forms

	x = detectorObject[selfName](thisEvent)[1][0]

	#

	for i in arange(len(detectorObject[selfName](thisEvent)[0])):

		y = detectorObject[selfName](thisEvent)[0][i]
		y -= mean(y[:300])
		try:
			#IPython.embed()
			y /= dot(y,y)
			y -= dot(dot(eigen_wave_forms['ch'+str(i)],y),eigen_wave_forms['ch'+str(i)])
			temp = vstack([eigen_wave_forms['ch'+str(i)],y])

		except (ValueError,TypeError,) as e:
			temp = y/dot(y,y)

			my_max = max(abs(temp))	#generating eigenbasis with 
			
			eigen_wave_forms['ch'+str(i)] = y/dot(y,y)**0.5

		try:
			if(len(temp.shape)<2):
				raise IndexError
			
			#################	
			#brute force svd approach. too big. fails. use svd approach based on eig below. keeping here so don't make same mistake
			#u,s,v = svd(temp)	
			#################
			#how to preferentially select out peak region without explicit windowing?  Solution directly below
			#finicky with threshold value
			#################
			#thresholded_temp = 0 + temp			
			#for j in arange(len(temp)):
			#	my_mask = abs(temp[j])<thresh_hold*max(abs(temp[j]))
			#	thresholded_temp[j][my_mask] = 0
			#my_eig = eig(dot(thresholded_temp,thresholded_temp.transpose()))
			#################
		
			#################
			#brute force windowing
			my_eig = eig(dot(temp[:,waveform_window[0]:waveform_window[1]],temp[:,waveform_window[0]:waveform_window[1]].transpose()))
			#################			

			#my_eig = eig(dot(temp,temp.transpose()))
			v = dot(my_eig[1],temp)
			#v = array([j/dot(j,j) for j in v])

			eigen_wave_forms['ch'+str(i)] = v[:eigen_basis_size]	
	
		except (LinAlgError,IndexError) as e:
			pass


	return eigen_wave_forms


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
