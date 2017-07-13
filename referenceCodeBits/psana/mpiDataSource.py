from psana import *
import numpy as np
import sys
runnum = int(sys.argv[1])

# for realtime analysis add ":dir=/reg/d/ffb/sxr/sxrn9616/xtc:live"
# at the same time as your switch to the priority queue in the submit script
dsource = MPIDataSource('exp=sxr12516:run=%d:smd'%runnum)
APD = Detector('Acq01')
gd_det = Detector('FEEGasDetEnergy')
gmd_det = Detector('GMD')
mono_det = Detector('MONO_encoder')
evr_det = Detector('evr0')
ebeam_det = Detector('EBeam')

# need to add delay-stage encoder (like mono encoder)

# to be used for andor
#andor_det = Detector('andor')

# to be used for timing tool
#ttool_fltpos_det = Detector('TTSPEC:FLTPOS')

smldata = dsource.small_data('/reg/d/psdm/sxr/sxrn9616/results/oldrun%d.h5'%runnum,gather_interval=100)

for nevt,evt in enumerate(dsource.events()):
   wf = APD.waveform(evt)
   gd = gd_det.get(evt)
   gmd = gmd_det.get(evt)
   mono = mono_det.get(evt)
   ebeam = ebeam_det.get(evt)
   eventCodes = evr_det.eventCodes(evt)
   #ttool_fltpos = ttool_fltpos_det()
   #andor = andor_det.calib(evt)

   #if wf is None or gd is None or gmd is None or mono is None or eventCodes is None or ebeam is None:
   #   #print 'none',wf,gd,gmd,mono,eventCodes
   #   print 'none',eventCodes
   #   continue


   d = {}
   if wf is not None: d['apd_waveform']=wf[0][:10]
   if gd is not None:
      gd_vals = np.array((gd.f_11_ENRC(),gd.f_12_ENRC(),
                          gd.f_21_ENRC(),gd.f_22_ENRC()))
      d['gd']=gd_vals
   if gmd is not None: d['gmd']=gmd.relativeEnergyPerPulse()
   if mono is not None: d['mono']=mono.encoder_count()
   if eventCodes is not None:
      if 162 in eventCodes:
         xray_drop = 1
      else:
         xray_drop = 0
      d['xray_drop']=xray_drop

   #if ttool_fltpos is not None:
   #   d['ttool_fltpos'] = ttool_fltpos
   if ebeam is not None: d['photonEnergy'] = ebeam.ebeamPhotonEnergy()
   smldata.event(d)

smldata.save()
