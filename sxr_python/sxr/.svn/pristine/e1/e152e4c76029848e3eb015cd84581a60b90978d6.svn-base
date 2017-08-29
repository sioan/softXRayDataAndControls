#!/usr/bin/python
# This module provides support 
# for the SXR Large Area Detector Mover (LADM or LAM)
# for the SXR beamline (@LCLS)
# 
# Author:         Daniel Flath (SLAC)
# Created:        Nov 12, 2011
# Modifications:
#   Nov 12, 2011 DF
#       first version

import numpy as n
from numpy import rad2deg,arcsin,sqrt,tan
import sys
from utilities import estr
import pypsepics
from pypslog import logprint

class BeLens:
  """ Class to control the SXR LADM """

  def __init__(self,x,y,z,name="Be Lens"):
    self.x   = x
    self.y   = y
    self.z   = z
    self.name = name
    self.motors = {
      "x": x,
      "y": y,
      "z": z
      }

  def status(self):
    str = "** %s Status **\n\t%10s\t%10s\t%10s\n" % (self.name,"Motor","User","Dial")
    keys = self.motors.keys()
    keys.sort()
    for key in keys:
       m = self.motors[key]
       str += "\t%10s\t%+10.4f\t%+10.4f\n" % (key,m.wm(),m.wm_dial())
    return str
  
  def __repr__(self):
    return self.status()
