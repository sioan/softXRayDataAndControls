import os
from psana import *
import time
import pylab 
import sys

runNum = sys.argv[1]

dsource = MPIDataSource('exp=xpp11816:run='+str(runNum))
#dsource = DataSource('exp=sxr12416:run=5')
analogInDetector  = Detector('AMO-AIN-01')
analogIn1Detector  = Detector('AMO:USR:ai1:1')
analogIn2Detector  = Detector('AMO:USR:ai1:2')
analogIn3Detector  = Detector('AMO:USR:ai1:3')
wavelengthDetector = Detector('SIOC:SYS0:ML00:AO192')

gmdDetector  = Detector('GMD')
FEEGasDetEnergyDetector  = Detector('FEEGasDetEnergy')
GATTFEEDetector = Detector('GATT:FEE1:310:R_ACT')


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

   analogIn1 = analogIn1Detector(evt)
   analogIn2 = analogIn2Detector(evt)
   analogIn3 = analogIn3Detector(evt)
   #print analogIn3 

   wavelength = wavelengthDetector(evt)

   GATTFEE = GATTFEEDetector(evt)

   d = {}

   #if ain is not None:
	#print 'found ain'
	#voltages = ain.channelVoltages()
    	#print voltages,type(voltages)
	#d['analogVoltages']=voltages
	
  	#smldata.event(voltages=voltages) 
   """
   if wavelength is not None:
	d['wavelength'] = wavelength

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

   if GATTFEE is not None:
	d['GATTFEE'] = GATTFEE
   """

   if (analogIn1 and analogIn2 and analogIn1) is not None:
	d['analogVoltages'] = pylab.array([analogIn1,analogIn2,analogIn3])



   smldata.event(d)

   #if nevt>200: break
 
# save HDF5 file, including summary data
smldata.save()
