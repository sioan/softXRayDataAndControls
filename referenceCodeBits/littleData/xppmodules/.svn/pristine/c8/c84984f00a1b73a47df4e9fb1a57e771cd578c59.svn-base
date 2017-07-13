import sys
import os
#p = ["./psanamon","./xppmodules/src/cspad","./xppmodules/src/cspad/alignment"]
#for pi in p:
#  if not (pi in sys.path): sys.path.append(pi)

import sys
sys.path.insert(1,'/reg/g/xpp/xppcode/python')
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

import time
import numpy as np
import threading
from psana import *
import ConfigParser
from utilities import *
import sys
import os 
import h5py

class xpp_binning(object):
    def __init__(self):

        self.read_conf()        
        self.printFreq = 1000

        if self.debug:
          print '*** here in new init'

        self.time_init = time.time()
        self.counter = 0

    def read_conf(self):
        print 'we are reading the cnf file!'
        self.commonMode  = self.configBool('commonMode',False)
        self.InputFile  = self.configStr('InputFile','')
        self.keyStr  = self.configStr('keyStr','')
        self.alias  = self.configStr('alias','')
        self.det = psana.Detector(self.alias, env)
      
    def beginjob(self, evt, env):
      self.time_begin = time.time()
      print 'time init :%.2f'%(self.time_begin - self.time_init)
      if self.debug:
        print '*** here in beginjob'

      f = h5py.File(self.InputFile)
      self.mask = f['mask'].value
      self.correct = f['correct'].value
      self.bins = f['bins'].value
      self.shape = f['shape'].value

      if self.debug:
          print 'Masked %d pixel out of %d' %(np.sum(self.mask),np.sum(np.ones_like(self.mask)))

      self.time_begin_done = time.time()
      if self.debug:
        print 'time begin :%.2f'%(self.time_begin_done - self.time_begin)
      self.time_int = 0
      
    def beginrun(self, evt, env):
        self.ncalib=0
        if self.debug:
            print 'found run number',evt.run()                                
        self.pedestal = self.det.pedestal(evt.run())

    def begincalibcycle(self, evt, env):
      if self.debug:
          print '*** here in begincalib'
      if self.ncalib==0:
          env.configStore().put(self.mask, "%s_mask"%self.keyStr)
          env.configStore().put(self.correct, "%s_correction"%self.keyStr)
          env.configStore().put(self.bins, "%s_bins"%self.keyStr)
          env.configStore().put(self.shape, "%s_shape"%self.keyStr)
      self.ncalib+=1
      
    def event(self, evt, env):
      self.printFreq()
        
      start_time_int = time.time()
      if self.commonMode:
          data = self.det.calib(evt)
      else:
          data = self.det.raw_data(evt)-self.pedestal

      #now apply the mask, correct, flatten, bin, shape.
      resTmp = data*correction[~self.mask].flatten()
      res = np.bincount(resTmp, self.bins).reshape(shape)

      if self.counter%self.printFreq == 0:
        print 'xpp_binning: event: ',self.counter,' in rank: ',rank,' of ',size

      if self.debug and self.counter < 2:
        print 'az average, shape: ',res

      evt.put(res,self.det.source,'%s_res'%self.keyStr)

      end_time_int = time.time()
      this_time_int = time.time() - start_time_int
      self.time_int += this_time_int
            
    def endcalibcycle(self, evt, env):
      if self.debug:
        print '*** here in endcalib'

    def endrun(self, evt, env):
      if self.debug:
        print '*** here in endrun'

    def endjob(self, evt, env):
      self.time_end = time.time()
      if self.debug:
        print '*** here in endjob'

      print 'time for integration : %.2f '%(self.time_int)
      print 'time for integration ',self.time_int
      print 'time to end : %.2f'%(self.time_end - self.time_begin_done)

    def printFreq(self):
      if self.counter < 100:
        self.printFreq = 10
      elif self.counter < 1000:
        self.printFreq = 100
      elif self.counter < 10000:
        self.printFreq = 1000
      else:
        self.printFreq = 10000
