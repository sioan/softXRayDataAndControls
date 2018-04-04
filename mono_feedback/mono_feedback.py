import sys
#sys.path.append("/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.47/lib/python2.7/site-packages")
#sys.path.append("/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.47/lib/python2.7/site-packages/psmon/")	#source $PSPKG_ROOT/etc/set_env.sh
#sys.path.append("/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.47/lib/python2.7/site-packages/psmon/")
import time
from psp.Pv import Pv
import IPython
import numpy as np
from pylab import *
from psmon.plots import Image,XYPlot
from psmon import publish

def ts_to_fid(timestamp):
	return 0x7FFF & timestamp[1]

def main():
	my_list = []

	#pv_list = [gdet, gmd, ebeam]

	gdet, gmd, e_beam = get_time_stamped_data()
	e_beam_mean = np.mean(e_beam)
	e_beam_std = np.std(e_beam)
	my_bins = arange(e_beam_mean-3*e_beam_std,e_beam_mean+3*e_beam_std,6*e_beam_std/100.0)
	
	e_beam_histogram = np.histogram(e_beam,my_bins)[0]
	e_beam_histogram/=sum(e_beam_histogram)
	plot_ebeam_hist = XYPlot(0,"counts vs. e_beam",my_bins[1:],e_beam_histogram)

	gmd_histogram = np.histogram(e_beam*gmd,my_bins)[0]/e_beam_histogram
	plot_gmd_hist = XYPlot(0,"counts vs. e_beam",my_bins[1:],gmd_histogram)


	#publish.local = True
	time_const = 0.95

	while(True):

		gdet, gmd, e_beam = get_time_stamped_data()
		current_beam_histogram = np.histogram(e_beam,my_bins)[0]
		e_beam_histogram= e_beam_histogram*time_const+(1.0-time_const)*current_beam_histogram*1.0/sum(current_beam_histogram)
		e_beam_histogram/=1.0*sum(e_beam_histogram)
		
		plot_ebeam_hist = XYPlot(0,"counts vs. e_beam",my_bins[1:],e_beam_histogram)
		publish.send('counts_ebeam',plot_ebeam_hist)

		gmd_histogram = np.histogram(e_beam*gmd,my_bins)[0]/e_beam_histogram
		plot_gmd_hist = XYPlot(0,"gmd vs. e_beam",my_bins[1:],gmd_histogram)
		publish.send('gmd_ebeam',plot_ebeam_hist)



	#tst_one = Pv('SXR:TST:CTRL:1')
	#tst_two = Pv('SXR:TST:CTRL:2')
    
	#temp = get_time_stamped_data()
	#for i in np.arange(10):
	#while(True):

		#x,y,dydx = get_slope()
		#tst_one.put(y)
		#tst_two.put(dydx)
		#my_list.append([x,y,dydx])
		
    

	#my_list=array(my_list)
	IPython.embed()

def get_slope():

	my_array = get_time_stamped_data()
	
	normalized_mono = my_array[1]/my_array[0]

	my_cov = np.cov(np.array([my_array[2],normalized_mono]))

	my_slope = my_cov[0,1]/my_cov[0,0]


	return np.mean(my_array[2]), np.mean(normalized_mono),my_slope

def get_time_stamped_data():
	sample_time = 0.50
	num_to_show = 5
	gdet = Pv('GDET:FEE1:241:ENRC')
	gmd = Pv('SXR:GMD:BLD:milliJoulesPerPulse')
	ebeam = Pv('BLD:SYS0:500:PHOTONENERGY')

	pv_list = [gdet, gmd, ebeam]

	for pv in pv_list:
		pv.monitor_start(True)
	time.sleep(sample_time)
	for pv in pv_list:
		pv.monitor_stop()

	my_dict = {}

	for pv in pv_list:
		for my_timestamps, my_vals in zip(pv.timestamps, pv.values):
			if ts_to_fid(my_timestamps) in my_dict:
				my_dict[ts_to_fid(my_timestamps)][pv.name] = my_vals
			else:
				my_dict[ts_to_fid(my_timestamps)] = {pv.name:my_vals}

       


	my_array = np.array([np.array([my_dict[i][j] for j in my_dict[i]]) for i in my_dict if len(my_dict[i])==3]).transpose()
      
	return my_array



if __name__ == '__main__':
    main()
