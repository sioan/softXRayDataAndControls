import pylab as pl
import numpy as np
import os,sys
import PyCSPadImage.CalibPars as calp
import PyCSPadImage.CSPADPixCoords  as pixc #<-- current issue as using old geometry....
import numpy as np
from PSCalib.GeometryAccess import GeometryAccess

def get_cspad_pixel_coordinate_index_arrays_new(expname=None):
	parentdir = '/reg/d/psdm/xpp/'
	if expname==None or expname=='newest':
		expname='xpptut13'
	fname_geometry = parentdir+expname+'/calib/CsPad::CalibV1/XppGon.0:Cspad.0/geometry/0-end.data'
	geometry = GeometryAccess(fname_geometry, 0377)
	iX, iY = geometry.get_pixel_coord_indexes(do_tilt=True)
	iX -= iX.min()
	iY -= iY.min()
	return iX.flatten(),iY.flatten()	

def get_cspad_pixel_coordinates(expname=None):
	parentdir = '/reg/d/psdm/xpp/'
	if expname==None or expname=='newest':
		expname='xpptut13'
	fname_geometry = parentdir+expname+'/calib/CsPad::CalibV1/XppGon.0:Cspad.0/geometry/0-end.data'
	geometry = GeometryAccess(fname_geometry, 0377)
	X, Y, Z = geometry.get_pixel_coords()
	return X.squeeze().flatten(),Y.squeeze().flatten(),Z.squeeze().flatten()

def get_cspad_pixel_coordinate_index_arrays(path_calib='./', runnum=1) :
        """Uses cspad geometry calibration parameters and
	returns flatten cspad iX and iY arrays (size=32*185*388) of pixel coordinates [in pix]
	"""
	calibstore = calp.CalibPars( path=path_calib, run=runnum )
	#pixcoords.print_cspad_geometry_pars()
	iX,iY = pixc.CSPADPixCoords(calibstore).get_cspad_pix_coordinate_arrays_pix()
	iX -= iX.min()
	iY -= iY.min()
	return iX.flatten(), iY.flatten()

def getCsPadPixCoordinates(path_calib='xpptut13', 
                           rotation=0, 
                           mirror=False):
  #this needs to be different and point to the psdm dirs.
  parentdir = '/reg/d/psdm/xpp/'
  if path_calib==None or path_calib=='newest':
    expstr='xpptut13'
    alignmentdir = parentdir+expstr+'/calib/CsPad::CalibV1/XppGon.0:Cspad.0'
    allfiles = os.listdir(alignmentdir)
    files = []
    for tf in allfiles:
      if 'calib-' in tf:
        files.append(tf)
    files.sort()

    if path_calib==None:
      print "Please select calibration file:"
      for i,tf in enumerate(files):
        print "%d  :  %s" %(i+1,tf)
      path_calib = files[int(raw_input())-1]
    else:
      path_calib = files[-1]

  else:
    parentdir = '/reg/d/psdm/xpp/'+path_calib
    path_calib = parentdir+'/calib/CsPad::CalibV1/XppGon.0:Cspad.0'


  run=0
  calib = calp.CalibPars(path_calib,run)
  coord = pixc.CSPADPixCoords(calib)
  X,Y = coord.get_cspad_pix_coordinate_arrays_um(config=None)
  x = np.concatenate(X,0)
  y = np.concatenate(Y,0)

  return x,y

class loadingtest(object):
  def loadcoo(self):
    return getCsPadPixCoordinates(path_calib='')

class CspadPattern(object):
  def __init__(self,Nx=1000,Ny=1000,path_calib='newest'):
    self._path_calib = path_calib
    self._xpx = [] 
    self._ypx = []
    self.load_coordinates()
    xmn = np.min(self.xpx)
    xmx = np.max(self.xpx)
    self.xVec = np.linspace(xmn,xmx,Nx)
    self._binxVec = np.linspace(xmn-(xmx-xmn)/Nx/2,
                                xmx+(xmx-xmn)/Nx/2,Nx+1)
    ymn = np.min(self.ypx)
    ymx = np.max(self.ypx)
    self.yVec = np.linspace(ymn,ymx,Ny)
    self._binyVec = np.linspace(ymn-(ymx-ymn)/Ny/2,
                                ymx+(ymx-ymn)/Ny/2,Ny+1)
    self.shp = np.shape(self.xpx)
    self.shpPattern = (Ny,Nx)
    xind = np.digitize(self.xpx.ravel(),self._binxVec)
    yind = np.digitize(self.ypx.ravel(),self._binyVec)
    self.binning = np.ravel_multi_index((yind-1,xind-1),(Ny,Nx))
    self.numperbin = np.bincount(self.binning)
    self.pixssz = np.array([110.,110])*1e-6
    #self.bin = wrapFunc(self._bin,isPerEvt=True)


  def _bin(self,I):
    Ilong = np.bincount(self.binning, weights=np.asfarray(I.ravel()))
    Ilong = Ilong/self.numperbin
    P = np.zeros(np.prod(self.shpPattern))
    P[:len(Ilong)] = Ilong
    P = np.reshape(P,self.shpPattern)
    return P

  def ind2ori(self,ind):
    if np.size(ind) == np.size(self.shpPattern):
      pass
    indbool = ind
    indbool = indbool.ravel()
    indout = indbool[np.ix_(self.binning)]
    indout = np.reshape(indout,self.shp)
    return indout

  def polygonmask(self,polygon):
    return polygonmask(polygon,self.xpx,self.ypx)

  def load_coordinates(self,rotation=0,mirror=0):
    self._xpx,self._ypx = getCsPadPixCoordinates(rotation=rotation,mirror=mirror,path_calib = self._path_calib)

  def load_coordinates_test(self,rotation=0,mirror=0):
      return getCsPadPixCoordinatesTT(rotation=rotation,mirror=mirror,path_calib = self._path_calib)

  def _get_xpx(self):
    if len(self._xpx)==0:
      #self._xpx = np.load(os.path.dirname(self._path) + '/' + 'cspad_x.npy')
      self._xpx,self._ypx = getCsPadPixCoordinates(rotation=0,path_calib = self._path_calib)
    return self._xpx
  xpx = property(_get_xpx)

  def _get_ypx(self):
    if len(self._ypx)==0:
      #self._ypx = np.load(os.path.dirname(self._path) + '/' + 'cspad_y.npy')
      self._xpx,self._ypx = getCsPadPixCoordinates(rotation=0,path_calib = self._path_calib)
    return self._ypx
  ypx = property(_get_ypx)

  def saveMaskDAQ(self,filename,mask=None):
    if mask==None:
      mask = self.mask
    f = file(filename,'w')
    for seg in mask:
      for line in seg:
        for el in line:
          f.write(' '+str(int(el)))
        f.write('\n')

