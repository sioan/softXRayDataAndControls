#!/usr/bin/python
# This module provides support 
# for the Gruebel SAXS Chamber
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

class GruebelSaxs:
  """ Class to control the Gruebel SAXS Chamber """

  def __init__(self, samx, samy, samz, pinx, piny, pinz, objName="saxs"):
    self.samx = samx
    self.samy = samy
    self.samz = samz
    self.pinx = pinx
    self.piny = piny
    self.pinz = pinz
    self.objName = objName

    self.motors = {
      "samx": samx,
      "samy": samy,
      "samz": samz,
      "pinx": pinx,
      "piny": piny,
      "pinz": pinz
      }

  def status(self):
    str = "** SAXS Status **\n\t%10s\t%10s\t%10s\n" % ("Motor","User","Dial")
    keys = self.motors.keys()
    keys.sort()
    for key in keys:
       m = self.motors[key]
       str += "\t%10s\t%+10.4f\t%+10.4f\n" % (key,m.wm(),m.wm_dial())
    return str

  def detailed_status(self, toPrint=True):
    str = "** SAXS Detailed Status **\n"
    keys = self.motors.keys()
    keys.sort()
    formatTitle = "%15s %20s  %18s  %4s  %10s  %10s  %10s  %10s  %10s  %10s  %7s  %7s  %7s  %7s  %5s  %5s  %7s\n"
    formatEntry = "%15s %20s  %18s  %4s  %10.4f  %10.4f  %10.4f  %10.4f  %10.4f  %10.4f  %7.1f  %7.1f  %7.1f  %7.1f  %5.1f  %5.1f  %7.1f\n"
    str += formatTitle % ("SXR Name", "EPICS Name", "PV Name", "EGU", "User", "User LL", "User HL", "Dial", "Dial LL", "Dial HL", "Vmin", "Vmin", "Vmax", "Vmax", "Accel", "Decel", "% Run")
    str += formatTitle % ("", "", "", "", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(EGU)", "(Rev/s)", "(EGU/s)", "(Rev/s)", "(EGU/s)", "(s)", "(s)", "Current")
    for key in keys:
       m = self.motors[key]
       str += formatEntry % (self.objName+"."+key,m.get_par("description"), m.pvname, m.get_par("units"), m.wm(), m.get_par("low_limit"), m.get_par("high_limit"), m.wm_dial(), m.get_par("dial_low_limit"), m.get_par("dial_high_limit"), m.get_par("s_base_speed"), m.get_par("base_speed"), m.get_par("s_speed"), m.get_par("slew_speed"), m.get_par("acceleration"), m.get_par("back_accel"), float(m.get_par("run_current",":")))
       pass
     

    """
    # old way not used now
    for key in keys:
       m = self.motors[key]
       egu = m.get_par("units")
       str += "\t%15s\t%15s\n" % ("EPICS Name",m.get_par("description"))
       str += "\t%15s\t%15s\n" % ("PV Name",m.pvname)
       str += "\t%15s\t%15s\n" % ("SXR Name",m.name)
       str += "\t%15s\t%15s\n" % ("Units ('EGU')", egu)
       str += "\t%15s\t%15.4f\n" % ("User Pos (%s)" % (egu),m.wm())
       str += "\t%15s\t%15.4f\n" % ("User LL (%s)" % (egu),m.get_par("low_limit"))
       str += "\t%15s\t%15.4f\n" % ("User HL (%s)" % (egu),m.get_par("high_limit"))
       str += "\t%15s\t%15.4f\n" % ("Dial Pos (%s)" % (egu),m.wm_dial())
       str += "\t%15s\t%15.4f\n" % ("Dial LL (%s)" % (egu),m.get_par("dial_low_limit"))
       str += "\t%15s\t%15.4f\n" % ("Dial HL (%s)" % (egu),m.get_par("dial_high_limit"))
       str += "\t%15s\t%15.4f\n" % ("Vmin (Rev/s)",m.get_par("s_base_speed"))
       str += "\t%15s\t%15.4f\n" % ("Vmin (%s/s)" % (egu),m.get_par("base_speed"))
       str += "\t%15s\t%15.4f\n" % ("Vmax (Rev/s)",m.get_par("s_speed"))
       str += "\t%15s\t%15.4f\n" % ("Vmax (%s/s)" % (egu),m.get_par("slew_speed"))
       str += "\t%15s\t%15.4f\n" % ("Accel (s)",m.get_par("acceleration"))
       str += "\t%15s\t%15.4f\n" % ("Decel (s)",m.get_par("back_accel"))
       str += "\t%15s\t%15.4s\n" % ("Run Current (%)",float(m.get_par("run_current",":")))
       str += "\n"
    """
    if (toPrint):
      print str
    else:
      return str

    
  def __repr__(self):
    return self.status()
