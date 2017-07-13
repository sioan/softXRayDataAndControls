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
from cspad import CspadPattern
from cspad import get_cspad_pixel_coordinates
import azimuthalAveraging as aa
import azimuthalBinning as ab
from PyCSPadImage.CalibPars import  findCalibFile
from ixppy.cspad import commonModeCorrectImg
from ixppy.cspad import commonModeCorrectTile
from ixppy.cspad import maskEdges
from ixppy.cspad import createMaskUnbonded
from matplotlib import pyplot as plt

class xpp_anaRad(object):
    def __init__(self):

        self.xray_off_code = 162
        self.MaskEdge = 5

        self.read_conf()
        
        self.printFreq = 1000

        if self.debug:
          print '*** here in new init'

        self.time_init = time.time()
        self.counter = 0

    def read_conf(self):
        print 'we are reading the cnf file!'
        self.officialCal  = self.configBool('officialCal',True)
        self.MaskEdge = self.configListInt('MaskEdge')
        self.MaskUnbonded = self.configListBool('MaskUnbonded')
        self.MaskFile  = self.configStr('MaskFile','')
        self.DarkFile  = self.configStr('DarkFile','xxx')
        self.commonMode  = self.configBool('commonMode',False)
        self.commonModeArray  = self.configBool('commonModeArray',True)
        self.gainAv  = self.configFloat('gainAv',40.)
        self.threshold  = self.configInt('threshold',0)
        self.thresholdVal  = self.configFloat('thresholdVal',0.1)
        
        self.xcen  = self.configFloat('xcen',93458.)
        self.ycen  = self.configFloat('ycen',93955.)
        self.pixel  = self.configFloat('pixel',100e-06)
        self.dis_to_sam  = self.configFloat('dis_to_sam',0.1)
        self.eBeam  = self.configFloat('eBeam',9.)
        self.qBin   = self.configFloat('qBin',1e-2)
        self.phiBin  = self.configListInt('phiBin')
        self.debug  = self.configBool('debug',False)
        self.keyStr  = self.configStr('keyStr','')

        self.cspad_src = Source('cspad')
      
        
      
    def beginjob(self, evt, env):
      self.time_begin = time.time()
      print 'time init :%.2f'%(self.time_begin - self.time_init)
      if self.debug:
        print '*** here in beginjob'

      #now deal with mask files and pedestals:
      self.myMask = None
      self.myDark = None
      if self.MaskFile!='':
        print 'we read our own MASK file'
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

      if self.DarkFile is not 'xxx':
        print 'we read our own DARK file'
        if self.DarkFile.find('npy')>0:
          self.myDark = np.load(self.DarkFile)
        else:
          self.myDark = np.loadtxt(self.DarkFile)
      
      print 'we look for the official files.'
      dir = '/reg/d/psdm/xpp/'+env.experiment()+'/calib/CsPad::CalibV1/XppGon.0:Cspad.0/'
      #need to use proper file getting here.
      nname = findCalibFile(dir,type='pixel_rms',run=evt.run())
      cname = findCalibFile(dir,type='pixel_status',run=evt.run())
      dname = findCalibFile(dir,type='pedestals',run=evt.run())
      tempmask = (np.loadtxt(cname)).astype(np.bool)
      tempdark = np.loadtxt(dname)
      tempnoise = np.loadtxt(nname)
      Ntiles = 32
      self.noise = np.zeros([Ntiles,185,388])
      self.mask = np.zeros([Ntiles,185,388])
      self.dark0av = np.zeros([Ntiles,185,388])
      for i in range(0,Ntiles):
          self.noise[i] = tempnoise[i*185:(i+1)*185,:]
          self.mask[i] = tempmask[i*185:(i+1)*185,:]
          self.dark0av[i] = tempdark[i*185:(i+1)*185,:]
      if self.debug:
          print 'calibrun masked ',self.mask.sum(),' pixels'

      if (self.MaskEdge[0]>0):
          #print 'mask shape: ',self.mask.shape
          maskmid = True
          if len(self.MaskEdge)>1:
              maskmid = (self.MaskEdge[1]==1)
          #maskmid=True is default
          maskedg = maskEdges(Ntiles,offset=self.MaskEdge[0], maskmid=maskmid)
          self.mask = np.logical_or(self.mask,maskedg)
          if self.debug:
              print 'calibrun+edge masked ',self.mask.sum(),' pixels'
      if (self.MaskUnbonded[0]>0 and len(self.MaskUnbonded)>1):          
          maskub = createMaskUnbonded(Ntiles, maskDirectNeighbors=self.MaskUnbonded[1])
          self.mask = np.logical_or(self.mask,maskub)
          if self.debug:
              print 'calibrun+edge+unbonded masked ',self.mask.sum(),' pixels'
        
      #if we have specified a dark, then use that.
      if self.myDark is not None:
        self.dark0av = self.myDark

      #if we have specified a mask, then use that & default mask
      if self.myMask is not None:
          if self.myMask.shape != self.mask.shape:
              print 'input mask and default mask to not have the same shape, I will not add them'
          else: #or them as bad means "1"
              print 'add my mask to offical calibration mask (w. edges)'
              if (self.mask.view(bool).shape==self.mask.shape):
                  self.mask = np.logical_or(self.mask.view(bool),self.myMask.view(bool))
              else:
                  redFac = self.mask.view(bool).shape[-1]/self.mask.shape[-1]
                  self.mask = np.logical_or(self.mask.view(bool)[:,:,::redFac],self.myMask.view(bool))
      else:
          if (self.mask.shape[-1] == self.mask.view(bool).shape[-1]):
              self.mask = self.mask.view(bool)
          else:
              redFac = self.mask.view(bool).shape[-1]/self.mask.shape[-1]
              self.mask = self.mask.view(bool)[:,:,::redFac]

      if self.debug:
        print 'mask shape: ', self.mask.shape,' dtype ', self.mask.dtype
        print 'dark shape: ', self.dark0av.shape,' dtype ', self.dark0av.dtype
      #for i in range(0,32):
      #  print '--MASK: ',self.mask[i]
        
      xpx, ypx, zpx = get_cspad_pixel_coordinates(expname=env.experiment())
      xpx = xpx.reshape(32, 185,388)
      ypx = ypx.reshape(32, 185,388)
    
      if (self.eBeam <=0):
        if (env.epicsStore()).value("SIOC:SYS0:ML00:AO627") is not None:
          eBeam = (env.epicsStore()).value("SIOC:SYS0:ML00:AO627")
          if self.debug:
            print 'use ebeam 627'
        #worse, but if 627 is not there:
        else:
          if (env.epicsStore()).value("SIOC:SYS0:ML00:AO541") is not None:
            eBeam = (env.epicsStore()).value("SIOC:SYS0:ML00:AO541")
            if self.debug:
              print 'did not find ebeam 627, use ebeam 541'
          else:
            if self.debug:
              print 'no information about eBeam, will quit'
            self.stop()
            return

      if self.debug:
          print 'xpp_anaRad: create azimuthalBinning code',
          print 'Masked %d pixels.' %np.sum(self.mask)
        #Pplane set to 1 as default for binning is 0, for Azav it is 1.
      self.ao = ab.azimuthalBinning(x=xpx/1e3,y=ypx/1e3,xcen=self.xcen/1e3,ycen=self.ycen/1e3,d=self.dis_to_sam,mask=self.mask,lam=E2lam(self.eBeam)*1e10,Pplane=1,phiBins=self.phiBin[0],qbin=self.qBin)
      if self.phiBin[0]>1 and len(self.phiBin) > 1 and self.phiBin[1]>0:
          #1-d integration also, default phiBin to 1.
          self.ao1d = ab.azimuthalBinning(x=xpx/1e3,y=ypx/1e3,xcen=self.xcen/1e3,ycen=self.ycen/1e3,d=self.dis_to_sam,mask=self.mask,lam=E2lam(self.eBeam)*1e10,Pplane=1,qbin=self.qBin)


      self.time_begin_done = time.time()
      if self.debug:
        print 'time begin :%.2f'%(self.time_begin_done - self.time_begin)
      self.time_int = 0
      
    def beginrun(self, evt, env):
        self.ncalib=0
        self.read_conf()
        if self.debug:
            print 'found run number',evt.run()                                
        
    def begincalibcycle(self, evt, env):
      if self.debug:
          print '*** here in begincalib'
      if self.ncalib==0:
          env.configStore().put(self.ao.q, "cspadAzAv_q")
          env.configStore().put(self.mask.astype(float), "cspadAzAv_mask")
          env.configStore().put(self.ao.correction, "cspadAzAv_correction")
          env.configStore().put(self.ao.norm, "cspadAzAv_norm")
          if self.phiBin[0] > 1:
              env.configStore().put(self.ao.Cake_norm, "cspadAzAv_2dnorm")
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
      if (self.officialCal):
        cspad = evt.get(CsPad.DataV2, self.cspad_src,'calibrated')
      else:
        #raw event here...
        cspad = evt.get(CsPad.DataV2, self.cspad_src)

      if cspad is None:
        if self.debug:
          print 'no Cspad...'
          #for key in evt.keys():
          #    print key
        return

      if self.counter%self.printFreq == 0:
        print 'xpp_anaRad: event: ',self.counter,' in rank: ',rank,' of ',size

      self.counter += 1
      data_ar = (cspad.quads(0)).data()
      for i in range(1,cspad.quads_shape()[0]):
        data_ar = np.append(data_ar,(cspad.quads(i)).data(),axis=0)
      if not self.officialCal:
        data_ar -= self.dark0av

      #common mode
      if self.commonMode:
        self.time_begin_cm = time.time()
        if not self.commonModeArray:
            if self.debug:
                print 'use image correction straight from ixppy, no mask'
            data_ar = commonModeCorrectImg(data_ar,mask=self.mask.view(bool),gainAv=self.gainAv)
            #data_ar = commonModeCorrectImg(data_ar,mask=None,gainAv=self.gainAv)
        else:
            commonModeCorr=[]
            for tNo,tile in enumerate(data_ar):
                if self.mask is None:
                    tmask=None
                else:
                    tmask = self.mask[tNo]
                tile,bg = commonModeCorrectTile(tile,mask=tmask,gainAv=self.gainAv,nbSwitchFactor=3,unbPx=None)
                commonModeCorr.append(bg)
            evt.put(np.array(commonModeCorr),self.cspad_src,self.keyStr+'commonModeCorr')
        if self.debug:
            print 'time CM/evt :%.2f'%(time.time() - self.time_begin_cm)

      #thresholding
      if self.threshold != 0:
          if abs(self.threshold) == 1:
              data_ar[data_ar<self.thresholdVal*self.gainAv]=0
          else:
              data_ar[data_ar<self.thresholdVal*self.noise]=0
      if self.threshold<0:
        data_ar[data_ar>0]=1
        
      #average
      if self.phiBin[0] == 1:
        self.I = self.ao.doAzimuthalAveraging(data_ar)
      else:
        self.I = self.ao.doCake(data_ar)
        if len(self.phiBin)>1 and self.phiBin[1]>0:
          self.I1d = self.ao.doAzimuthalAveraging(data_ar)
      evt.put(self.I.flatten(),self.cspad_src,self.keyStr+'azimuthalInt')
      if len(self.phiBin)>1 and self.phiBin[1]>0:
        evt.put(self.I1d.flatten(),self.cspad_src,self.keyStr+'azimuthalInt1d')

      if self.debug and self.counter < 2:
        print 'az average, shape: ',self.I.shape, ' av: ',self.I
      #np.save("IntRes_offCalib_"+str(self.counter),self.I)
      shapeAr = (np.array(self.I.shape)).view(float)
      if self.debug and self.counter < 5:
        print 'i shape: ',self.I.shape,'  ',shapeAr
      if self.counter==0:
          env.configStore().put(shapeAr,'cspadAzAv_'+self.keyStr+'azimuthalIntDim')

      #image integral for normalization
      #average of the azimuthal averaged array
      data_ar_int = np.array([np.sum(data_ar),np.average(self.I) ])
      if self.debug:
          print 'masked_int: data ',data_ar.shape,' mask ',self.mask.shape,' mask_view_bool ',self.mask.view(bool).shape,' mask_astype_bool ',self.mask.astype(bool).shape
      masked_int = np.sum(data_ar[self.mask])
      nansum_av = np.nansum(self.I)/self.I.shape[0]
      data_ar_int_mask = np.array([masked_int, nansum_av])
      if self.debug and self.counter%self.printFreq == 0:
        print 'cspad_array: ',data_ar_int[0],' ',data_ar_int_mask
        print 'average average: ',data_ar_int[1],' ',np.sum(self.I)/self.I.shape[0], ' ',np.nansum(self.I)/self.I.shape[0]
      evt.put(data_ar_int,self.cspad_src,self.keyStr+'sum_intav')
      evt.put(data_ar_int_mask,self.cspad_src,self.keyStr+'sum_intav_mask')
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
