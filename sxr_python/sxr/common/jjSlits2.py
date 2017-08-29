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
import virtualmotor

class JJSlits:
  """ Class to control the SXR Beamstop """

  def __init__(self,svg,svo,shg,sho,name):
    self.__svg  = svg
    self.__svo  = svo
    self.__shg  = shg
    self.__sho  = sho
    self.name = name

  def status(self):
    str = "** \"%s\" JJ-Slit Status **\n" % (self.name)
    str += "\t(svg, svo, shg, sho) [user]: %+.4f, %+.4f, %+.4f, %+.4f\n" % (self.__svg.wm(),self.__svo.wm(),self.__shg.wm(),self.__sho.wm())
    str += "\t(svg, svo, shg, sho) [dial]: %+.4f, %+.4f, %+.4f, %+.4f\n" % (self.__svg.wm_dial(),self.__svo.wm_dial(),self.__shg.wm_dial(),self.__sho.wm_dial())
    return str
  
  def __repr__(self):
    return self.status()

  class JJSlitsGapVM(virtualmotor.VirtualMotor):
    def __init__(self,name,gMotor,oMotor):
      VirtualMotor(None,name,self.move,gMotor.wm,self.wait,self.set)
      self.gMotor = gMotor
      self.oMotor = oMotor

    def move(self,aPos):
      gm = self.gMotor
      om = self.oMotor
      gp0 = gm.wm()
      gm.move(aPos)
      gm.wait()
      gp1 = gm.wm()
      op0 = om.wm()
      odelta = gp1-gp0
      om.mvr(odelta)
      om.wait()
      op1 = om.wm()
      
      
      
