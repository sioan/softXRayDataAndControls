import sys
#sys.path.append("/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.47/lib/python2.7/site-packages")
#sys.path.append("/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.47/lib/python2.7/site-packages/psmon/")	#source $PSPKG_ROOT/etc/set_env.sh
#sys.path.append("/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.47/lib/python2.7/site-packages/psmon/")
import time
from psp.Pv import Pv
import IPython
import numpy as np
from pylab import *
from psmon.plots import MultiPlot,Image,XYPlot
from psmon import publish
import time

def ts_to_fid(timestamp):
	return 0x7FFF & timestamp[1]

def main():
	my_list = []

	gdet = Pv('GDET:FEE1:241:ENRC')
	gmd = Pv('SXR:GMD:BLD:milliJoulesPerPulse')
	ebeam = Pv('BLD:SYS0:500:PHOTONENERGY')
	pv_list = [gdet, gmd, ebeam]

	gdet, gmd, e_beam = get_time_stamped_data(pv_list)
	e_beam_mean = np.mean(e_beam)
	e_beam_std = np.std(e_beam)
	e_range = 20+0*6*e_beam_std
	n_bins = 100
	my_bins = arange(e_beam_mean-e_range,e_beam_mean+e_range,2*e_range/n_bins)
	
	e_beam_histogram = np.histogram(e_beam,my_bins)[0]
	e_beam_histogram/=sum(e_beam_histogram)
	plot_ebeam_hist = XYPlot(0,"counts vs. e_beam",my_bins[1:],e_beam_histogram)

	gmd_histogram = np.histogram(e_beam*gmd,my_bins)[0]/e_beam_histogram
	plot_gmd_hist = XYPlot(0,"counts vs. e_beam",my_bins[1:],gmd_histogram)


	#publish.local = True
	hist_size = 2400

	gdet_list, gmd_list, e_beam_list = (array([]),array([]),array([]))

	while(True):

		try:

			gdet, gmd, e_beam = get_time_stamped_data(pv_list)

			e_beam_mean = np.mean(e_beam)
			e_beam_std = np.std(e_beam)
			e_range = 10+0*6*e_beam_std
			n_bins = 100
			my_bins = arange(e_beam_mean-e_range,e_beam_mean+e_range,2*e_range/n_bins)

			e_beam_list = append(e_beam_list[-hist_size:],e_beam)
			gmd_list = append(gmd_list[-hist_size:],gmd)
			gdet_list = append(gdet_list[-hist_size:],gdet)

			e_beam_histogram = np.histogram(e_beam_list,my_bins)[0]
			gmd_histogram = np.histogram(e_beam_list,my_bins,weights=gmd_list)[0]*1.0/(e_beam_histogram+1e-12)
			gdet_histogram = np.histogram(e_beam_list,my_bins,weights=gdet_list)[0]*1.0/(e_beam_histogram+1e-12)
		
		
			plot_ebeam_hist = XYPlot(0,"counts vs. e_beam",my_bins[1:],e_beam_histogram)
			publish.send('counts_ebeam',plot_ebeam_hist)
			

			plot_gmd_hist = XYPlot(0,"gmd vs. e_beam",my_bins[1:],gmd_histogram)
			publish.send('gmd_ebeam',plot_gmd_hist)

			normalized_e_beam_histogram = e_beam_histogram*1.0/sum(nan_to_num(e_beam_histogram)+1e-12)
			normalized_gmd_histogram = gmd_histogram*1.0/sum(nan_to_num(gmd_histogram))
			normalized_gdet_histogram = gdet_histogram*1.0/sum(nan_to_num(gdet_histogram))

			plot_overlay = XYPlot(0,"gmd and ebeam",[my_bins[1:],my_bins[1:]],[normalized_e_beam_histogram,normalized_gmd_histogram])
			#plot_overlay = XYPlot(0,"gmd and ebeam",[my_bins[1:],my_bins[1:],my_bins[1:]],[normalized_e_beam_histogram,normalized_gmd_histogram,normalized_gdet_histogram])
			x_temp = arange(-10,10,1) 
			publish.send('both_gmd_ebeam',plot_overlay)


		except KeyboardInterrupt:
			break
		except ValueError:
			print("GMD likely down")
			time.sleep(2)



def get_slope():

	my_array = get_time_stamped_data()
	
	normalized_mono = my_array[1]/my_array[0]

	my_cov = np.cov(np.array([my_array[2],normalized_mono]))

	my_slope = my_cov[0,1]/my_cov[0,0]


	return np.mean(my_array[2]), np.mean(normalized_mono),my_slope

def get_time_stamped_data(pv_list):
	sample_time = 0.50
	num_to_show = 5

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
