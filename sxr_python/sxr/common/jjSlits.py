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

class JJSlits:
  """ Class to control the SXR Beamstop """

  def __init__(self,svg,svo,shg,sho,name):
    self.svg  = svg
    self.svo  = svo
    self.shg  = shg
    self.sho  = sho
    self.name = name

  def status(self):
    str = "** \"%s\" JJ-Slit Status **\n" % (self.name)
    str += "\t(svg, svo, shg, sho) [user]: %+.4f, %+.4f, %+.4f, %+.4f\n" % (self.svg.wm(),self.svo.wm(),self.shg.wm(),self.sho.wm())
    str += "\t(svg, svo, shg, sho) [dial]: %+.4f, %+.4f, %+.4f, %+.4f\n" % (self.svg.wm_dial(),self.svo.wm_dial(),self.shg.wm_dial(),self.sho.wm_dial())
    return str
  
  def __repr__(self):
    return self.status()
