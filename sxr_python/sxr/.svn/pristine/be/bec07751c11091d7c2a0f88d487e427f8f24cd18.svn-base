#!/usr/bin/python
# This module provides support for PV based monitors
# 
# Author:         Marco Cammarata (SLAC)
# Created:        Aug 5, 2010
# Modifications:
#   Aug 5, 2010 MC
#       first version

import pypsepics
from numpy import nan,array,sqrt,isfinite

class PVdetector:
  """A simple class to handle PV based detectors"""
  def __init__(self,pvname,mne_name):
    self.pvname = pvname
    self.name   = mne_name
    self.__monitorlist=[]

  def get(self):
    try:
      v=pypsepics.get(self.pvname)
    except:
      v=1e1000/1e1000
    return v

#  def monitor_in_terminal_start(self):
#    camonitor(self.pvname)

  def monitor_start(self):
    pypsepics.monitor_start(self.pvname)
#    camonitor(self.pvname,writer=self.__monitorlist.append)

  def monitor_clear(self):
    pypsepics.monitor_clear(self.pvname)
#    del self.__monitorlist
#    self.__monitorlist=[]

  def monitor_stop(self):
    pypsepics.monitor_stop(self.pvname)
#    camonitor_clear(self.pvname)

  def monitor_get(self):
    return pypsepics.monitor_get(self.pvname)

  def cleanup(self):
    self.monitor_stop()
    self.monitor_clear()
      
class detector:
  """A simple class to handle Pv based detectors"""
  def __init__(self,pvname="XPP:IOC:USERPV:SB2:IPM",namebase="",kind="NotKnown",timeout=15):
    self.__kind = kind
    if (namebase == ""):
      namebase = pvname
    if (kind.lower() == "ipm"):
      self.ch0 =  PVdetector( pvname + ":CH0" ,namebase+".ch0" )
      self.ch1 =  PVdetector( pvname + ":CH1" ,namebase+".ch1" )
      self.ch2 =  PVdetector( pvname + ":CH2" ,namebase+".ch2" )
      self.ch3 =  PVdetector( pvname + ":CH3" ,namebase+".ch3" )
      self.sum =  PVdetector( pvname + ":SUM" ,namebase+".sum")
      self.xpos = PVdetector( pvname + ":XPOS",namebase+".xpos")
      self.ypos = PVdetector( pvname + ":YPOS",namebase+".ypos")

    if (kind.lower() == "pim"):
      self.ch0 =  PVdetector( pvname + ":CH0" ,namebase+".ch0" )
      self.ch1 =  PVdetector( pvname + ":CH1" ,namebase+".ch1" )
      self.ch2 =  PVdetector( pvname + ":CH2" ,namebase+".ch2" )
      self.ch3 =  PVdetector( pvname + ":CH3" ,namebase+".ch3" )

  def __repr__(self):
    return self.status()

  def status(self):
    str=""
    if (self.__kind=="ipm"):
      str  = " %10s %6s %6s %10s %10s %10s %10s\n" % ("sum", "xpos","ypos","ch0(up)","ch1(north)","ch2(down)","ch3(south)")
      str += "  %+10.3e %+6.3f %+6.3f " % ( self.sum.get(),self.xpos.get(),self.ypos.get() )
      str += "%10.3e %10.3e %10.3e %10.3e\n" % ( self.ch0.get(),self.ch1.get(),self.ch2.get(),self.ch3.get() )
    if (self.__kind=="pim"):
      str  = " %10s %10s %10s %10s\n" % ("ch0(up)","ch1(north)","ch2(down)","ch3(south)")
      str += "%10.3e %10.3e %10.3e %10.3e\n" % ( self.ch0.get(),self.ch1.get(),self.ch2.get(),self.ch3.get() )
    return str
