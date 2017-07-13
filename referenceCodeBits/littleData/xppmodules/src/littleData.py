import os
import copy
import numpy as np
import h5py
import fnmatch

from matplotlib import pyplot as plt
from utilities import pumpprobe_status
from utilities import E2lam
from utilities import rebin
from utilities import cm_epix
from DetObject import DetObject
#import azimuthalBinning as ab
#import droplet as droplet
import xtcav.ShotToShotCharacterization as Xtcav  
from littleDataUtils import dropObject

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
mpiSize = comm.Get_size()

import psana
from collections import Counter
#import time


def addToObj(obj,name,value,overWrite=True,ixpsaved=False, setParent=True):
  """ Functions to add things to an object create intermediate dropObject if 
  necessary
  usage:
  from a class you could call addToObj(self,"p1.p2.p3.a1",np.arange(10))
  p1 p2 and p3 will be dropObject and a1 an attribute of p3 with value np.arange(10)
  given an instance (for example data) of a class another use is addToObj(data,...)
  """
  temp = name
  where = obj
  while (temp.find(".")>0):
    parent = temp[0:temp.find(".")]
    if parent not in where.__dict__:
      where.__dict__[parent] = dropObject(name=parent,parent=where)
    where =  where.__dict__[parent]
    temp = temp[temp.find(".")+1:]
  if ( (temp not in where.__dict__) or overWrite ):
    where.__dict__[temp] = value
    if setParent:
      try:
        where.__dict__[temp]._parent = where
      except:
	pass
  return obj

def existsInObj(obj,name):
  temp = name
  where = obj
  while (temp.find(".")>0):
    parent = temp[0:temp.find(".")]
    if (parent in where.__dict__):
      where =  where.__dict__[parent]
      temp = temp[temp.find(".")+1:]
    else:
      return False
  return (temp in where.__dict__)

def getFromObj(obj,name):
  temp = name
  where = obj
  while (temp.find(".")>0):
    parent = temp[0:temp.find(".")]
    if (parent in where.__dict__):
      where =  where.__dict__[parent]
      temp = temp[temp.find(".")+1:]
      return where.__dict__[temp]
    else:
      print name, ' not found'
      return None
  if (temp in where.__dict__):
    return where.__dict__[temp]
  else:
    return None

def gatherLittleData(ld, fname = None):
  fh5 = None
  if fname is not None and rank==0:
    fh5 = h5py.File(fname, "w")

  KeysWrittenAsInt = ['EvtID/time','lightStatus/laser','lightStatus/xray']

  ldGather = littleData()
  keys = ld.getKeys()

  for key in keys:
    mysend = ld.ndarray(key.replace('/','.')).flatten()
    lengths = np.array(comm.gather(len(mysend)))
    if len(lengths.shape)<1 or lengths.shape[0]<mpiSize:
      lengths = np.zeros(mpiSize).astype(int)
    comm.Bcast(lengths, root=0)
  
    #make this bigger to effectively disable currently broken slicing.
    maxSize=1024*1024*1024*1024
    #maxSize=1024*1024*1024
    #maxSize=100*1024*1024

    nSplit = np.ceil(sum(lengths)/maxSize)
    #print 'for key ',key,' we have length ',sum(lengths),' split into ',nSplit
    if nSplit==0:
      #print 'to small....set to 1(no splitting) ',nSplit,  sum(lengths)/maxSize, '++++', maxSize#, sum(lengths)
      nSplit=1
      
    myFullArray = ld.ndarray(key.replace('/','.'))
    #change code to split at first non event axis
    totalRecv=[]
    totalNevts=0
    totalSize=0
    myObj=None
    if len(myFullArray.shape)>1:
      singleLength=np.ceil(myFullArray.shape[1]/nSplit)
      #print 'rank ',rank,' single length: ',key,singleLength,myFullArray.shape[1]/nSplit,' -- ',myFullArray.shape[1],nSplit
    else:
      singleLength=None
    for iSplit in range(int(nSplit)):
      if nSplit==1 or singleLength==None:
        mySubArray = myFullArray
      elif iSplit<nSplit-1:
        mySubArray = myFullArray[:,iSplit*singleLength:(iSplit+1)*singleLength]
        print '***array ',iSplit,' for ', key, 'full ',myFullArray.shape, 'sub ',mySubArray.shape,' rank ',rank
      else:
        mySubArray = myFullArray[:,iSplit*singleLength:]
        print '***lastarray for ', key, 'full ',myFullArray.shape, ' sub ',mySubArray.shape,' rank ',rank
        
      mysend = mySubArray.flatten()
      lengths = np.array(comm.gather(len(mysend))) # get list of lengths
      
      myrecv = None
      if mysend.dtype=='float32':
        mysend = mysend.astype('float64')
        mysend.dtype='float64'
          #if mysend.dtype=='uint16':
          #  mysend = mysend.astype('float64')
          #  mysend.dtype='float64'
      if rank==0:
        #shape = ld.ndarray(key.replace('/','.'))[0].shape
        shape = mySubArray[0].shape
        size = sum(lengths)
        nEvts = size
        for shp in shape:
          nEvts /= shp
            #this will not work if mysend is int array with a nan -> myrecv will be float if nan present and int otherwise.
        myrecv = np.empty(size,mysend.dtype) # allocate receive buffer
      comm.Barrier()
      comm.Gatherv(sendbuf=mysend.flatten(), recvbuf=[myrecv, lengths])
      if rank==0:
        if nSplit>1:
          print key,' myrecv: ',myrecv.shape, mysend.flatten().shape,  ' after gather from lengths ',lengths

      if rank==0:
        if nSplit==1:
          #mysend=mysend.astype(float)
          if nEvts != size:
            new_shape = (nEvts,)+ shape
            myObj = myrecv.reshape(new_shape)
          else:
            myObj = myrecv
          #print 'adding ', key ,' to hdf5 with shape ', myObj.shape
        else:
          if nEvts == size:
            totalRecv.append(myrecv)
          else:
            new_shape = (nEvts,)+ shape
            print 'shapes: ',myrecv.shape,' ',new_shape,' iSplit ',iSplit
            totalRecv.append(myrecv.reshape(new_shape))
          if iSplit==nSplit-1:
            totalRecvAr=None
            for iso,splitObj in enumerate(totalRecv):
              if rank==0:
                if fh5 is None:
                  addToObj(ldGather, key.replace('/','.')+('_%d'%iso), splitObj)
                else:    
                  arShape=()
                  for i in range(0,len(splitObj.shape)):
                    arShape+=(splitObj.shape[i],)
                  #for debug, also save reassembled sub-arrays.
                  dset = fh5.create_dataset(key.append('_%d'%iso), arShape)
                  dset[...] = myObj.astype(float)

              if iso==0:
                totalRecvAr = splitObj
              else:
                #print 'shapes: ',totalRecvAr.shape,' ',splitObj.shape,' rank ',rank,' iSplit ',iSplit,' iso ',iso
                totalRecvAr = np.append(totalRecvAr, splitObj, axis=1)
              #print key,' build final object from these? rank ', rank, iSplit, ' object shape: ', splitObj.shape, ' iso ',iso, totalRecvAr.shape
              
            print 'adding ', key ,' to hdf5 after recombining with shape:', totalRecvAr.shape
            myObj = totalRecvAr
      
    if rank==0:
      if fh5 is None:
        addToObj(ldGather, key.replace('/','.'), myObj)
      else:    
        arShape=()
        for i in range(0,len(myObj.shape)):
          arShape+=(myObj.shape[i],)

        if key in KeysWrittenAsInt or key[:3]=='Evr':
          dset = fh5.create_dataset(key, arShape, dtype='int32')
          dset[...] = myObj
        elif fnmatch.fnmatch(key,'opal?/ROI') or fnmatch.fnmatch(key,'opal_?/ROI'):
          print 'found an opal', key
          dset = fh5.create_dataset(key, arShape, dtype='int32')
          dset[...] = myObj
        else:                            
          dset = fh5.create_dataset(key, arShape)
          dset[...] = myObj.astype(float)

  if fh5 is None:
    return ldGather
  else:
    return fh5
                
