from psana import *
import numpy as np
from ImgAlgos.PyAlgos import PyAlgos
from skbeam.core.accumulators.histogram import Histogram

dsource = MPIDataSource('exp=sxr07416:run=28:smd')
det = Detector('OPAL1')

alg = PyAlgos()
alg.set_peak_selection_pars(npix_min=9, npix_max=100, amax_thr=40,
                            atot_thr=300, son_min=0)

hist_row = Histogram((1024,0.,1024.))
hist_col = Histogram((1024,0.,1024.))
hist_amp = Histogram((1024,0.,3000.))

smldata = dsource.small_data('run28.h5',gather_interval=100)

peakrow = np.zeros((10),dtype=int)
peakcol = np.zeros((10),dtype=int)
peakamp = np.zeros((10),dtype=float)
for nevt,evt in enumerate(dsource.events()):

   calib = det.calib(evt)
   if calib is None: continue
   peaks = alg.peak_finder_v1(calib, thr_low=40, thr_high=40, radius=5, dr=0.0)
   npeaks = len(peaks)
   if npeaks==0: continue
   print nevt,len(peaks)
   if npeaks>10:
      print 'too many peaks'
      continue

   # save per-event data
   peakrow.fill(-1)
   peakcol.fill(-1)
   peakamp.fill(0.0)
   for pnum,peak in enumerate(peaks):
      peakrow[pnum] = peak[1]
      peakcol[pnum] = peak[2]
      peakamp[pnum] = peak[5]
      print peakamp[pnum]
      hist_row.fill(float(peakrow[pnum]))
      hist_col.fill(float(peakcol[pnum]))
      hist_amp.fill(float(peakamp[pnum]))

      print ("peak value = "+str(peak[1]))

   smldata.event(npeaks=len(peaks),peakrow=peakrow,peakcol=peakcol,peakamp=peakamp)
   if nevt>35: break

#import matplotlib.pyplot as plt
#plt.plot(hist_row.values)
#plt.show()
hist_row_tot = smldata.sum(hist_row.values)
hist_col_tot = smldata.sum(hist_col.values)
hist_amp_tot = smldata.sum(hist_amp.values)
smldata.save(hist_row_tot=hist_row_tot, hist_col_tot=hist_col_tot, hist_amp_tot=hist_amp_tot)
