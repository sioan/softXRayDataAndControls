from pylab import *
import h5py
from scipy.optimize import curve_fit
import IPython

#load data
experiment_run_name = "sxrlr0716run18"
my_file = experiment_run_name+".h5"
my_hdf5_object = h5py.File("small_h5_data/"+my_file,"r")

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
	sigma_min = 0.5
	#return a*exp(-(x-x0)**2/(2*sigma**2))+4e-2
	return a*exp(-(x-x0)**2/(2*(sigma**2+sigma_min**2)))+offset

def get_peaks(my_spectra):
	energy = arange(len(my_spectra))
	num_peaks = 10
	working_area = 10
	initial_positions = argsort(my_spectra)[:num_peaks]
	initial_amplitudes = my_spectra[initial_positions]

	my_fits = [0,0,0,0]

	for i in arange(num_peaks):
		try:
			if(initial_positions[i]>working_area and initial_positions[i]<(len(energy)-working_area)):
				y = my_spectra[initial_positions[i]-working_area:initial_positions[i]+working_area]
				x = energy[initial_positions[i]-working_area:initial_positions[i]+working_area]
	
				popt,pcov = curve_fit(gaussian,y,x,p0=[initial_positions[i],0.1,initial_amplitudes[i],0.0])
		
				my_fits = vstack([my_fits,[popt[0]+initial_positions[i],popt[1],popt[2],popt[3]]])
		except RuntimeError:
			#IPython.embed()
			pass

	return my_fits[1:]


my_amplitudes = array([])
my_energies = array([])
my_sigmas = array([])

my_counter = 0
for my_spectra in my_dict['andor_spec/image']:
	my_fit = get_peaks(my_spectra)
	my_amplitudes = append(my_amplitudes, my_fit[:,2])	
	my_energies = append(my_energies,my_fit[:,0])
	my_sigmas = append(my_sigmas,my_fit[:,1])
	if(my_counter%100==0):
		print(my_counter)
	my_counter +=1

#plot(sum(array([(i>340)*1.0 for i in my_dict['andor_spec/image']]),axis=0))
#show()