def noiseMap(Istack):
  return np.std(np.asfarray(Istack)/sum(Istack),axis=0)



def corrLongPix(I,fillvalues=True,BGcorrect=None):
  if BGcorrect:
    if BGcorrect<0:
      stripe = I[-BGcorrect:,:]
    elif BGcorrect>0:
      stripe = I[:BGcorrect,:]
    stripe = np.ma.masked_array(stripe,np.isnan(stripe))
    I = I-np.mean(stripe,axis=0)
  Io = np.ones((185,388+3))*np.nan
  Io[:,:388/2-1] =  I[:,:388/2-1]
  Io[:,-388/2+1:] =  I[:,388/2+1:]
  if fillvalues:
    mpp1 = I[:,388/2-1].copy()/2.5
    mpp2 = I[:,388/2].copy()/2.5
    for n in range(2):
      Io[:,388/2-1+n]  =  mpp1.copy()
      Io[:,-388/2-n] =  mpp2.copy()
    Io[:,388/2+1] = np.mean(np.vstack([mpp1,mpp2]),axis=0).transpose()
  return Io



def getCommonModeFromHist(im,searchoffset=200,COMrad=3):                        
  bins = np.arange(-100,100) 
  hist,dum = np.histogram(im.ravel(),bins)
  aboveoffset = (hist>searchoffset)
  iao = list(aboveoffset).index(True)
  imx = iao + list(np.diff(hist[aboveoffset])<0).index(True)
  CM = (1.*np.sum(hist[imx-COMrad:imx+COMrad+1]*bins[imx-COMrad:imx+COMrad+1])/ np.sum(hist[imx-COMrad:imx+COMrad+1])) 
  return CM

def create_pixel_histogram(cspad_det,dark=None,Nmax=None):
  cc = 0
  npatt = len(cspad_dat.time[cc])
  if Nmax==None or Nmax>npatt:
    Nmax = npatt
  chunks = cspad_dat.chunks(Nmax=Nmax)

  histbins = []
  histograms = []

  for ch in chunks[cc]:
    data = ch.data
    if not dark==None:
      data = data-dark
    if histbins==[]:
      datshp = np.shape(data[0])
      Nel = np.prod(datshp)
      histbins = np.empty(datshp,dtype=np.object_)
      data = data.reshape(datshp[0],-1)
      ind = 0
      for n in range(Nel):
        ind = np.ravel_index(n,datshp)
        histbins[ind] = histEdges(data[ind])
    
    for n in range(Nel):
      ind = np.ravel_index(n,datshp)
      if histograms ==[]:
        histograms = np.empty(datshp,dtype=np.object_)
        histpgrams[ind] = np.histogram(data[ind],histbins[ind])
      else:
        histograms[ind] += np.histogram(data[ind],histbins[ind])

  return histograms,histbins


def maskEdge(shape=(185,388),offset=1,maskmid=True):
  msk = np.zeros(shape,dtype='bool')
  msk[:offset,:] = True
  msk[:,:offset] = True
  msk[-offset:,:] = True
  msk[:,-offset:] = True
  if maskmid:
    msk[:,np.floor((max(shape)-1)/2.)] = True
    msk[:,np.ceil((max(shape)-1)/2.)] = True
  return msk
    
def maskEdges(i,offset=1,maskmid=True):
  shp = np.shape(i)
  shpTile = shp[-2:]
  shpdet  = shp[:-2]
  mskTile = maskEdge(shape=shpTile,offset=offset,maskmid=maskmid)
  tmsk = mskTile
  iter_shpdet = list(shpdet)
  iter_shpdet.reverse()
  for N in iter_shpdet:
    tmsk = [tmsk for n in xrange(N)]

  return np.asarray(tmsk)
  

  








    








