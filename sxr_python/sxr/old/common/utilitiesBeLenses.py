from periodictable import xsf
from periodictable import formula as ptable_formula
import numpy as np
from numpy import real
import datetime
import os
import shutil
import pprint

def setLensSetsToFile(sets_listOfTuples,filename='/reg/neh/operator/xppopr/xpppython_files/Be_lens_sets/current_set'):
  try:
    shutil.copy2(filename,os.path.split(filename)[0]+'sets_Be_'+datetime.datetime.now().strftime('%Y-%m-%d'))
  except:
    pass	 
  f=open(filename,'w')
  f.write(pprint.pformat(sets_listOfTuples))
  f.close()
  
def getLensSet(setnumber_topToBot,filename='/reg/neh/operator/xppopr/xpppython_files/Be_lens_sets/current_set'):
  f=open(filename)
  sets = eval(f.read())
  f.close()
  return sets[setnumber_topToBot-1]

def getAttLen(E,material="Be",density=None):
  """ get the attenuation length (in meter) of material (default Si), if no
      parameter is given for the predefined energy;
      then T=exp(-thickness/att_len); E in keV"""
  att_len = float(xsf.attenuation_length(material,density=density,energy=E))
  return att_len

def getDelta(E,material="Be",density=None):
  """ returns 1-real(index_of-refraction) for a given material at a given energy"""
  delta = 1-real(xsf.index_of_refraction(material,density=density,energy=E))
  return delta

def calcFocalLengthForSingleLens(E,radius,material="Be",density=None):
  """ returns the focal length for a single lens f=r/2/delta """
  delta = getDelta(E,material,density)
  f = radius/2./delta
  return f

def calcFocalLength(E,lens_set,material="Be",density=None):
  """ lens_set = (n1,radius1,n2,radius2,...) """
  num = []
  rad = []
  ftot_inverse = 0
  if type(lens_set) is int:
    lens_set = getLensSet(lens_set)
  for i in range(len(lens_set)/2):
    num = lens_set[2*i]
    rad = lens_set[2*i+1]
    ftot_inverse += num/calcFocalLengthForSingleLens(E,rad,material,density)
  return 1./ftot_inverse

def calcBeamFWHM(E,lens_set,distance = 4,material="Be",density=None,fwhm_unfocused=500e-6):
  """ usage calcBeamFWHM(8, (2,200e-6,4,500-6) )
      calculate beam parameters at a given distance for a given 
      lens set and energy.
      Optionally some other parameters can be set
  """
  f = calcFocalLength(E,lens_set,material,density)
  lam = 12.398/E*1e-9
  # the w parameter used in the usual formula is 2*sigma
  w_unfocused    = fwhm_unfocused*2/2.35
  # assuming gaussian beam divergence = w_unfocused/f we can obtain
  waist = lam/np.pi*f/w_unfocused
  rayleigh_range = np.pi*waist**2/lam
  print "waist          : %.3e" % waist
  print "waist FWHM     : %.3e" % (waist*2.35/2.)
  print "rayleigh_range : %.3e" % rayleigh_range
  print "focal length   : %.3e" % f
  size = waist*np.sqrt(1.+(distance-f)**2./rayleigh_range**2)
  print "size           : %.3e" % size
  print "size FWHM      : %.3e" % (size*2.35/2.)
  return size*2.35/2

def findEnergy(lens_set,distance=4.,material="Be",density=None):
  """ usage findEnergy( (2,200e-6,4,500e-6) ,distance =4 )
      finds the neergy that would focus at a given distance (default = 4m)
  """
  Emin = 1.
  Emax = 24.
  E = (Emax+Emin)/2.
  absdiff =100
  while ( absdiff > 0.0001 ):
    fmin = calcFocalLength(Emin,lens_set,material,density)
    fmax = calcFocalLength(Emax,lens_set,material,density)
    E = (Emax+Emin)/2.
    f = calcFocalLength(E,lens_set,material,density)
    if ( (distance<fmax) and (distance>f) ):
      Emin = E
    elif ( (distance>fmin) and (distance<f) ):
      Emax = E
    else:
      print "somehow failed ..."
      break
    absdiff = abs(distance-f)
  print "Energy that would focus at a distance of %.3f is %.3f" % (distance,E)
  s = calcBeamFWHM(E,lens_set,distance,material,density)
  return E
