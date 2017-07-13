import os
import copy
import numpy as np
import h5py
import fnmatch

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
mpiSize = comm.Get_size()

import psana
from collections import Counter
#import time

class dropObject(object):
  def __init__(self,name='noname',parent=None):
    self._name = name
    self._parent = parent

  def add(self,name,data):
    if (name not in self.__dict__):
      self._add(name,data)
    else:
      self.__dict__[name].append(data)
  def _add(self,name,data):
    self.__dict__[name]=[data]
  def addField(self,name,data):
    if (name not in self.__dict__):
      if isinstance(data, list) or  isinstance(data, np.ndarray):
        self.__dict__[name]=data
      else:
        self.__dict__[name]=[data]
    else:
      print 'field ',name,' already in dropObject: ',self._name
  def __repr__(self):
    return "dropObject with fields: "+str(self.__dict__.keys())
  def __getitem__(self,x):
    return self.__dict__[x]
  def __setitem__(self,name,var,setParent=True):
    self._add(name,var)
    if setParent:
      try:
        self[name]._parent = self
      except:
	pass
  def _get_keys(self):
    return [tk for tk in self.__dict__.keys() if not tk[0]=='_']

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


