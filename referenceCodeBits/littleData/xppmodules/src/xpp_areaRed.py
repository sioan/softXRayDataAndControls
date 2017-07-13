import sys
import os
#p = ["./psanamon","./xppmodules/src/cspad","./xppmodules/src/cspad/alignment"]
#for pi in p:
#  if not (pi in sys.path): sys.path.append(pi)

import sys
sys.path.insert(1,'/reg/common/package/mpi4py/mpi4py-1.3.1/install/lib/python')
sys.path.insert(1,'/reg/g/xpp/xppcode/python')
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
from PyCSPadImage.CalibPars import  findCalibFile
import RegDB.experiment_info
from ixppy.cspad import commonModeCorrectImg
from ixppy.cspad import commonModeCorrectTile
from matplotlib import pyplot as plt

class xpp_areaRed(object):
    def __init__(self):

        self.edgeMask = 5

        self.read_conf()
        
        self.printFreq = 1000

        if self.debug:
          print '*** here in new init'

        self.time_init = time.time()
        self.counter = 0

    def read_conf(self, env=None):
        print 'we are reading the areaRed_conf cnf file!'
        self.areaName = self.configStr('areaName','area')
        self.areaSrc = self.configListStr('areaSrc')
        self.areaROI = self.configListInt('areaROI')
        self.areaSaveProj = self.configInt('areaSaveProj', -1)
        self.areaSaveROI = self.configBool('areaSaveROI', False)

        self.edgeMask = self.configInt('MaskEdge',5)
        self.MaskFile  = self.configStr('MaskFile','')
        self.DarkFile  = self.configStr('DarkFile','')
        self.commonMode  = self.configBool('commonMode',False)
        self.commonModeArray  = self.configBool('commonModeArray',True)
        self.gainAv  = self.configFloat('gainAv',40.)
        self.threshold  = self.configInt('threshold',0)
        self.thresholdVal  = self.configFloat('thresholdVal',0.1)
        
        self.debug  = self.configBool('debug',False)

        if self.areaName!='area':
            if self.areaName != '':
                self.parName = self.areaName+'_'
            else:
                self.parName = self.areaName
        else:
            if (len(self.areaSrc)>0):
                self.parName = '_ROI'
                for iPar in self.areaROI:
                    self.parName+='_%i'%(iPar)

        self.expname = 'None'
        if env is not None:
            if (env.jobName()).find('shmem')>=0:
                self.expname = RegDB.experiment_info.active_experiment('XPP')[1]
            else:
                self.expname=env.experiment()

    def readDetCalib(self, evt):
        self.noise = None
        #if area detector is cspad or cs140, deal with mask files and pedestals:
        if self.areaSrc[0].find('cs')>=0 or  self.areaSrc[0].find('Cs')>=0:
          
            self.myMask = None
            self.myDark = None
            if self.MaskFile!='':
                print 'we read our own MASK file (works only for big cspad for now)'
                print self.MaskFile 
                if self.MaskFile.find('npy')>0:
                    self.myMask = np.load(self.MaskFile)
                    print '####  FOUND NPY MASK   ########'
                else:
                    self.myMask = (np.loadtxt(self.MaskFile)).astype(np.bool)
                #and now make this 32:185:388 the correct way and then invert.
                if len(self.myMask.shape)==2 and self.myMask.shape[0]==32:
                    self.myMask = np.array( [np.transpose(np.resize(thisAsic,(388,185))) for thisAsic in self.myMask])
                    self.myMask = ~self.myMask
                elif not self.myMask.shape == (32, 185, 388):
                    print 'this mask file does not have the correct shape: implment this!'
                    self.stop()

            if self.DarkFile is not '':
                print 'we read our own DARK file'
                if self.DarkFile.find('npy')>0:
                    self.myDark = np.load(self.DarkFile)
                else:
                    self.myDark = np.loadtxt(self.DarkFile)
      
            print 'we look for the official files.'
            is140k=False
            if self.areaSrc[0].find('140')>=0 or  self.areaSrc[0].find('2x2')>=0:
                is140k=True
                self.noise = np.zeros([185,388,2])
                self.mask = np.zeros([185,388,2])
                self.dark0av = np.zeros([185,388,2])
                dir = '/reg/d/psdm/xpp/'+self.expname+'/calib/CsPad2x2::CalibV1/XppGon.0:Cspad2x2.0/'
            else:
                #works if we only have one 2x2. figure other stuff out later.
                self.noise = np.zeros([32,185,388])
                self.mask = np.zeros([32,185,388])
                self.dark0av = np.zeros([32,185,388])
                dir = '/reg/d/psdm/xpp/'+self.expname+'/calib/CsPad::CalibV1/XppGon.0:Cspad.0/'
            #check that directory actually exists!
            if (os.path.isdir(dir)):
                runnr = evt.run()
                if runnr > 9999:
                    runnr=9999
                nname = findCalibFile(dir,type='pixel_rms',run=runnr)
                cname = findCalibFile(dir,type='pixel_status',run=runnr)
                dname = findCalibFile(dir,type='pedestals',run=runnr)
                tempmask = (np.loadtxt(cname)).astype(np.bool)
                tempdark = np.loadtxt(dname)
                tempnoise = np.loadtxt(nname)
                if not is140k:
                    for i in range(0,32):
                        self.noise[i] = tempnoise[i*185:(i+1)*185,:]
                        self.mask[i] = tempmask[i*185:(i+1)*185,:]
                        self.dark0av[i] = tempdark[i*185:(i+1)*185,:]
                        if (self.edgeMask>0):
                            for i in self.mask:
                                i[:self.edgeMask,:]=True
                                i[:,:self.edgeMask]=True
                                i[:,-self.edgeMask:]=True
                                i[-self.edgeMask:,:]=True
                  #data looks like(185, 388, 2)
                else:
                    self.noise = tempnoise.reshape(185, 388, 2)
                    self.mask = tempmask.reshape(185, 388, 2)
                    self.dark0av = tempdark.reshape(185, 388, 2)
            else:
                print 'Calibration directory for detector requested in xpp_areaRed not found!'
                print 'will not apply mask, dark, .....'
              
            #if we have specified a dark, then use that.
            if self.myDark:
                self.dark0av = self.myDark

            #if we have specified a mask, then use that & default mask
            if self.myMask is not None:
                if self.myMask.shape != self.mask.shape:
                    print 'input mask and default mask to not have the same shape, I will not add them'
                else: #or them as bad means "1"
                    self.mask = np.logical_or(self.mask,self.myMask)

            if self.debug:
                print 'mask shape: ', self.mask.shape
                print 'dark shape: ', self.dark0av.shape
          #for i in range(0,32):
          #  print '--MASK: ',self.mask[i]


    def beginjob(self, evt, env):
      self.time_begin = time.time()
      print 'time init :%.2f'%(self.time_begin - self.time_init)
      if self.debug:
        print '*** here in beginjob'

      #put this in function later, fill mask, dark, noise file arrays for each detector
        
      self.time_begin_done = time.time()
      if self.debug:
        print 'time begin :%.2f'%(self.time_begin_done - self.time_begin)
      self.time_int = 0
      
    def beginrun(self, evt, env):
        self.ncalib=0
        self.read_conf(env)
        self.readDetCalib(evt)
        if self.debug:
            print 'found run number',evt.run()                                
            

    def begincalibcycle(self, evt, env):
      if self.debug:
        print '*** here in begincalib'
      if self.ncalib==0:
          if self.MaskFile!='' and self.mask.sum()>0:
              env.configStore().put(self.mask.astype(float), (self.areaSrc[0]+self.parName+'_area_mask'))
          env.configStore().put(np.array(self.areaROI), (self.areaSrc[0]+self.parName+'_areaROI'))

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
      self.counter += 1

      if getImg(evt, self.areaSrc) is None:
          #for key in evt.keys():
          #    print key
          if self.debug:
              print 'no area detector image in xpp_areaRed'
          #here we need to append np.nan arrays to the event!
          evt.put(np.array([np.nan]),areaSrc,(self.parName+'int'))
          evt.put(np.array([np.nan]),areaSrc,(self.parName+'comX'))
          evt.put(np.array([np.nan]),areaSrc,(self.parName+'comY'))
          if len(self.areaROI)==2:          
              imgAr = np.empty((self.areaROI[1]-self.areaROI[0])) 
          elif len(self.areaROI)==4:
              imgAr = np.empty((self.areaROI[1]-self.areaROI[0], self.areaROI[3]-self.areaROI[2] )) 
          elif len(self.areaROI)==6:
              imgAr = np.empty((self.areaROI[1]-self.areaROI[0], self.areaROI[3]-self.areaROI[2], self.areaROI[5]-self.areaROI[4]  )) 
          imgAr[:] = np.nan
          if imgAr is not None:
              areaImg = np.squeeze(imgAr)
          #subarea to save
          if self.areaSaveROI:
              evt.put(areaImg,areaSrc,(self.parName+'ROIarea'))
          #projection
          xproj = np.sum(areaImg,0)
          yproj = np.sum(areaImg,1)
          if (self.areaSaveProj>0 and self.areaSaveProj%2==0):
              evt.put(xproj,areaSrc,(self.parName+'xproj'))
          if (self.areaSaveProj>0 and self.areaSaveProj%3==0):
              evt.put(yproj,areaSrc,(self.parName+'yproj'))

          return

      if len(self.areaROI)>1 and not (self.areaSrc[0].find('cs')>=0 or self.areaSrc[0].find('Cs')>=0):
          areaImg = getImg(evt, self.areaSrc, self.areaROI).copy()
      else:
          areaImg = getImg(evt, self.areaSrc).copy()
      
      if self.counter%self.printFreq == 0:
          if self.debug:
              print 'xpp_areaRed: event: ',self.counter,' in rank: ',rank,' of ',size
          elif rank==0:
              print 'xpp_areaRed: event: ',self.counter,' in rank: ',rank,' of ',size

      #if we have a cspad detector, 
      if self.areaSrc[0].find('cs')>=0 or self.areaSrc[0].find('Cs')>=0:
          #do own calibration
          if len(self.areaSrc)==1:
              areaImg = areaImg.astype(float) - self.dark0av
              
          #common mode
          if self.commonMode:
              self.time_begin_cm = time.time()
              if not self.commonModeArray:
                  if self.debug:
                      print 'use image correction straight from ixppy, no mask'
                  areaImg = commonModeCorrectImg(areaImg,mask=self.mask.view(bool),gainAv=self.gainAv)
              else:
                  commonModeCorr=[]
                  if self.areaSrc[0].find('140')>=0 or  self.areaSrc[0].find('2x2')>=0:                  
                      for tNo in zip(range(0,2)):
                          if self.mask is None:
                              tmask=None
                          else:
                              tmask = self.mask[:,:,tNo].view(bool)
                          tile,bg = commonModeCorrectTile(areaImg[:,:,tNo],mask=tmask,gainAv=self.gainAv,nbSwitchFactor=3,unbPx=None)
                          commonModeCorr.append(bg)
                  else:
                      for tNo,tile in enumerate(areaImg):
                          if self.mask is None:
                              tmask=None
                          else:
                              tmask = self.mask[tNo].view(bool)
                          tile,bg = commonModeCorrectTile(tile,mask=tmask,gainAv=self.gainAv,nbSwitchFactor=3,unbPx=None)
                          commonModeCorr.append(bg)
                  evt.put(np.array(commonModeCorr),areaSrc,(self.parName+'commonModeCorr'))
              if self.debug:
                  print 'time CM/evt :%.2f'%(time.time() - self.time_begin_cm)

          #read in a ROI as for e.g. peak - still cspad only
          area_crop = None
          if len(self.areaROI)==2:          
              area_crop = areaImg[self.areaROI[0]:self.areaROI[1]]
          elif len(self.areaROI)==4:
              area_crop = areaImg[self.areaROI[0]:self.areaROI[1],self.areaROI[2]:self.areaROI[3]]
          elif len(self.areaROI)==6:
              area_crop = areaImg[self.areaROI[0]:self.areaROI[1],self.areaROI[2]:self.areaROI[3],self.areaROI[4]:self.areaROI[5]]
              if area_crop is not None:
                  areaImg = np.squeeze(area_crop)

      #thresholding
      if self.threshold != 0:
          if abs(self.threshold) == 1:
              areaImg[areaImg<self.thresholdVal*self.gainAv]=0
          elif self.noise is not None and self.noise.shape==areaImg.shape:
              areaImg[areaImg<self.thresholdVal*self.noise]=0
      if self.threshold<0:
        areaImg[areaImg>0]=1

      #total integral
      ROIint = np.sum(areaImg).astype(float)
      evt.put(np.array([ROIint]),areaSrc,(self.parName+'int'))

      #projection
      xproj = np.sum(areaImg,0).astype(float)
      yproj = np.sum(areaImg,1).astype(float)
      if (self.areaSaveProj>0 and self.areaSaveProj%2==0):
          evt.put(xproj,areaSrc,(self.parName+'xproj'))
      if (self.areaSaveProj>0 and self.areaSaveProj%3==0):
          evt.put(yproj,areaSrc,(self.parName+'yproj'))

      #center-of-mass
      x=np.arange(areaImg.shape[1])
      y=np.arange(areaImg.shape[0])
        
      com_x = np.sum(xproj*x).astype(float)/np.sum(xproj).astype(float)
      com_y = np.sum(yproj*y).astype(float)/np.sum(yproj).astype(float)
      evt.put(np.array([com_x]),areaSrc,(self.parName+'comX'))
      evt.put(np.array([com_y]),areaSrc,(self.parName+'comY'))

      #subarea to save
      if self.areaSaveROI:
          evt.put(copy.deepcopy(areaImg.astype(float)),areaSrc,(self.parName+'ROIarea'))
      
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

      print 'time for area reduction : %.2f '%(self.time_int)
      print 'time to end : %.2f'%(self.time_end - self.time_begin_done)
