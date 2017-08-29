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

class Aerotech:
  """ Class to control the SXR LADM """

  def __init__(self,x,y):
    self.x   = x
    self.y   = y

  def status(self):
    str = "** Detector Translation Status **\n"
    str += "\t(x, y) [user]: %+.4f, %+.4f\n" % (self.x.wm(),self.y.wm())
    str += "\t(x, y) [dial]: %+.4f, %+.4f\n" % (self.x.wm_dial(),self.y.wm_dial())
    return str
  
  def __repr__(self):
    return self.status()
