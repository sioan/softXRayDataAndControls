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
import beamstop

class Beamstops:
  """ Class to control the SXR Beamstops """

  def __init__(self):
    self.beamstops=[]

  def addBeamstop(self,beamstop):
    self.beamstops.append(beamstop)

  def status(self):
    str = "** LADM Beam-stops **\n"
    for bs in self.beamstops:
      str += bs.status()
    return str
  
  def __repr__(self):
    return self.status()