class arrayData(object):
  def __init__(self, keys=[], vals=[]):
    if len(keys) != len(vals):
      print 'different number of keys and values!',len(keys), len(vals)
      print 'keys: ',keys
      print 'vals: ',vals
    for numkey, key in enumerate(keys):
      self.__dict__[key]=[vals[numkey]]
  def add(self, dat):
    #check length of data & self!
    if isinstance(dat, self.__class__) and self.comp_keys(dat):
      for key in self._get_keys():
        self.__dict__[key].extend(dat.__dict__[key])
    else:
      print 'you cannot add ',dat,' to ',self
      print Counter(dat.printKeys())
      print ' versus '
      print Counter(self.printKeys())
      #try to apppend nan for array size matching
      for key in self._get_keys():
        self.__dict__[key].extend([np.nan])
      
  def printKeys(self):
    for tk in self._get_keys():
      print tk
  def _get_keys(self):
    return [tk for tk in self.__dict__.keys() if not tk[0]=='_']
  def comp_keys(self, dat):
    if dat._get_keys()==self._get_keys():
      return True
    if Counter(dat._get_keys())==Counter(self._get_keys()):
      return True
    return False

class littleData(object):
  def ndarray(self, mne, debug=False):
    dat = getFromObj(self,mne)
    if dat is None:
      return None
    if debug and len(dat)<1:
      print 'Huh?'
      return None
    if isinstance(dat[0], float) or isinstance(dat[0], int) or isinstance(dat[0], np.uint64) or isinstance(dat[0], tuple)  or isinstance(dat[0], np.ndarray) or isinstance(dat[0], np.float32):
      return np.array(dat)
    if isinstance(dat[0], list):
      if isinstance(dat[0][0], float) or isinstance(dat[0][0], int) or isinstance(dat[0][0], np.float32) :
        return np.array(dat)
    if isinstance(dat[0][0], np.float32):
      return np.array(dat)
    print 'not float or list ',mne
    return None

  def add(self, otherLittleDat):
    for key in self.__dict__.keys():
      self.__dict__[key].add(otherLittleDat.__dict__[key])

  def printKeys(self, debug=False):
    for obj in self.__dict__.keys():
      if debug:
        print 'obj: ',obj
      for key in self.__dict__[obj].__dict__.keys():
        if not key[0]=='_':
          print 'dataObjects: ',obj, key

  def getKeys(self):
    keyList=[]
    for obj in self.__dict__.keys():
      for key in self.__dict__[obj].__dict__.keys():
        if not key[0]=='_':
          keyList.append(obj+'/'+key)
    return keyList

  def writeToOutputFile(self, fh5, debug=False):
    print 'writing to output file'
    #writing all the user fields.
    if fh5.driver == 'mpio':
      print 'please call writeToOutputFile_mpi instead'
      return
    keys = self.getKeys()
    for key in keys:
      if debug:
        print key
      npAr = self.ndarray(key.replace('/','.'), debug=debug)
      npAr = npAr.squeeze()
      arShape=()
      for i in range(0,len(npAr.shape)):
        arShape+=(npAr.shape[i],)
      if  key.split('/')[0]=='EvtID':
        dset = fh5.create_dataset(key, arShape, dtype='int32')
        dset[...] = npAr
      elif key.split('/')[0]=='lightStatus' or key.split('/')[0]=='Evr':
        dset = fh5.create_dataset(key, arShape, dtype='i1')
        dset[...] = npAr
      elif key.split('/')[1]=='nDroplets' or key.split('/')[1]=='nPhotons' or key.split('/')[1]=='dropletsNpix':
        dset = fh5.create_dataset(key, arShape, dtype='i2')
        dset[...] = npAr
      elif key.split('/')[1].find('dropletsX')>=0 or key.split('/')[1].find('dropletsY')>=0:
        #i2 -> int16
        if npAr.dtype=='int64' or npAr.dtype=='int32': 
          dset = fh5.create_dataset(key, arShape, dtype='i2')
          dset[...] = npAr
        else:
          dset = fh5.create_dataset(key, arShape)
          dset[...] = npAr.astype(float)        
      elif key.split('/')[1].find('PixX')>=0 or key.split('/')[1].find('PixY')>=0:
          dset = fh5.create_dataset(key, arShape, dtype='i2')
          dset[...] = npAr
      elif fnmatch.fnmatch(key,'opal?/ROI') or fnmatch.fnmatch(key,'opal_?/ROI'):
        print 'found an opal', key
        dset = fh5.create_dataset(key, arShape, dtype='int16')
        dset[...] = npAr
      else:                            
        dset = fh5.create_dataset(key, arShape)
        dset[...] = npAr.astype(float)

  def setupHdf5File_mpi(self, fh5, currSize=100, debug=False,chunkSize=2048):
    #writing all the user fields.
    if fh5.driver != 'mpio':
      print 'please call writeToOutputFile instead!'
      return

    if debug:
      print 'setting up hdf5 file!'
    keys = self.getKeys()
    for key in keys:
        if debug:
          print 'setting up dataset for ',key
        npAr = self.ndarray(key.replace('/','.'), debug=debug)
        npAr = npAr.squeeze()
        maxShape=( None, )
        arShape=( currSize, )
        chunkSizeAr=max(1, int(chunkSize/(npAr.flatten().shape[0])))
        chunkShape=( chunkSizeAr, )
        for i in range(0,len(npAr.shape)):
          arShape+=(npAr.shape[i],)
          maxShape+=(npAr.shape[i],)
          chunkShape+=(npAr.shape[i],)
        dataType='f4'
        if key=='EvtID/time':
          dataType='i4'
        if key=='EvtID/fid':
          dataType='i4'
        elif key.split('/')[0]=='lightStatus' or key.split('/')[0]=='Evr':
          dataType='i1'
        elif key.split('/')[1].find('dropletsX')>=0 or key.split('/')[1].find('dropletsY')>=0:
          if npAr.dtype=='int64': 
            dataType='i4'
        elif key.split('/')[1].find('dropletsNpix')>=0:
            dataType='i2'
        elif key.split('/')[1]=='nDroplets' or key.split('/')[1]=='nPhotons':
           dataType='i2'
        elif key.split('/')[0].find('opal')>=0 and len(npAr.shape)>2:
          dataType='i16'
        dataset = fh5.create_dataset(key, arShape, dtype=dataType, maxshape=maxShape, chunks=chunkShape)

  def writeToOutputFile_mpi(self, fh5, currIdx, debug=False):
    if debug:
      print 'write %d to hdf5 file '%currIdx
    keys = self.getKeys()
    for key in keys:
        if debug:
          print 'looking at: ',key,currIdx
        npAr = self.ndarray(key.replace('/','.'), debug=debug)
        npAr = npAr.squeeze()
        try:
          fh5[key][currIdx] = npAr
          if debug:
            print 'written: ',key,currIdx
        except:
          print 'DEBUG: array ',key
          print 'pix array ',fh5[key].shape, currIdx
          print 'pix array ',fh5[key][currIdx].shape, npAr.shape
          print 'pix array ',fh5[key][currIdx].dtype, npAr.dtype
          print 'failed writing to file at event %d for key %s'%(currIdx, key)
          fh5[key][currIdx] = npAr
          print 'wrote'

