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

class G2(Device):
  """
  Class to control the L637-David Grating-2 enclosure elements

  Motors are:

  x:    chamber x
  y:    chamber y
  z:    chamber z
  attx: attenuator x
  atty: attenuator y
  apx:  aperture x
  """

  def __init__(self,x,y,z,attx,atty,apx,objName="g2",pvBase=None,presetsfile=None):
     Device.__init__(self,objName,pvBase,presetsfile)
     self.x = x
     self.y = y
     self.z = z
     self.attx = attx
     self.atty = atty
     self.apx = apx
     #self.objName=objName
     #self.pvBase=pvBase
     
     self.motors = {
        "x": x,
        "y": y,
        "z": z,
        "attx": attx,
        "atty": atty,
        "apx": apx
        }
  """
  def status(self):
    str = "** L637-David G2 Status **\n\t%10s\t%10s\t%10s\n" % ("Motor","User","Dial")                                                       
    keys = self.motors.keys()
    keys.sort()
    for key in keys:
       m = self.motors[key]
       str += "\t%10s\t%+10.4f\t%+10.4f\n" % (key,m.wm(),m.wm_dial())
       pass
    return str

  def detailed_status(self, toPrint=True):
    str = "** G2 Detailed Status **\n"
    keys = self.motors.keys()
    keys.sort()
    formatTitle = "%15s %20s  %18s  %4s  %10s  %10s  %10s  %10s  %10s  %10s  %7s  %7s  %7s  %7s  %5s  %5s  %7s\n"
    formatEntry = "%15s %20s  %18s  %4s  %10.4f  %10.4f  %10.4f  %10.4f  %10.4f  %10.4f  %7.1f  %7.1f  %7.1f  %7.1f  %5.1f  %5.1f  %7.1f\n"
    str += formatTitle % ("SXR Name", "EPICS Name", "PV Name", "EGU", "User", "User LL", "User HL", "Dial", "Dial LL", "Dial HL", "Vmin", "Vmin", "Vmax", "Vmax", "Accel", "Decel", "% Run")
    str += formatTitle % ("", "", "", "", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(Rev/s)", "(EGU/s)", "(Rev/s)", "(EGU/s)", "(s)", "(s)", "Current")
    for key in keys:
       m = self.motors[key]
       str += formatEntry % (self.objName+"."+key,m.get_par_silent("description"), m.pvname, m.get_par_silent("units"), m.wm(), m.get_par_silent("low_limit"), m.get_par_silent("high_limit"), m.wm_dial(), m.get_par_silent("dial_low_limit"), m.get_par_silent("dial_high_limit"), m.get_par_silent("s_base_speed"), m.get_par_silent("base_speed"), m.get_par_silent("s_speed"), m.get_par_silent("slew_speed"), m.get_par_silent("acceleration"), m.get_par_silent("back_accel"), float(m.get_par_silent("run_current",":")))
    if (toPrint):
      print str
    else:
      return str
    

  def __repr__(self):
    return self.status()
  """

  pass

  

class Sample(Device):
  """
  Class to control the L637-David Sample Elements for Shifts 1-5

  Motors are:

  apx: cleanup aperture x translation
  apy: cleanup aperture y translation
  sx: sample/diagnostic main x-translation  
  sh: sample fine horizontal translation
  sv: sample fine vertical translation
  sth: sample fine theta rotation
  yagz: yag vertical tranlsation
  bsh: beamstop horizontal translation
  bsv: beamstop vertical translation
  deth: detector horizontal translation
  detv: detector vertical translation
  
  """

  def __init__(self,apx,apy,sx,sh,sv,sth,yagy,bsh,bsv,deth,detv,objName="sample",pvBase=None,presetsfile=None):
     Device.__init__(self,objName,pvBase,presetsfile)
     self.apx = apx
     self.apy = apy
     self.sx = sx
     self.sh = sh
     self.sv = sv
     self.sth = sth
     self.yagy = yagy
     self.bsh = bsh
     self.bsv = bsv
     self.deth = deth
     self.detv = detv
     self.objName=objName
     self.pvBase=pvBase

     self.motors = {
        "apx": apx,
        "apy": apy,
        "sx": sx,
        "sh": sh,
        "sv": sv,
        "sth": sth,
        "yagy": yagy,
        "bsh": bsh,
        "bsv": bsv,
        "deth": deth,
        "detv": detv
        }

  """
  def status(self):
    str = "** L637-David Sample Status **\n\t%10s\t%10s\t%10s\n" % ("Motor","User","Dial")                                                       
    keys = self.motors.keys()
    keys.sort()
    for key in keys:
       m = self.motors[key]
       str += "\t%10s\t%+10.4f\t%+10.4f\n" % (key,m.wm(),m.wm_dial())
       pass
    return str

  def detailed_status(self, toPrint=True):
    str = "** G2 Detailed Status **\n"
    keys = self.motors.keys()
    keys.sort()
    formatTitle = "%15s %20s  %18s  %4s  %10s  %10s  %10s  %10s  %10s  %10s  %7s  %7s  %7s  %7s  %5s  %5s  %7s\n"
    formatEntry = "%15s %20s  %18s  %4s  %10.4f  %10.4f  %10.4f  %10.4f  %10.4f  %10.4f  %7.1f  %7.1f  %7.1f  %7.1f  %5.1f  %5.1f  %7.1f\n"
    str += formatTitle % ("SXR Name", "EPICS Name", "PV Name", "EGU", "User", "User LL", "User HL", "Dial", "Dial LL", "Dial HL", "Vmin", "Vmin", "Vmax", "Vmax", "Accel", "Decel", "% Run")
    str += formatTitle % ("", "", "", "", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(Rev/s)", "(EGU/s)", "(Rev/s)", "(EGU/s)", "(s)", "(s)", "Current")
    for key in keys:
       m = self.motors[key]
       str += formatEntry % (self.objName+"."+key,m.get_par_silent("description"), m.pvname, m.get_par_silent("units"), m.wm(), m.get_par_silent("low_limit"), m.get_par_silent("high_limit"), m.wm_dial(), m.get_par_silent("dial_low_limit"), m.get_par_silent("dial_high_limit"), m.get_par_silent("s_base_speed"), m.get_par_silent("base_speed"), m.get_par_silent("s_speed"), m.get_par_silent("slew_speed"), m.get_par_silent("acceleration"), m.get_par_silent("back_accel"), float(m.get_par_silent("run_current",":")))
    if (toPrint):
      print str
    else:
      return str
    

  def __repr__(self):
    return self.status()
  """

  pass

  
