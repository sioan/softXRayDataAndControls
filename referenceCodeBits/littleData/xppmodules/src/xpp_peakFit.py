import sys
import os
#p = ["./psanamon","./xppmodules/src/cspad","./xppmodules/src/cspad/alignment"]
#for pi in p:
#  if not (pi in sys.path): sys.path.append(pi)

import sys
sys.path.insert(1,'/reg/common/package/mpi4py/mpi4py-1.3.1/install/lib/python')
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

import time
import numpy as np
import threading
#import psutil
from psana import *
import ConfigParser
from utilities import *
import sys
import os 
from matplotlib import pyplot as plt
from GaussFit import fitPeaks

class xpp_peakFit(object):
    def __init__(self):

        self.edgeMask = 5
        self.read_conf()
        
        self.printFreq = 1000

        if self.debug:
          print '*** here in new init'

        self.time_init = time.time()
        self.counter = 0

    def read_conf(self):
        print 'we are reading the peakFit_conf cnf file!'
        self.areaSrc = self.configListStr('areaSrc')
        self.areaROI = self.configListInt('areaROI')
        self.areaProj = self.configInt('areaProj', 0)
        self.areaSaveProj = self.configBool('areaSaveProj', False)        
        self.peakWindow = self.configListInt('peakWindow')
        self.peakNmax = self.configInt('peakNmax',10)
        self.debug  = self.configBool('debug',False)

        if (len(self.areaSrc)>0):
            self.parName = '_Peak'
            for iPar in self.areaROI:
                self.parName+='_%i'%(iPar)
      
    def beginjob(self, evt, env):
      self.time_begin = time.time()
      print 'time init :%.2f'%(self.time_begin - self.time_init)
      if self.debug:
        print '*** here in beginjob'

      if self.debug:
        print 'time begin :%.2f'%(self.time_begin_done - self.time_begin)
      self.time_int = 0
      self.time_begin_done = time.time()
      
    def beginrun(self, evt, env):
        self.ncalib=0
        self.read_conf()
        if self.debug:
            print 'found run number',evt.run()                                
            
    def begincalibcycle(self, evt, env):
      if self.debug:
        print '*** here in begincalib'
        if self.ncalib==0 and self.MaskFile!='' and self.mask.sum()>0:
          env.configStore().put(self.mask.astype(float), (self.areaSrc[0]+self.parName+'_area_mask'))
      self.ncalib+=1

    def event(self, evt, env):
      if self.counter < 100:
        self.printFreq = 10
      elif self.counter < 1000:
        self.printFreq = 100
      elif self.counter < 10000:
        self.printFreq = 1000
      else:
        self.printFreq = 10000
        
      start_time_int = time.time()

      areaSrc = Source(self.areaSrc[0])
      if getImg(evt, self.areaSrc) is None:
          #print 'IM not found'
          #for key in evt.keys():
          #    print key
          if self.debug or self.eventNr<5:
              print 'no area detector image in xpp_peakFit, will return'
          return

      if len(self.areaROI)>1 and not (self.areaSrc[0].find('cs')>=0 or self.areaSrc[0].find('Cs')>=0):
          areaImg = getImg(evt, self.areaSrc, self.areaROI).copy()
      else:
          areaImg = getImg(evt, self.areaSrc).copy()
      if self.counter%self.printFreq == 0:
        print 'xpp_peakFit: event: ',self.counter,' in rank: ',rank,' of ',size
      self.counter += 1

      #projection
      if (self.areaProj%1==0):
          proj = np.sum(areaImg,0)
      else:
          proj = np.sum(areaImg,1)
      if (self.areaSaveProj):
          evt.put(proj,areaSrc,(self.parName+'_proj'))

      #now fit peaks.
      peakDat = proj
      mean=[]
      sigma=[]
      height=[]
      fitPeaks(peakDat, self.peakWindow, mean, sigma, height, showPlot=False)
      for i in range(self.peakNmax):
          mean.append(-1)
          sigma.append(-1)
          height.append(-1)
      means = np.array(mean[:self.peakNmax])
      sigmas = np.array(sigma[:self.peakNmax])
      heights = np.array(height[:self.peakNmax])

      evt.put(means,areaSrc,(self.parName+'_means'))
      evt.put(sigmas,areaSrc,(self.parName+'_sigmas'))
      evt.put(heights,areaSrc,(self.parName+'_heights'))
          
      #image integral for normalization
      self.time_int += (time.time() - start_time_int)

            
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

      print 'time for peak fitting : %.2f '%(self.time_int)
      print 'time to end : %.2f'%(self.time_end - self.time_begin_done)
