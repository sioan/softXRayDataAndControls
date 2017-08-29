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

class Beamstop:
  """ Class to control the SXR Beamstop """

  def __init__(self,radial,transverse,radius):
    self.r          = radial
    self.t          = transverse
    self.radius     = radius

  def status(self):
    str = "** \"%smm\" Beam-stop Status **\n" % (self.radius)
    str += "\t(radial, transverse) [user]: %+.4f, %+.4f\n" % (self.r.wm(),self.t.wm())
    str += "\t(radial, transverse) [dial]: %+.4f, %+.4f\n" % (self.r.wm_dial(),self.t.wm_dial())
    return str
  
  def __repr__(self):
    return self.status()
