#!/usr/bin/python
# This module provides support 
# for the SXR Large Area Detector Mover (LADM or LAM)
# for the SXR beamline (@LCLS)
# 
# Author:         Daniel Flath (SLAC)
# Created:        Aug 19, 2011
# Modifications:
#   Aug 19, 2011 DF
#       first version

import numpy as n
from numpy import rad2deg,arcsin,sqrt,tan
import sys
from utilities import estr
import pypsepics
from pypslog import logprint
import math
from device import Device

class Goniometer(Device):
  """
  Class to control the SXR 4.5 circle Diffractometer

  Motors are:

  x: system x
  y: system y
  th: sample theta
  th2: detector 2theta
  chi: sample chi (rotation about z, or beam trajectory)
  phi: sample phi (rotation about x)
  sx: sample x
  sy: sample y
  sz: sample z
  dy: detector y
  gam: detector gama (rotation about x while sample/detector are colinear on z)


  Additionally, 2 virtual motors are defined:

  reflectdet: Moves dy/gam in coordination to achieve a 2-phi rotation of the detector about the sample.
              See methods 'diffDetPhi*'
  diffDSPhi:  Moves phi/reflectdet to achieve sample/detector phi reflection geometry
              See methods 'diffDSPhi*'
  """

  def __init__(self,x,y,th,th2,chi,phi,sx,sy,sz,dy,gam,objName="diff",pvBase=None,presetsfile="/reg/neh/operator/sxropr/sxrpython_data/diffpresets.py"):
     Device.__init__(self,objName,pvBase,presetsfile)
     self.x = x
     self.y = y
     self.th = th
     self.th2 = th2
     self.chi = chi
     self.phi = phi
     self.sx = sx
     self.sy = sy
     self.sz = sz
     self.dy = dy
     self.gam = gam
     self.objName = objName
     self.detCenOffset = None
     self.pvBase = pvBase
     self.reflectdet = None # externally defined, in sxrbeamline.py
     self.reflect = None    # externally defined, in sxrbeamline.py
     
     self.motors = {
        "x": x,
        "y": y,
        "th": th,
        "th2": th2,
        "chi": chi,
        "phi": phi,
        "sx": sx,
        "sy": sy,
        "sz": sz,
        "dy": dy,
        "gam": gam
        }

  
  # TODO:  Should have an interactive flag and throw exception otherwise
  def set_det_cen_offset(self, off=None):
    """ Required to initialize Phi Reflection virtual motors.  Sets offset of detector from Sample """
    if off is not None:
      self.detCenOffset = off
    else:
      print "Enter detector offset (620mm + tape scale reading on 2-Theta arm of diffractometer)\n>",
      self.detCenOffset=float(raw_input())
      pass
    pass
      
  def checkDetPhiConfig(self):
    """ Check if user performed initialization """
    if self.detCenOffset is None:
      print "Detector Center not defined.  (You can use 'set_det_cen_offset()' to set it.)"
      self.set_det_cen_offset()
      pass
    pass

  def assertLimitsDetPhi(self, phi):
    """ Check that 'virtual motor' position is reachable by all physical stages """
    ll = self.getLowLimDetPhi()
    if phi < ll:
      print "%f is less than low limit of %f" % (phi,ll)
      return False
    hl = self.getHiLimDetPhi()
    if phi > hl:
      print "%f is more than hi limit of %f" % (phi,hl)
      return False
    return True
    

  def moveDetPhi(self, phi):
    """ Move Detector to phi reflection (2*phi).  This requires translating det-y and rotating det-gamma """
    self.checkDetPhiConfig()
    if not self.assertLimitsDetPhi(phi):
      return
    tphi = 2. * phi
    y_off = -1. * self.detCenOffset * math.tan(tphi*math.pi/180.)
    print "moving gam,dy to %f,%f" % (tphi,y_off)
    self.gam.move_silent(tphi)
    self.dy.move_silent(y_off)
    if self.pvBase is not None:
      pypsepics.put(self.pvBase + ":GON:REFD",phi)
    pass

  def wmDetPhi(self):
    """ Retrieve position (angle) of det-phi virtual motor calculated from det-y and det-gamma physical stages """ 
    self.checkDetPhiConfig()
    tphi = self.gam.wm()
    if 0.01 > math.fabs(-1. * self.detCenOffset * math.tan(tphi*math.pi/180.) - self.dy.wm()):
      return tphi/2.
    else:
      return None
    pass
  
  def waitDetPhi(self):
    """ Wait for movement completion of physical motors which comprise virtual motor det-phi """
    self.checkDetPhiConfig()
    self.gam.wait()
    self.dy.wait()
    pass

  def getLowLimDetPhi(self):
    """ Minimum achievable angle in virtual motor coordinates, based on soft-limits of related physical stages """
    return max(self.gam.get_lowlim()/2.,
               -0.5*(180./math.pi)*math.atan2(self.dy.get_hilim(),self.detCenOffset)
               )
    pass

  def getHiLimDetPhi(self):
    """ Maximum achievable angle in virtual motor coordinates, based on soft-limits of related physical stages """
    return min(self.gam.get_hilim()/2.,
               -0.5*(180./math.pi)*math.atan2(self.dy.get_lowlim(),self.detCenOffset)
               )
    pass
  
  def assertLimitsDSPhi(self, phi):
    """ Check that 'virtual motor' position is reachable by all physical stages """
    ll = self.getLowLimDSPhi()
    if phi < ll:
      print "%f is less than low limit of %f" % (phi,ll)
      return False
    hl = self.getHiLimDSPhi()
    if phi > hl:
      print "%f is more than hi limit of %f" % (phi,hl)
      return False
    return True
    

  def moveDSPhi(self, phi):
    """ Move physical motors in sample/detector stages to get Phi reflection geometry """
    if not self.assertLimitsDSPhi(phi):
      return
    self.reflectdet.move_silent(phi)
    self.phi.move_silent(phi)
    if self.pvBase is not None:
      pypsepics.put(self.pvBase + ":GON:REF",phi)
    pass

  def wmDSPhi(self):
    """ Calculate sample/detector phi reflection based on physical stage positions, within tolerance """
    dp = self.reflectdet.wm()
    p = self.phi.wm()
    if 0.01 > math.fabs(dp - p):
      return p
    else:
      return None
    pass
  
  def waitDSPhi(self):
    """ Wait for sample/detector phi coordinated physical motions to finish """
    self.reflectdet.wait()
    self.phi.wait()
    pass

  def getLowLimDSPhi(self):
    """ Minimum achievable sample/detector phi reflection based on phyisical motor limits """
    return max(self.getLowLimDetPhi(),
               self.phi.get_lowlim()
               )
    pass

  def getHiLimDSPhi(self):
    """ Maximum achievable sample/detector phi reflection based on phyisical motor limits """
    return min(self.getHiLimDetPhi(),
               self.phi.get_hilim()
               )
    pass