def resizeHdf5File_mpi(fh5, numResize=100, debug=False):
  if fh5.driver != 'mpio':
    print' input hdf5 file doesn not have mpi driver!'
    return
  if debug:
    print 'resize hdf5 file!'
  
  for group in fh5.keys():
    for ds in fh5[group].keys():
      if debug:
        print 'resize: ',group,ds
      newShape = (numResize,)+fh5[group+'/'+ds].shape[1:]
      fh5[group+'/'+ds].resize(newShape)

#writing default config parameters: hardcode here for now.
def writeCfgToOutputFile(fh5, ldr):
    dset = fh5.create_dataset(('DataCfg/BeamOffCodes'), np.array(ldr.beamOffCodes).shape)
    dset[...] = np.array(ldr.beamOffCodes).astype(int)
    dset = fh5.create_dataset(('DataCfg/ttCalib'), np.array(ldr.ttCalib).shape)
    dset[...] = np.array(ldr.ttCalib).astype(float)

def getCfgOutput(detDropObject):
    cfgData=[]
    cfgKeyStrings=[]
    for key in detDropObject.__dict__.keys():
        if key == 'mask_ROI' or key == 'mask_ROI_shape':
            continue
        if isinstance(detDropObject[key], list) or isinstance(detDropObject[key], np.ndarray):
            cfgKeyStrings.append(detDropObject._name+'_'+key)
            if isinstance(detDropObject[key], list):
                cfgData.append(np.array(detDropObject[key]))
            elif isinstance(detDropObject[key], np.ndarray):
                cfgData.append(detDropObject[key])
    #now add ROI boundaries (so we can use mask, rms from main det object later....)
    for ROI in detDropObject.getROIs():
      cfgKeyStrings.append(detDropObject._name+'_'+ROI.name+'_bound')
      cfgData.append(np.array(ROI.bound))

    for drops in detDropObject.getDroplets():
      for aduHist in drops.aduHists:
        cfgKeyStrings.append(detDropObject._name+'_'+aduHist.name+'_bins')
        cfgData.append(np.array(aduHist.bins))
        
    return cfgData, cfgKeyStrings

def writeUserCfgToOutputFile(fh5, detDropObject, h5ds='UserDataCfg_psana/', debug=False):
    cfgData, cfgKeyStrings = getCfgOutput(detDropObject)
    if not len(cfgKeyStrings) == len(cfgData) :
      if debug:
        print 'len(cfgKeyStings) != len(cfgData) !'
      return
    for key,data in zip(cfgKeyStrings,cfgData):
      datShape=()
      for i in range(0,len(data.shape)):
        datShape+=(data.shape[i],)
      #print 'add dataset ',(h5ds+key)
      dset = fh5.create_dataset((h5ds+key), datShape)
      dset[...] = data.astype(float)

#should this go into analysis code and be imported from there?
def writeMicroAna(fh5, i0_string, sig_string, sig_ROI=None, cuts=[]):
  #get arrays in question
  ar_laser = fh5['lightStatus/laser'].value
  ar_i0 = fh5[i0_string].value
  ar_sig = fh5[sig_string].value
  if sig_ROI is not None:
    #TO BE DONE!
    ar_sig = ar_sig[sigROI] #see ar1d of analysis code.
  ar_scan = fh5['scan/var0'].value
  scanVar=''
  #now get scan variable name
  for key in fh5['scan'].keys():
    if key.find('var')<0 and key.find('none')<0:
      scanVar = key
  #look at ana code for treatment here.
  ar_delay = None
  if scanVar.find('lxt')>=0:
    ar_delay = fh5['scan/var0'].value*1e12+fh5['ttCorr/tt']
  #TO BE DONE: add code for new delay scan once settled.
  Filter = np.ones_like(ar_laser).astype(bool)
  #TO BE DONE!
  #also this take from analysis code.
  for cut in cuts:
    selvar = fh5[cut[0]]
    sel = selvar>=cut[1] & selvar<=cut[2]
  #now add the few dataset to the micro dataset
  #this dataset assume you have set up the analysis
  dset = fh5.create_dataset('micro/laser', ar_laser.shape)
  dset[...] = ar_laser[Filter].astype(bool)
  dset = fh5.create_dataset('micro/i0', ar_i0.shape)
  dset[...] = ar_i0[Filter].astype(float)
  dset = fh5.create_dataset('micro/sig', ar_sig.shape)
  dset[...] = ar_sig[Filter].astype(float)
  if ar_delay is not None:
    dset = fh5.create_dataset('micro/delay', ar_delay.shape)
    dset[...] = ar_scan[Filter].astype(float)
  elif scanVar!='':
    dset = fh5.create_dataset('micro/'+scanVar, ar_scan.shape)
    dset[...] = ar_scan[Filter].astype(float)

