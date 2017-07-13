import os
from psana import *
import time
import pylab 

for runNum in pylab.arange(1,100):

	dsource = MPIDataSource('exp=sxr12416:run='+str(runNum))
	#dsource = DataSource('exp=sxr12416:run=5')
	analogInDetector  = Detector('SXR-AIN-01')
	gmdDetector  = Detector('GMD')
	FEEGasDetEnergyDetector  = Detector('FEEGasDetEnergy')

	try:
		os.remove("run"+str(runNum)+".h5")
	except OSError:
		print("no previous files to delete")

	smldata = dsource.small_data('run'+str(runNum)+'.h5',gather_interval=10)


	partial_run_sum = None

	startTime=time.time()
	for nevt,evt in enumerate(dsource.events()):
	   
	   # save per-event data
	  
	   if(nevt%100==0):
		print ("time " +str((time.time()-startTime)/60.0)+" nevt = "+str(nevt))


	   gmd = gmdDetector.get(evt)
	   
	   FEEGasDetEnergy = FEEGasDetEnergyDetector.get(evt)

	   ain  = analogInDetector.get(evt)

	   d = {}

	   if ain is not None:
		#print 'found ain'
		voltages = ain.channelVoltages()
	    #   print voltages,type(voltages)
		d['analogVoltages']=voltages
		
	  	#smldata.event(voltages=voltages)
	

	   if FEEGasDetEnergy is not None:
		#print 'found FEEGasDetEnergy'

		d['FEEGasDetEnergy']={}
		d['FEEGasDetEnergy']['f_11_ENRC']=FEEGasDetEnergy.f_11_ENRC()
		d['FEEGasDetEnergy']['f_12_ENRC']=FEEGasDetEnergy.f_12_ENRC()
		d['FEEGasDetEnergy']['f_21_ENRC']=FEEGasDetEnergy.f_21_ENRC()
		d['FEEGasDetEnergy']['f_22_ENRC']=FEEGasDetEnergy.f_22_ENRC()
	
		#smldata.event(d)



	   if gmd is not None:
		#print 'found gmd'
	
		d['GasMonitorDetector']={}
		d['GasMonitorDetector']['milliJoulesAverage']=gmd.milliJoulesAverage()
		d['GasMonitorDetector']['milliJoulesPerPulse']=gmd.milliJoulesPerPulse()
	
	   smldata.event(d)

	   #if nevt>200: break
	 
	# save HDF5 file, including summary data
	smldata.save()