class Sample2(Device):
  """
  Class to control the L637-David Sample Area Elements for shift 5

  Motors are:

  apx: cleanup aperture x translation
  apy: cleanup aperture y translation
  sx: sample/diagnostic main x-translation  
  sh: sample fine horizontal translation    >> to sphi, 1mm -> 1.22'  (0.82mm = 1')
  sv: sample fine vertical translation
  sth: sample fine theta rotation           >>  1mm -> 1.22'  (0.82mm = 1')
  yagz: yag vertical tranlsation
  bsh: beamstop horizontal translation
  bsv: beamstop vertical translation
  deth: detector horizontal translation
  detv: detector vertical translation
  
  """

  def __init__(self,apx,apy,sx,sphi,sv,sth,yagy,bsh,bsv,deth,detv,objName="sample",pvBase=None,presetsfile=None):
     Device.__init__(self,objName,pvBase,presetsfile)
     self.apx = apx
     self.apy = apy
     self.sx = sx
     self.sphi = sphi
     self.sv = sv
     self.sth = sth
     self.yagy = yagy
     self.bsh = bsh
     self.bsv = bsv
     self.deth = deth
     self.detv = detv
     self.objName=objName
     self.pvBase=pvBase

     self.motors = {
        "apx": apx,
        "apy": apy,
        "sx": sx,
        "sphi": sphi,
        "sv": sv,
        "sth": sth,
        "yagy": yagy,
        "bsh": bsh,
        "bsv": bsv,
        "deth": deth,
        "detv": detv
        }

  """
  def status(self):
    str = "** L637-David Sample Status **\n\t%10s\t%10s\t%10s\n" % ("Motor","User","Dial")                                                       
    keys = self.motors.keys()
    keys.sort()
    for key in keys:
       m = self.motors[key]
       str += "\t%10s\t%+10.4f\t%+10.4f\n" % (key,m.wm(),m.wm_dial())
       pass
    return str

  def detailed_status(self, toPrint=True):
    str = "** G2 Detailed Status **\n"
    keys = self.motors.keys()
    keys.sort()
    formatTitle = "%15s %20s  %18s  %4s  %10s  %10s  %10s  %10s  %10s  %10s  %7s  %7s  %7s  %7s  %5s  %5s  %7s\n"
    formatEntry = "%15s %20s  %18s  %4s  %10.4f  %10.4f  %10.4f  %10.4f  %10.4f  %10.4f  %7.1f  %7.1f  %7.1f  %7.1f  %5.1f  %5.1f  %7.1f\n"
    str += formatTitle % ("SXR Name", "EPICS Name", "PV Name", "EGU", "User", "User LL", "User HL", "Dial", "Dial LL", "Dial HL", "Vmin", "Vmin", "Vmax", "Vmax", "Accel", "Decel", "% Run")
    str += formatTitle % ("", "", "", "", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(Rev/s)", "(EGU/s)", "(Rev/s)", "(EGU/s)", "(s)", "(s)", "Current")
    for key in keys:
       m = self.motors[key]
       str += formatEntry % (self.objName+"."+key,m.get_par_silent("description"), m.pvname, m.get_par_silent("units"), m.wm(), m.get_par_silent("low_limit"), m.get_par_silent("high_limit"), m.wm_dial(), m.get_par_silent("dial_low_limit"), m.get_par_silent("dial_high_limit"), m.get_par_silent("s_base_speed"), m.get_par_silent("base_speed"), m.get_par_silent("s_speed"), m.get_par_silent("slew_speed"), m.get_par_silent("acceleration"), m.get_par_silent("back_accel"), float(m.get_par_silent("run_current",":")))
    if (toPrint):
      print str
    else:
      return str
    

  def __repr__(self):
    return self.status()
  """

  pass

  
