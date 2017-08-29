#!/usr/bin/python
# This module provides support 
# PIM (profile intensity monitor) devices
# for the XPP beamline (@LCLS)
# 
# Author:         Marco Cammarata (SLAC)
# Created:        June 14, 2010
# Modifications:
#   June 14, 2010 MC
#       first version


import numpy as n
import sys
from utilities import estr
import pypsepics

class PIM:
  """ Class to control the XPP PIM """
  def __init__(self,screen_motor,zoom_lens_motor,lens_focus_motor=None,led=None,det=None,desc="PIM",zoomPV=None):
		self.y = screen_motor
		self.zoom  = zoom_lens_motor
#		if not lens_focus_motor==None:
                self.focus = lens_focus_motor
		self.__led = led
		self.__desc = desc
		self._screen_in_pos = 0
		self._diode_in_pos = 26
		self._all_out_pos = -51.99999995
		self.__det = det
		self.__zoomPV = zoomPV

  def zoomlvl(self,level=None):
    """Set or get zoom level

Usage:
  zoomlvl()  --> Get zoom level
  zoomlvl(4) --> Set zoom to level 4
    """
    if not self.__zoomPV:
      print "Must have zoom level PV"
      return
    if not level: 
      return pypsepics.get(self.__zoomPV + ':CUR_ZOOM')
    elif 1 <= level <= 12:
      print "Zooming to level", level
      pypsepics.put(self.__zoomPV + ':DES_ZOOM', level)
    else: 
      return "Argument must be between 1 and 12"

  def zoomlvl_calibrate(self):
    """Self calibration for navitar zoom level"""
    from time import sleep
    low_percent = 1
    high_percent = 65
    print 'Finding lower limit...' 
    self.zoom.move(low_percent)
    while self.zoom.ismoving():
      pass
    (status,msg) = self.zoom.check_limit_switches()
    while status is not 'low': 
      self.zoom.mvr(-1)
      while self.zoom.ismoving(): 
        pass
      (status,msg) = self.zoom.check_limit_switches()
    max_out = pypsepics.get(self.zoom.pvname + '.RMP')
    pypsepics.put(self.__zoomPV + ':MAX_OUT', max_out)
    pypsepics.put(self.zoom.pvname + ':SET_ZERO.PROC', 1)
    print '...Done.'
    sleep(2)
    print 'Finding upper limit...'
    self.zoom.move(high_percent)
    sleep(1)
    while self.zoom.ismoving():
      pass
    (status,msg) = self.zoom.check_limit_switches()
    while status is not 'high': 
      self.zoom.mvr(1)
      while self.zoom.ismoving(): 
        pass
      (status,msg) = self.zoom.check_limit_switches()
    max_in = pypsepics.get(self.zoom.pvname + '.RMP')
    pypsepics.put(self.__zoomPV + ':MAX_IN', max_in)
    print '...Done.'
    print 'Finished calibrating' 
 
  def lightoff(self):
    pypsepics.put(self.__led,0);

  def lighton(self,level=100):
    pypsepics.put(self.__led,level);

  def __getlight(self):
    import pyca
    try: 
      l=pypsepics.get(self.__led)
      return l
    except pyca.pyexc:
      return "Not connected"
  def set_screen_in(self,pos):
    self._screen_in_pos = pos
  def set_diode_in(self,pos):
    self._diode_in_pos = pos
  def set_all_out(self,pos):
    self._all_out_pos = pos
       
  def screen_in(self):
	  self.y.move(self._screen_in_pos)
  def diode_in(self):
    if (self.__getlight() != "Not connected" and self.__getlight() > 1):
		  print "Note: the LED light is not off, use .lightoff() to switch it off"
    self.y.move(self._diode_in_pos)
  def all_out(self):
    self.y.move(self._all_out_pos)
  def __repr__(self):
    return self.status()
  def status(self):
		tolerance=2*self.y.get_par("retry_deadband")
		str  = estr("%s " % self.__desc,color="black",type="bold")
		pos = self.y.wm()
#		if ( abs(pos-self._screen_in_pos)<5e-3 ):
		if ( abs(pos-self._screen_in_pos)<tolerance ):
			str += "screen is %s\n" % estr("IN",type="normal")
		elif ( abs(pos-self._diode_in_pos)<tolerance ):
			str += "diode is %s\n" % estr("IN",type="normal")
		elif ( abs(pos-self._all_out_pos)<tolerance ):
			str += "all elements are %s\n" % estr("OUT",color="green",type="normal")
		else:
			str += "%s\n" % estr("UNKOWN position",type="normal")
		str += " zoom %.1f%%\n" % self.zoom.wm()
                if (self.focus is not None):
                  str += " focus %.1f%%\n" % self.focus.wm()
		if (self.__led is not None):
			str += " light level %s%%\n" % self.__getlight()
	#	if (self.__det is not None):
	#		str += " %s" % self.__det.status()
		return str
