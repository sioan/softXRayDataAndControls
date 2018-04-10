from pylab import *
import h5py
from scipy.optimize import curve_fit
import IPython

#load data
experiment_run_name = "sxrlr0716run17"
my_file = experiment_run_name+".h5"
my_hdf5_object = h5py.File(my_file,"r")

#convert hdf5 to dict
my_list = []
def func(name, obj):
	my_list.append(name)

my_hdf5_object.visititems(func)
my_dict = {}
for i in my_list:
	try:
		my_dict[i] = array(my_hdf5_object[i])
	except:
		pass
pixel_to_femtosecond_list = []
width_list = []

my_hdf5_object.close()

def gaussian(x, x0,sigma,a,offset):
	sigma_min = 0.75
	#return a*exp(-(x-x0)**2/(2*sigma**2))+4e-2
	return a*exp(-(x-1.0*x0)**2/(2*(sigma**2+sigma_min**2)))+offset

def get_peaks(my_spectra):
	energy = arange(len(my_spectra))
	num_peaks = 3
	working_area = 10
	initial_positions = argsort(my_spectra)[-num_peaks:]
	initial_amplitudes = my_spectra[initial_positions]*1.0
	known_good_region = 2200

	my_fits = [0,0,0,0,0]

	for i in arange(num_peaks):
		try:
			if((initial_positions[i]>working_area and initial_positions[i]<(len(energy)-working_area)) and initial_positions[i]< known_good_region):
				y = my_spectra[initial_positions[i]-working_area:initial_positions[i]+working_area]
				x = energy[initial_positions[i]-working_area:initial_positions[i]+working_area]
	
				popt,pcov = curve_fit(gaussian,x,y,p0=[initial_positions[i]*1.0,0.1,initial_amplitudes[i],0.0])
		
				my_fits = vstack([my_fits,[initial_positions[i],popt[0],popt[1],popt[2],popt[3]]])

				my_spectra[initial_positions[i]-working_area:initial_positions[i]+working_area]-=0
			else:
				my_fits = vstack([my_fits,[initial_positions[i],0,0,0,0]])

		except RuntimeError:
			#IPython.embed()
			#pass
			my_fits = vstack([my_fits,[initial_positions[i],0,0,0,0]])

	return my_fits[1:]


my_amplitudes = array([])
my_energies_fine = array([])
my_energies_coarse = array([])
my_sigmas = array([])

my_counter = 0
for my_spectra in my_dict['andor_spec/image']:
	
	my_spectra=my_spectra*1.0
	my_median= median(my_spectra)
	for i in arange(5):
		my_spectra[i::5]=my_spectra[i::5]-median(my_spectra[i::5])+my_median	#fourier filtering

	my_fit = get_peaks(my_spectra)
	my_amplitudes = append(my_amplitudes, my_fit[:,3])	
	my_energies_coarse = append(my_energies_coarse,my_fit[:,0])
	my_energies_fine = append(my_energies_fine,my_fit[:,1])
	my_sigmas = append(my_sigmas,my_fit[:,2])
	if(my_counter%100==0):
		print(my_counter)
	my_counter +=1

#hist(my_energies_coarse[my_amplitudes*(my_sigmas**2+1.0**2)**0.5>345],bins=arange(2048))
#plot(sum(array([(i>345)*1.0 for i in my_dict['andor_spec/image']]),axis=0))

#plot(sum(array([(i>340)*1.0 for i in my_dict['andor_spec/image']]),axis=0))
#show()
