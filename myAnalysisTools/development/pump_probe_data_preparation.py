#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
from pylab import *
import h5py
import os


myDirectory="smallHdf5Data/"
myFiles = [i for i in os.listdir(myDirectory) if "h5" in i]

timeToolSign = 1
atm_camera_key = 'TSS_OPAL'
atm_data_key = 'pixelTime'
delay_stage_key = 'delayStage'
signal_of_interest_key = 'acqiris2'
normalizing_reference_key = 'GMD'

for i in myFiles:
	print i
	f = h5py.File(myDirectory+i,"r+")
	if ("atm_corrected_timing" not in f):
		atm_corrected_timing= 2/.3*(array(f[delay_stage_key]))+timeToolSign*array(f[atm_camera_key][atm_data_key])/1000.0
		normalized_intensity= array(f[signal_of_interest_key])/array(f[normalizing_reference_key])
		
		f.create_dataset("atm_corrected_timing", data=atm_corrected_timing, chunks=True, maxshape=(None,))
		f.create_dataset("normalized_intensity", data=normalized_intensity, chunks=True, maxshape=(None,))
	f.close()
	


	#removing pre laser shot need to abstract into config file
	#update mask
	#laserMask = myDict[correctedxAxis] < 12.4
	#myMask *= laserMask 
