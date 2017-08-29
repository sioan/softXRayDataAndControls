#!/usr/bin/python
# This module provides support
# for generic devices
# for the SXR beamline (@LCLS)
# 
# Author:         Daniel Flath (SLAC)
# Created:        Apr 25, 2013
# Modifications:
#   Apr 25, 2011 DF
#       first version

import numpy as n
import sys
from utilities import estr
import pypsepics
from pypslog import logprint

class Device:
  """
    Base class for beamline devices.

    Add some documentation!
  """

  def __init__(self,objName=None,pvBase=None,presetsfile=None):
     self.objName = objName
     self.pvBase = pvBase
     self.__presetsfile=presetsfile
     self.__globpresets=None
     self.__presets=None

     # fill this out in base classes like "self.motors={"motor1name": motor1object, "motor2name": motor2object, ...}
     self.motors = dict()

  def status(self):
    str = "** %s Status **\n\t%10s\t%10s\t%10s\n" % (self.objName, "Motor","User","Dial")
    keys = self.motors.keys()
    keys.sort()
    for key in keys:
       m = self.motors[key]
       str += "\t%10s\t%+10.4f\t%+10.4f\n" % (key,m.wm(),m.wm_dial())
       pass
    return str

  def detailed_status(self, toPrint=True):
    str = "** %s Detailed Status **\n" % (self.objName)
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


  def presetGenerate(self, name='current_pos'):
    """ Generate a preset position list """
    mnames = self.motors.keys()
    mnames.sort()
    p = "%s = {" % (name)
    i=0
    for mn in mnames:
      if i: p+=", "
      m = self.motors[mn]
      p += "'%s':%f" % (mn,m.wm())
      i+=1
      pass
    p += "}"
    print "Below is a preset string for the current position of the '%s' motors.  Please remove any motors which you do not want to move when activating the preset!\n\n%s" % (self.objName, p) 
    pass

  def __presetsLoad(self):
    if self.__presetsfile is None:
      print "ERROR: no presets file loaded for device %s" % self.objName
      return
    
    self.__globpresets=dict()
    self.__presets=dict()
    execfile(self.__presetsfile, self.__globpresets,self.__presets)
    pass

  # internal.  Expects presets are already loaded
  def __presetGet(self, preset_name):
    if preset_name not in self.__presets.keys():
      print "ERROR No such preset"
    else:
      return self.__presets[preset_name]
    pass

  def presetMove(self, preset_name, confirm=True):
    self.__presetsLoad()

    p = self.__presetGet(preset_name)

    if self.__presetValidate(p):
      print "Moving to preset location '%s'" % preset_name
      self.presetPrint(preset_name)
      if confirm:
          print "\nPerform this move? [N/y] ",
          r = raw_input()
          if r.lower() != 'y':
              return
          pass
      print "OK! Performing Moves"
      mots = p.keys() 
      mots.sort()
      for m in mots:
          self.motors[m].move_silent(p[m])
          pass
      pass
  pass
  
  def presetList(self):
    self.__presetsLoad()
    if self.__presets is None or not len(self.__presets.keys()):
        print "No presets defined"
        return
    print "Available presets:"
    for n in self.__presets.keys():
      print "\t%s" % n
      pass
    pass

  def presetPrint(self,preset_name):
    self.__presetsLoad()
    p = self.__presetGet(preset_name)
    keys = p.keys()
    keys.sort()
    print "Preset name:  '%s'" % preset_name
    print "%15s\t%10s\t%10s\t%10s" % ("motor","position","current","delta")
    for k in keys:
      curpos = self.motors[k].wm()
      delta = curpos - p[k]
      print "%15s\t%10f\t%10f\t%+10f" % (k,float(p[k]),curpos,delta)
      pass
    pass
    

  def __presetValidate(self,preset):
    for m in preset.keys():
      if m not in self.motors.keys():
        print "ERROR: Preset motor '%s' does not exist in device '%s'" % (m,self.objName)
        return False
      pass
    return True    

    pass


  
    
