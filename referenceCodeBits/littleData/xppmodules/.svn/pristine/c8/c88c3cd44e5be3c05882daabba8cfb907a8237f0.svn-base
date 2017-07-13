import sys
import os
p = ["./psanamon"]
for pi in p:
  if not (pi in sys.path): sys.path.append(pi)

import time
import numpy as np
import threading
import psutil
from psana import *
from psutil import ImageHelper, HistHelper, HistOverlayHelper, XYPlotHelper
import ConfigParser
from utilities import *
import resource
import timeit

class xpp_makeDarkMask(object):
    def __init__(self):

        self.xray_off_code = 162
        self.edgeMask = 5
        self.noiseCut = 5
        self.coldCut = 2

        self.debug = 0
        self.maxEvt = 1000
        self.read_conf()
        
        self.fname = "./dark_"
        self.printFreq = 100

        if self.debug > 0:
          print '*** here in new init'

    def read_conf(self):
        config = ConfigParser.RawConfigParser()
        config.read('./xppmodules/src/xpp_makeDarkMask.cfg')

        self.xray_off = config.getint('xpp_makeDarkMask','xray_off')

        self.edgeMask = config.getint('xpp_makeDarkMask','MaskEdge')
        self.noiseCut = config.getfloat('xpp_makeDarkMask','NoiseCut')
        self.coldCut = config.getfloat('xpp_makeDarkMask','ColdCut')

        self.calcMed = config.getboolean('xpp_makeDarkMask','CalcMed')
        self.calcMAD = config.getboolean('xpp_makeDarkMask','CalcMAD')
        self.calcOwn = config.getboolean('xpp_makeDarkMask','CalcOwn')
        self.writeAr = config.getboolean('xpp_makeDarkMask','writeAr')
        
        self.maxEvt = config.getfloat('xpp_makeDarkMask','MaxEvt')
        if self.maxEvt < 200:
            self.printFreq = 10
        elif self.maxEvt > 2000:
            self.printFreq = 1000
        
        self.dt = -1.1
        self.this_t = 0

        self.counter = 0
      
    def beginjob(self, evt, env):
      if self.debug > 0:
        print '*** here in beginjob'

      #containers for results
      self.dark_av = np.zeros([32,185,388], dtype=float)
      self.noise_std = np.zeros([32,185,388], dtype=float)
      self.mask = np.zeros([32,185,388], dtype=int)

      if (self.calcOwn):
        self.dark_sum = np.zeros([32,185,388], dtype=int)
        self.dark_sumsq = np.zeros([32,185,388], dtype=np.float64)
      
      #startarray for collecting dark events
      self.dark_ar = np.zeros([self.maxEvt,32,185,388], dtype=np.int16)
      print 'dark_ar: ',self.dark_ar.shape
      
      self.fname += env.experiment()+'_run'
      self.fname += str(evt.run())+'_'
      self.fname += str(self.maxEvt)+'evt_'

      self.t0=time.time()

    def beginrun(self, evt, env):
      if self.debug > 0:
        print 'found run number',evt.run()                                
        
    def begincalibcycle(self, evt, env):
      if self.debug > 0:
        print '*** here in begincalib'

    def event(self, evt, env):

      xfel_status = 1
      EVR_code = evt.get(EvrData.DataV3, Source('DetInfo(NoDetector.0:Evr.0)'))
      if EVR_code is None:
        if self.debug > 0:
          print '** no evr'
        return
      if (self.xray_off > 0):
        xfel_status, laser_status = pumpprobe_status(EVR_code, [self.xray_off], [self.xray_off])
      #work on the darks!
      if (xfel_status == 1):
        return

      if self.counter%self.printFreq == 0 :
        print 'Event: ',self.counter

      cspad = evt.get(CsPad.DataV2, Source('DetInfo(XppGon.0:Cspad.0)'))
      if (cspad is None):
        return
      data_ar = (cspad.quads(0)).data()
      for i in range(1,cspad.quads_shape()[0]):
        data_ar = np.append(data_ar,(cspad.quads(i)).data(),axis=0)

      self.dark_ar[self.counter] = data_ar
      if (self.calcOwn):
        self.dark_sum += data_ar
        self.dark_sumsq += np.multiply(data_ar,data_ar, dtype=np.float64)
        
      #usage = resource.getrusage(resource.RUSAGE_SELF)
      #sh_mem = getattr(usage,'ru_ixrss')
      #ush_mem = getattr(usage,'ru_idrss')
      #if (self.counter%self.printFreq == 0):
      #  print '** at event ',self.counter,'  : ',sh_mem,'  ',ush_mem
      self.counter += 1
      if self.counter >= self.maxEvt:
          self.stop()

    def endcalibcycle(self, evt, env):
      if self.debug > 0:
        print '*** here in endcalib'

    def endrun(self, evt, env):
      if self.debug > 0:
        print '*** here in endrun'

    def endjob(self, evt, env):
      if self.counter < self.maxEvt:
          print ' nt enough events, slice dark_av array to filled number'
          self.dark_ar = self.dark_ar[:self.counter-1,:,:,:]

      t1=time.time()
      print "Time needed for code up to array saving: %.2f"%(t1-self.t0)
      if self.writeAr:
          np.save(self.fname+"darkArray",self.dark_ar)
      print " array is written"

      t0=time.time()
      if (self.calcOwn):
        self.dark_av = np.divide(self.dark_sum, self.counter, dtype=float)
        t1=time.time()
      else:
        self.dark_av = np.mean(self.dark_ar,axis=0)
        t1=time.time()
      print "Time needed for mean %.2f"%(t1-t0)
      if (self.dark_av is not None):
        np.save(self.fname+"darkav",self.dark_av)

      t0=time.time()
      if (self.calcOwn):
        self.dark_sumsq = np.subtract(np.divide(self.dark_sumsq,self.counter,dtype=np.float64), self.dark_av*self.dark_av, dtype=np.float64)        
        self.noise_std = np.sqrt(np.abs(self.dark_sumsq))
        t1=time.time()
      else:
        self.noise_std = np.std(self.dark_ar,axis=0)
        t1=time.time()
      if (self.noise_std is not None):
        np.save(self.fname+"noise_std",self.noise_std)
      print "Time needed for std %.2f"%(t1-t0)

      t0=time.time()
      if (self.calcMed and not self.calcMAD):
        self.dark_med = np.median(self.dark_ar,axis=0)
        t1=time.time()
        print "Time needed for mediam %.2f"%(t1-t0)
        print self.dark_av[0:10,0,0]
        print self.dark_med[0:10,0,0]
        np.save(self.fname+"dark_med",self.dark_med)
      if (self.calcMAD):
        self.dark_med = np.median(self.dark_ar,axis=0)
        t1=time.time()
        print "Time needed for mediam %.2f"%(t1-t0)
        np.save(self.fname+"dark_med",self.dark_med)

        self.dark_MAD = np.abs(self.dark_ar - self.dark_med)
        self.dark_MAD = np.median(self.dark_MAD,axis=0)
        t2=time.time()
        print "Time needed for MAD  %.2f"%(t2-t1)
        np.save(self.fname+"dark_MAD",self.dark_MAD)

      #now make the mask
      self.mask = np.logical_and(self.noise_std<self.noiseCut, self.dark_av>self.coldCut)
      if (self.edgeMask>0):
          for i in self.mask:
              i[:self.edgeMask,:]=False
              i[:,:self.edgeMask]=False
              i[:,-self.edgeMask:]=False
              i[-self.edgeMask:,:]=False
      if (self.mask is not None):
        np.save(self.fname+"mask",self.mask)