class littleDataReader(object):
    def __init__(self):
        if rank==0:
          print 'create little data reader....'
        self.accessors = dropObject()
        self.addAccessors()
        self.ttCalib = [ np.nan, np.nan ]
        self.ttDet = None
        self.ttROI = [[ np.nan, np.nan ],[ np.nan, np.nan ]]
        self.ttSaveRaw = False
        self.ipmSavePos = False
        self.aioInfo = [ [],[],[] ]
        self.encInfo = []
        xtcav_nb = 1 #number of bunches used for lasOffReference
        xtcav_size = 5000 #initial size of array
        self.xtcav = [ Xtcav.ShotToShotCharacterization(), False , xtcav_size, xtcav_nb]
        self.reqDet = []

    def addAccessors(self):
        self.accessors.ebeam = [True, psana.Source('BldInfo(EBeam)'), psana.Bld.BldDataEBeam]
        self.accessors.gdet = [True, psana.Source('BldInfo(FEEGasDetEnergy)'), [psana.Bld.BldDataFEEGasDetEnergyV1, psana.Bld.BldDataFEEGasDetEnergy] ]
        self.accessors.phasecav = [True, psana.Source('BldInfo(PhaseCavity)'), psana.Bld.BldDataPhaseCavity]
        self.accessors.l3t = [True, psana.Source('ProcInfo()'), [psana.L3T.DataV1, psana.L3T.DataV2]]
        #store as three time components (fid, sec, nanosec)
        self.accessors.EvtID = [True, 'EvtID', psana.EventId ]
        self.accessors.scan = [True, 'scan', ['var0', 'var1', 'var2'] ]
        self.accessors.epicsUser = [True, 'EPICS', []]
        self.accessors.Evr = [True, psana.Source('DetInfo(NoDetector.0:Evr.0)'), [psana.EvrData.DataV3, psana.EvrData.DataV4]]
        self.accessors.Xtcav = [False, psana.Source('DetInfo(XrayTransportDiagnostic.0:Opal1000.0)'), psana.Camera.FrameV1]

    def addAccessorsXPP(self):
        self.accessors.ipm1 = [True, psana.Source('BldInfo(NH2-SB1-IPM-01)'), psana.Lusi.IpmFexV1]
        self.accessors.ipm1c = [True, psana.Source('BldInfo(NH2-SB1-IPM-02)'), psana.Lusi.IpmFexV1]
        self.accessors.ipm2 = [True, psana.Source('BldInfo(XppSb2_Ipm)'), psana.Lusi.IpmFexV1]
        self.accessors.ipm3 = [True, psana.Source('BldInfo(XppSb3_Ipm)'), psana.Lusi.IpmFexV1]
        self.accessors.diode2 = [True, psana.Source('BldInfo(XppSb3_Pim)'), psana.Lusi.IpmFexV1]
        self.accessors.diode3 = [True, psana.Source('BldInfo(XppSb4_Ipm)'), psana.Lusi.IpmFexV1]
        self.accessors.diodeU = [True, psana.Source('BldInfo(XppEnds_Ipm0)'), psana.Lusi.IpmFexV1]
        self.accessors.lombpm = [True, psana.Source('BldInfo(XppMon_Pim0)'), psana.Lusi.IpmFexV1]
        self.accessors.lomdiode = [True, psana.Source('BldInfo(XppMon_Pim1)'), psana.Lusi.IpmFexV1]
        self.accessors.epics = [True, 'EPICS', ['SiAtt_T', 'SiAtt_T3rd', 's1h_w', 's1v_w', 's2h_w', 's2v_w', 's3h_w', 's3v_w', 's4h_w', 's4v_w', 'lxt_vitara', 'lxt', 'lxt_ttc', 'lxe', 'ccmE', 'lomE', 'lomEC', 'gon_v', 'gon_h', 'gon_r', 'gon_x', 'gon_y', 'gon_z', 'gon_roll', 'gon_pitch', 'gon_kappa_eta', 'gon_kappa_kappa', 'gon_kappa_phi', 'gon_phi', 'gon_kappa_samx','gon_kappa_samy', 'gon_kappa_samz', 'robot_x', 'robot_y', 'robot_z', 'robot_rx', 'robot_ry', 'robot_rz', 'robot_az', 'robot_el', 'robot_ra', 'las_comp_wp', 'las_opa_wp'] ]
        self.accessors.tt = [True, 'EPICS', ['XPP:TIMETOOL:FLTPOS','XPP:TIMETOOL:FLTPOS_PS','XPP:TIMETOOL:AMPL','XPP:TIMETOOL:FLTPOSFWHM','XPP:TIMETOOL:REFAMPL','XPP:TIMETOOL:AMPLNXT']]
        self.accessors.slowAdc = [True, psana.Source('DetInfo(XppEndstation.0:Gsc16ai.0)'), psana.Gsc16ai.DataV1]
        self.accessors.AIO = [True, psana.Source('BldInfo(XPP-AIN-01)'), psana.Bld.BldDataAnalogInputV1]
        self.accessors.enc = [True, psana.Source('DetInfo(XppEndstation.0:USDUSB.0)'), psana.UsdUsb.FexDataV1]
        self.evrCodes = [162, 150, 164, 140, 141, 142, 143, 144, 145, 146, 40, 41, 42, 43, 44, 45, 46, 90, 91, 92, 93, 94, 95, 96, 97, 98, 190, 191, 192, 193, 194 ]
        self.beamOffCodes = [ [ 162 ], [ 91 ]]

    def addAccessorsXCS(self):
        self.accessors.ipm2 = [True, psana.Source('BldInfo(XCS-IPM-02)'), psana.Lusi.IpmFexV1]
        self.accessors.ipm3 = [True, psana.Source('BldInfo(XCS-IPM-03)'), psana.Lusi.IpmFexV1]
        #snelson: remove temporarily
        #self.accessors.ipm5 = [True, psana.Source('BldInfo(XCS-IPM-05)'), psana.Lusi.IpmFexV1]
        self.accessors.dio3 = [True, psana.Source('BldInfo(XCS-DIO-03)'), psana.Lusi.IpmFexV1]
        self.accessors.dio5 = [True, psana.Source('BldInfo(XCS-DIO-05)'), psana.Lusi.IpmFexV1]
        self.accessors.diodeMono = [True, psana.Source('BldInfo(XCS-IPM-mono)'), psana.Lusi.IpmFexV1]
        self.accessors.diodeGon = [True, psana.Source('BldInfo(XCS-IPM-gon)'), psana.Lusi.IpmFexV1]
        self.accessors.diodeLadm = [True, psana.Source('BldInfo(XCS-IPM-gon)'), psana.Lusi.IpmFexV1]
        self.accessors.epics = [True, 'EPICS', ['att_transmission', 'att_transmission_3rd_h', 'ccm_E', 'lom_E', 'DIFF_phis', 'DIFF_th', 'DIFF_tth', 'DIFF_xs', 'DIFF_ys', 'DIFF_zs', 'DIFF_x', 'DIFF_y', 'DIFF_chis','DIFF_dety','ladm_theta','LAM_Z','LAM_X1','LAM_X2','LAM_Y1','LAM_Y2','LAM_DET_Y','LAM_DET_X'] ]
        self.accessors.AIO = [True, psana.Source('BldInfo(XCS-AIN-01)'), psana.Bld.BldDataAnalogInputV1]
        self.evrCodes = [162, 150, 164, 140, 141, 142, 143, 144, 145, 146, 40, 41, 42, 43, 44, 45, 46, 83, 84, 85, 86, 87, 88, 89 ]
        self.beamOffCodes = [ [ 162 ], []]

    def addAccessorsMFX(self):
        self.evrCodes = [162, 150, 164, 140, 141, 142, 143, 144, 145, 146, 40, 41, 42, 43, 44, 45, 46 ]
        self.beamOffCodes = [ [ 162 ], []]

    #functions to configure set for specific events
    def setEpicsUser(self, userVarList):
      if isinstance(userVarList, list) and len(userVarList)>0:
        self.accessors.epicsUser[2] = userVarList
      else:
        print 'adding EPICS user variable needs a list of pv names/aliases as input!'

    def setEvrCodes(self, evrCodes):
      self.evrCodes = evrCodes
        
    def setBeamOffCodes(self, evrCodes):
      self.beamOffCodes = evrCodes
        
    def set_ttCalib(self, calibPars):
      if calibPars != None:
        self.ttCalib = calibPars
        
    def set_ttRaw(self, ROIPars=None):
      self.ttSaveRaw=True
      if ROIPars != None:
        self.ttROI = ROIPars

    def set_ipmPos(self):
      self.ipmSavePos=True

    def set_xtcav(self, size=5000, details=False):
      self.accessors.Xtcav[0] = True
      self.xtcav[1] = details
      self.xtcav[2] = size

    def set_AIO(self, AIOPars):
      if len(AIOPars)<2:
        print 'need 3 lists: channel#, user-friendly names & conversion factors (optional)'
        return
      self.aioInfo[0] = AIOPars[0]
      self.aioInfo[1] = AIOPars[1]
      if len(AIOPars)==3:
        self.aioInfo[2] = AIOPars[2]
      else:
        self.aioInfo[2] = [1. for entry in AIOPars[0]]

    def setReqDet(self, det):
      if isinstance(det, list):
        for thisdet in det:
          if isinstance(thisdet, DetObject):
            self.reqDet.append(thisdet._name)
          else:
            self.reqDet.append(thisdet)
      else:
        if isinstance(det, DetObject):
          self.reqDet.append(det._name)
        else:
          self.reqDet.append(det)

    def getConfig(self, env, debug=False):
      if env.experiment()[:3]=='xpp':
        self.addAccessorsXPP()
      elif env.experiment()[:3]=='xcs':
        self.addAccessorsXCS()
      elif env.experiment()[:3]=='mfx':
        self.addAccessorsMFX()

      confkeys = env.configStore().keys()

      for key in self.accessors.__dict__:
        #_ is for internal variables.
        if key[0]=='_':
          continue
        #the timetool 'PV' has changed, deal with old data here
        if key=='tt':
          if (self.accessors.__dict__[key][2])[0] not in [ pv for pv in env.epicsStore().pvNames() ]:
            self.accessors.tt = [True, 'EPICS', ['TTSPEC:FLTPOS','TTSPEC:FLTPOS_PS','TTSPEC:AMPL','TTSPEC:FLTPOSFWHM','TTSPEC:REFAMPL','TTSPEC:AMPLNXT']]
          for cfgKey in confkeys:
            if cfgKey.type() == psana.TimeTool.ConfigV2:
              ttCfg = env.configStore().get(psana.TimeTool.ConfigV2, cfgKey.src())
              self.ttCalib = ttCfg.calib_poly()
              self.ttROI = [[ttCfg.sig_roi_lo().row(),ttCfg.sig_roi_hi().row()],\
                            [ttCfg.sig_roi_lo().column(),ttCfg.sig_roi_hi().column()]]
              self.ttAlias=cfgKey.alias()
              self.ttDet=psana.Detector(cfgKey.alias())
              try:
                self.ttProj=ttCfg.write_projections()
                if self.ttProj:
                  #self.ttProj_cfg = [ttCfg.signal_projection_size(), ttCfg.sideband_projection_size(), ttCfg.reference_projection_size()]
                  self.ttProj_cfg = [ttCfg.sig_roi_hi().column()-ttCfg.sig_roi_lo().column()+1, 
                                     ttCfg.sb_roi_hi().column()-ttCfg.sb_roi_lo().column()+1, 
                                     ttCfg.ref_roi_hi().column()-ttCfg.ref_roi_lo().column()+1,
                                     ttCfg.sig_roi_hi().column()-ttCfg.sig_roi_lo().column()]
              except:
                pass
        if key == 'enc':
          for cfgKey in confkeys:
            if cfgKey.type() == psana.UsdUsb.FexConfigV1:
              encCfg = env.configStore().get(cfgKey.type(), cfgKey.src())
              for ic in range(encCfg.NCHANNELS):
                  self.encInfo.append(encCfg.name(ic))
          #no fex info, check if older data
          if len(self.encInfo)==0:
            for cfgKey in confkeys:
              if cfgKey.type() == psana.UsdUsb.ConfigV1:
                self.encInfo.append('lasDelay')
            self.accessors.enc = [True, psana.Source('DetInfo(XppEndstation.0:USDUSB.0)'), psana.UsdUsb.DataV1]
            
        if key == 'Xtcav':
          if rank==0:
            print 'set env for xtcav'
          self.xtcav[0].SetEnv(env)

        #and now check for detectors.
        if isinstance(self.accessors.__dict__[key][1], psana.Source):
          if (self.accessors.__dict__[key][1].__repr__()) not in [ psana.Source(cfkey.src()).__repr__() for cfkey in confkeys]: 
            #print 'have no config for: ',key
            #for cfkey in confkeys: 
            #  print psana.Source(cfkey.src())
            isL3T = False
            isBld = False
            if (key == 'l3t'):
              #print 'in l3...',key
              l3ID  = 70
              for thisKey in confkeys:
                if thisKey.type():
                  if thisKey.type().TypeId == l3ID:
                    isL3T = True
            if ( (self.accessors.__dict__[key][1].__repr__()).find('EBeam')>=0 or (self.accessors.__dict__[key][1].__repr__()).find('FEEGasDetEnergy')>=0 or (self.accessors.__dict__[key][1].__repr__()).find('PhaseCavity')>=0 or (self.accessors.__dict__[key][1].__repr__()).find('AIN-01')>=0) :
              isBld = True
            if not isBld and not isL3T:
              if debug and rank == 0:
                print 'set accessor key to false for: ',key
              self.accessors.__dict__[key][0] = False
        self.getLittleDataHdf5Pars(env)

    def getUserKeys(self, evtkeys, areaname=None, debug=False):
      usrKeys = []
      usrKeyStrings = []
      for key in evtkeys:
        if debug:
          print 'KEY! ',key
        if key.type()!=None and key.type().__name__.find('ndarray')>=0:
          usrKeys.append(key)
          userName = key.key()
          if (isinstance(areaname,str)):
            if key.alias()!='' and areaname=='alias':
              userName = key.alias() + '_' + key.key()
            else:
              userName = areaname + key.key()
          #ensure that names are unique
          while userName in usrKeyStrings:
            userName+='_1'
          usrKeyStrings.append(userName.strip('\"').strip('\''))            
      if debug:
        print 'found number of user keys: ',len(usrKeys)
      return usrKeys, usrKeyStrings

    def userDataToLittleData(self, userData, descString, ld):
      userData_keys = [ key for key in userData.evt.__dict__.keys() if key.find('write_')>=0 ]
      userData_data = [ userData.evt[key] if isinstance(userData.evt[key], np.ndarray) else np.array(userData.evt[key]) for key in userData_keys ]
      userData_label = [ key.replace('write_','') for key in userData_keys ]
      self.addValueToKey(arrayData(userData_label,userData_data),descString,ld)        

    def extractUserKeys(self, evt, usrKeys):
      return [evt.get(thisKey.type(), psana.Source(thisKey.src()), thisKey.key()) for thisKey in usrKeys]

    def addValueToKey(self, thisDat, key,  dataContainer):
      if thisDat is not None:
        if key not in dataContainer.__dict__:
          newArray = copy.deepcopy(thisDat)
          addToObj(dataContainer, key, newArray)
        else:
          dataContainer.__dict__[key].add(thisDat)

    def extractValues(self, evt, env, dataContainer):
        for key in self.accessors.__dict__:
          if key[0]=='_' or key == 'Xtcav':
            continue
          if not self.accessors.__dict__[key][0]:
            continue

          data = None
          datatype=self.accessors.__dict__[key][2]
          if isinstance(self.accessors.__dict__[key][1], psana.Source):
            if isinstance(datatype, list):
              for version in self.accessors.__dict__[key][2]:
                try:
                  data = evt.get(version, self.accessors.__dict__[key][1])
                  if data is not None:
                    datatype=version
                except:
                  print 'not  version %f for key %f'%(version, key)
            try:
              data = evt.get(datatype, self.accessors.__dict__[key][1])
            except:
              print 'could not get data for key %s from event using evt.get(%s, %s)'%(key, datatype, self.accessors.__dict__[key][1])
          elif self.accessors.__dict__[key][1]=='EvtID':
            data = evt.get(self.accessors.__dict__[key][2])
          #for now have either data or epics store data. Consider scan stuff later.
          elif self.accessors.__dict__[key][1] == 'EPICS':
            data = env.epicsStore()
          elif self.accessors.__dict__[key][1] == 'scan':
            data = env.configStore()
          else:
            print 'what happened to key: ',key
            continue

          thisDat = None 
          if isinstance(data, psana.Lusi.IpmFexV1):
            if self.ipmSavePos:
              thisDat = arrayData(['sum','channels', 'xpos', 'ypos'],[data.sum(), [data.channel()[0], data.channel()[1], data.channel()[2], data.channel()[3]], data.xpos(), data.ypos()])
            else:
              thisDat = arrayData(['sum','channels'],[data.sum(), [data.channel()[0], data.channel()[1], data.channel()[2], data.channel()[3]]])

          elif isinstance(data, psana.Bld.BldDataPhaseCavity):
            thisDat = arrayData(['T1','T2'],[data.fitTime1(), data.fitTime2()])

          elif isinstance(data, psana.EpicsStore):
            varNames = [(var.replace(':','_')).replace(' ','').replace('TTSPEC_','').replace('XPP_TIMETOOL_','') for var in self.accessors.__dict__[key][2]]
            values = [ data.value(pv) if data.value(pv) is not None else np.nan for pv in self.accessors.__dict__[key][2] ]
            #if we are looking at timetool PVs, then add calibrated & raw info if so desired
            if 'tt' in self.accessors.__dict__.keys() and 'FLTPOS' in varNames :
              tt_correction = self.correct_TT(env, evt)
              varNames.append('ttCorr'); values.append(tt_correction)
              if self.ttSaveRaw:
                tt_raw = self.raw_TT(evt)
                if isinstance(tt_raw, dict):
                  for localKey in tt_raw.keys():
                    varNames.append(localKey)
                    values.append(tt_raw[localKey])
                else:
                  varNames.append('ttRaw'); values.append(tt_raw)
            thisDat = arrayData(varNames, values)


          elif isinstance(data, psana.EnvObjectStore):
            thisDat = None
            for cfgVersion in psana.ControlData.Config:
              scan = data.get(cfgVersion, psana.Source('ProcInfo()'))
              if scan is not None:
                varnames = ['var0','var1','var2','none0','none1','none2','varStep']
                varvalues = [np.nan, np.nan, np.nan]
                for i in range(0, np.min((scan.npvControls(),3))):
                  varnames[i+3] = scan.pvControls()[i].name()
                  varvalues[i] = scan.pvControls()[i].value()
                #thisDat = arrayData(varnames, varvalues*2)
                value_istep = env.epicsStore().value('scan_current_step')
                if value_istep is None:
                  value_istep = np.nan
                varvalues = varvalues*2; varvalues.append(value_istep)
                thisDat = arrayData(varnames, varvalues)

          elif isinstance(data, psana.EventId):
            if (self.accessors.__dict__[key][1] == 'EvtID'):
              thisDat = arrayData(['fid','time'], [data.fiducials(), data.time()])

          elif isinstance(data, psana.EvrData.DataV3) or isinstance(data, psana.EvrData.DataV4):
            ts_140=0
            for fevt in data.fifoEvents(): 
              if fevt.eventCode()==140:
                ts_140=fevt.timestampHigh()
            ec=[]
            for fevt in data.fifoEvents(): 
              if fevt.timestampHigh() == ts_140:
                ec.append(fevt.eventCode())
            thisDat = arrayData([str(code) for code in self.evrCodes], [ 1 if code in ec else 0 for code in self.evrCodes ])

          elif isinstance(data, psana.L3T.DataV1) or isinstance(data, psana.L3T.DataV2):
            thisDat = arrayData(['l3t'], [data.accept()])

          elif isinstance(data, psana.Bld.BldDataFEEGasDetEnergyV1) or isinstance(data, psana.Bld.BldDataFEEGasDetEnergy):
            if isinstance(data, psana.Bld.BldDataFEEGasDetEnergyV1):
              thisDat = arrayData(['f11','f12','f21','f22','f63','f64'],[data.f_11_ENRC(), data.f_12_ENRC(), data.f_21_ENRC(), data.f_22_ENRC(), data.f_63_ENRC(), data.f_64_ENRC()])
            else:
              thisDat = arrayData(['f11','f12','f21','f22','f63','f64'],[data.f_11_ENRC(), data.f_12_ENRC(), data.f_21_ENRC(), data.f_22_ENRC(), np.nan, np.nan])

          elif datatype in psana.Bld.BldDataEBeam:
            if psana.Bld.BldDataEBeam.index(datatype)>=6: 
              fieldNames = ['L3Energy','EnergyBC2','PhotonEnergy','Charge', 'LTUAngPos', 'UndAngPos','pulseLength']
              thisDat = arrayData(fieldNames,[data.ebeamL3Energy(), data.ebeamEnergyBC2(), data.ebeamPhotonEnergy(), data.ebeamCharge(), [data.ebeamLTUAngX(),data.ebeamLTUAngY(),data.ebeamLTUPosX(),data.ebeamLTUPosY()], [data.ebeamUndAngX(),data.ebeamUndAngY(),data.ebeamUndPosX(),data.ebeamUndPosY()], data.ebeamPkCurrBC2()/data.ebeamDumpCharge()])
            elif psana.Bld.BldDataEBeam.index(datatype)>=4:
              thisDat = arrayData(fieldNames, [data.ebeamL3Energy(), data.ebeamEnergyBC2(), np.nan, data.ebeamCharge(), [data.ebeamLTUAngX(),data.ebeamLTUAngY(),data.ebeamLTUPosX(),data.ebeamLTUPosY()], [data.ebeamUndAngX(),data.ebeamUndAngY(),data.ebeamUndPosX(),data.ebeamUndPosY()], np.nan])
            else:
              thisDat = arrayData(fieldNames, [data.ebeamL3Energy(), data.ebeamEnergyBC2(), np.nan, data.ebeamCharge(), [data.ebeamLTUAngX(),data.ebeamLTUAngY(),data.ebeamLTUPosX(),data.ebeamLTUPosY()], [np.nan, np.nan, np.nan, np.nan], np.nan])

          elif isinstance(data, psana.Gsc16ai.DataV1):
            values=[]
            chnName=[]
            for ichn,chn in enumerate(data.channelValue()):
              values.append(int(chn))
              chnName.append('ch%i'%ichn)
            thisDat = arrayData(chnName, values[:3])

          elif isinstance(data, psana.UsdUsb.FexDataV1):
            thisDat = arrayData([ chn for chn in self.encInfo if chn!='' ], [ chv for chn,chv in zip(self.encInfo,data.encoder_values()) if chn!='' ])

          elif isinstance(data, psana.UsdUsb.DataV1):
            thisDat = arrayData([ chn for chn in self.encInfo if chn!='' ], [ chv for chn,chv in zip(self.encInfo,data.encoder_count()) if chn!='' ])
            varNames = [ chn for chn in self.encInfo if chn!='' ]
            encOffset=1306521.2 #number for xpp02016
            values = [ (chv-encOffset)*1.3442564e-04 for chn,chv in zip(self.encInfo,data.encoder_count()) if chn!='' ]
            thisDat = arrayData(varNames, values)

          elif isinstance(data, psana.Bld.BldDataAnalogInputV1):
            chnNames=[]
            chnValues=[]
            for ich,chn,chsf in zip(self.aioInfo[0],self.aioInfo[1],self.aioInfo[2]):
              chnNames.append(chn)
              chnValues.append(data.channelVoltages()[ich]*chsf)
            thisDat = arrayData(chnNames, chnValues)

          #EPICS failures are handled in the get function.
          elif data is None:
            if self.accessors.__dict__[key][2]==psana.Lusi.IpmFexV1:
              if self.ipmSavePos:
                thisDat = arrayData(['sum','channels'],[np.nan, [np.nan, np.nan, np.nan, np.nan], np.nan, np.nan])
              else:
                thisDat = arrayData(['sum','channels'],[np.nan, [np.nan, np.nan, np.nan, np.nan]])
            elif self.accessors.__dict__[key][2]== [psana.Bld.BldDataFEEGasDetEnergyV1, psana.Bld.BldDataFEEGasDetEnergy]:
              thisDat = arrayData(['f11','f12','f21','f22','f63','f64'],[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
            elif self.accessors.__dict__[key][2]==psana.Bld.BldDataEBeam:
              thisDat = arrayData(['L3Energy','EnergyBC2','PhotonEnergy','Charge','LTUAngPos','UndAngPos','pulseLength'],[np.nan, np.nan, np.nan, np.nan, [np.nan, np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan, np.nan],np.nan])
            elif self.accessors.__dict__[key][2]==psana.Bld.BldDataPhaseCavity:
              thisDat = arrayData(['T1','T2'],[np.nan, np.nan])
            elif self.accessors.__dict__[key][2]==psana.L3T.DataV1:
              thisDat = arrayData(['l3t'], [np.nan])
            elif self.accessors.__dict__[key][2]==psana.Gsc16ai.DataV1:
              chnName=[]
              chnVal=[]
              #for ichn in np.arange(0,env.configStore().get(self.accessors.__dict__[key][2], self.accessors.__dict__[key][1]).numChannels()):
              for ichn in np.arange(0,env.configStore().get(psana.Gsc16ai.ConfigV1,psana.Source('adc')).numChannels()):
                chnVal.append(np.nan)
                chnName.append('chn%i'%ichn)
              thisDat = arrayData(chnName, chnVal)
            elif self.accessors.__dict__[key][2]== [psana.EvrData.DataV3, psana.EvrData.DataV4]:
              thisDat = arrayData([str(code) for code in self.evrCodes], [ np.nan for code in self.evrCodes ])
            elif self.accessors.__dict__[key][2]==psana.Bld.BldDataAnalogInputV1:
              chnNames=[]
              chnValues=[]
              for ich,chn,chsf in zip(self.aioInfo[0],self.aioInfo[1],self.aioInfo[2]):
                chnNames.append(chn)
                chnValues.append(np.nan)
              thisDat = arrayData(chnNames, chnValues)
            elif self.accessors.__dict__[key][2]==psana.UsdUsb.FexDataV1:
              thisDat = arrayData([ chn for chn in self.encInfo if chn!='' ], [ np.nan for chn in self.encInfo if chn!='' ])
          elif isinstance(data, object):
            thisDat = arrayData(data.__dict__.keys(), [data.__dict__[loc_key] for loc_key in data.__dict__.keys()])
        
          self.addValueToKey(thisDat, key,  dataContainer)
        
        xfel_status, laser_status = pumpprobe_status(evt, self.beamOffCodes[0], self.beamOffCodes[1])
        self.addValueToKey(arrayData(['xray','laser'],[xfel_status, laser_status]),'lightStatus',dataContainer)

        if self.accessors['Xtcav'][0]: 
          print 'try to get Xtcav'
          xtcav_success=False
          if self.xtcav[0].SetCurrentEvent(evt):
            timeOrg,power,ok=self.xtcav[0].XRayPower()
            #if self.xtcav[2]<0:
            #  comm.Barrier()
            #  self.xtcav[2]=arSize
            if ok:
              arSize=timeOrg[0].shape[0]
              agreement,ok=self.xtcav[0].ReconstructionAgreement()
              xtcav_success=True
              #better: add single val arrays if empty, then add actual size to
              #self.xtcav[2] and use addToObj to add the full correcly sized array to ld
              #def addToObj(obj,name,value,overWrite=True,ixpsaved=False, setParent=True):
              #usage example: addToObj(ldGather, key.replace('/','.'), myrecv)
              #padd array to size
              if arSize>=1 and arSize<=self.xtcav[2]:
                time = np.append(timeOrg[0],np.array([np.nan] * (self.xtcav[2]-arSize)))
                power = np.append(power[0],np.array([np.nan] * (self.xtcav[2]-arSize)))
              else:
                print 'Xtcav array is too small in run, please check littleData configuration',env.run()
                time = timeOrg[:self.xtcav[2]]
                power = power[:self.xtcav[2]]
              #if time.shape[0]>=10:
              #  print time[:10]
              #else:
              #  print time
              #print 'short version:',time.shape,power.shape,agreement
              self.addValueToKey(arrayData(['agreement','arSize','time','power'],[agreement, arSize, time, power]),'Xtcav',dataContainer)
          if not xtcav_success and self.xtcav[2]>0:
              arrayNan = ([np.nan] * self.xtcav[2])
              self.addValueToKey(arrayData(['agreement','arSize','time','power'],[-1, 0, arrayNan, arrayNan]),'Xtcav',dataContainer)
                    
    def correct_TT(self,env, evt):
      #ttOrg = env.epicsStore().value('XPP:TIMETOOL:FLTPOS')
      try:
        ttOrg = env.epicsStore().value(self.accessors.__dict__['tt'][2][0])
      except:
        return 0.
      if ttOrg is None or self.ttCalib[0] == np.nan:
        return np.nan
      if ttOrg != 0.:
        ttCorr = self.ttCalib[0]+ ttOrg*self.ttCalib[1]
        if len(self.ttCalib)>2:
          ttCorr+=ttOrg*ttOrg*self.ttCalib[2]
        return ttCorr
      return 0.

    def raw_TT(self,evt):
      if self.ttProj:
        retDict={}
        retKeys = ['tt_signal','tt_sideband','tt_reference','tt_sig_proj']
        try:
          ttDet=evt.get(psana.TimeTool.DataV2, psana.Source(self.ttAlias))
          ttData = [ttDet.projected_signal().astype(dtype='uint32').astype(float), ttDet.projected_sideband().astype(dtype='uint32').astype(float), ttDet.projected_reference().astype(dtype='uint32').astype(float)]
          ttImg = self.ttDet.raw(evt)
          if self.ttROI[0][0] is not np.nan:
            ttData.append(ttImg[self.ttROI[0][0]:self.ttROI[0][1],self.ttROI[1][0]:self.ttROI[1][1]].mean(axis=0))          

          for ikey,key in enumerate(retKeys):
            if self.ttProj_cfg[ikey]>0:
              if ttData[ikey].shape[0] == self.ttProj_cfg[ikey]:
                retDict[key] = ttData[ikey]
                print key, ttData[ikey].shape, ttData[ikey][:10]
              else:
                nanAr = np.empty(self.ttProj_cfg[ikey])
                nanAr[:]=np.nan
                retDict[key] = nanAr

          print 'sp '  ,ttData[0][:5]
          print 'simg ',ttData[3][:5]
        except:
          for ikey,key in enumerate(retKeys):
            if self.ttProj_cfg[ikey]>0:
              nanAr = np.empty(self.ttProj_cfg[ikey])
              nanAr[:]=np.nan
              retDict[key] = nanAr
        return retDict
      else:
        try:
          ttImg = self.ttDet.raw(evt)
          if self.ttROI[0][0] is not np.nan:
            return ttImg[self.ttROI[0][0]:self.ttROI[0][1],self.ttROI[1][0]:self.ttROI[1][1]].sum(axis=0)
          return ttImg.sum(axis=0)
        except:
          nanAr = np.empty([abs(self.ttROI[1][0]-self.ttROI[1][1])])
          nanAr[:]=np.nan
          return nanAr

    def getLittleDataHdf5Pars(self, env, dirname=None):
      #set the directory name for writing the possibly MPI'ed files:
      expname = env.experiment()
      if (env.jobName()).find('shmem')>=0:
        dirname = '/reg/neh/operator/%sopr/experiments/%s/littleData/'%(expname[:3],expname)
      elif dirname!=None and dirname!='None': #if we have set this, assume I also want the merge file here.
        outDir = dirname
      else:
        dirname = '/reg/d/psdm/%s/%s/hdf5/smalldata/'%(expname[:3],expname)
        if not os.path.isdir(dirname):
          dirname = '/reg/d/psdm/%s/%s/ftc/'%(expname[:3],expname)
      #now set self.dirname so that we'll remember through the functions.
      self.dirname = dirname
      return dirname
