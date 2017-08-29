
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

class LocalDetector:
  """ Class to control the SXR LADM """

  def __init__(self,svg,svo,shg,sho,yag,zoom,location=""):
    self.svg      = svg
    self.svo      = svo
    self.shg      = shg
    self.sho      = sho
    self.yag      = yag
    self.zoom     = zoom
    self.location = location

  def status(self):
    str = "** \"%s\" Local Detector Status **\n" % (self.location)
    str += "\tSlit(vg,vo,hg,ho) [user]: %+.4f, %+.4f, %+.4f, %+.4f\n" % (self.svg.wm(),self.svo.wm(),self.shg.wm(),self.sho.wm())
    str += "\tSlit(vg,vo,hg,ho) [dial]: %+.4f, %+.4f, %+.4f, %+.4f\n" % (self.svg.wm_dial(),self.svo.wm_dial(),self.shg.wm_dial(),self.sho.wm_dial())
    str += "\tYag(trans,zoom) [user]: %+.4f, %+.4f\n" % (self.yag.wm(), self.zoom.wm())
    str += "\tYag(trans,zoom) [dial]: %+.4f, %+.4f\n" % (self.yag.wm_dial(), self.zoom.wm_dial())
    return str
  
  def __repr__(self):
    return self.status()
