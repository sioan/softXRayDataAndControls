#!/usr/bin/python
# This module provides support 
# for the SXR Large Area Detector Mover (LADM or LAM)
# for the SXR beamline (@LCLS)
# 
# Author:         Daniel Flath (SLAC)
# Created:        Nov 12, 2011
# Modifications:
#   Nov 12, 2011 DF
#       first version

import numpy as n
from numpy import rad2deg,arcsin,sqrt,tan
import sys
from utilities import estr
import pypsepics
from pypslog import logprint
from motor import Motor as psmotor
from donemoving import donemoving


class PulsePicker:
  """ Class to control PulsePicker """

  def __init__(self,x,y,r,seq,evr,code_pp,code_daq,r_offset,r_swing=22.5,name="Picker_rev2"):
    self.x   = x
    self.y   = y
    rmot = pickerRotation(r.pvname,r.name)
    self.donemoving  = donemoving(r.pvname)
    self.r   = rmot
    self.seq = seq
    self.evr = evr
    self.code_pp = code_pp
    self.code_daq = code_daq
    self.r_swing = r_swing
    self.r_offset = r_offset
    self.name = name
    self.motors = {
      "x": x,
      "y": y,
      "r": r
      }
  def home(self):
    self.r.home()
    self.donemoving.wait_for_done(20)
    
  def move_delay(self,delay):
    self.evr.setDelay(delay)
  def get_delay(self):
    return self.evr.getDelay()

  def set_burst(self,Nshots,isseq=True):
    self.Nburstshot = Nshots
    self.evr.
    if isseq:
      self.seq.modeOnce()
      self.seq.setnsteps(Nshots+1)
      self.seq.setstep(0,self.code_pp,2)
      for seqstep in range(1,Nshots):
	self.seq.setstep(0,self.code_daq,1)
    
    if Nshots = 1:
      self.r._set_mode(1)
    elif (Nshots >1) and (Nshots < (2048-1)):
      self.r._set_mode(3)
    self.r._set_N(Nshots-1)

  def start_burst(self):
  
    while self.r._get_armed()==1: sleep(.001)
    self.r._set_armed(0)
    while self.r._get_armed()==0: sleep(.001)
    if self.Nburstshot > 1:
      self.r._set_go(1)
      while self.r._get_go()==0:    sleep(.001)
    self.r._set_armed(1)
    while self.r._get_armed()==1: sleep(.001)

    self.seq.start()




    
  #def status(self
    #str = "** %s Status **\n\t%10s\t%10s\t%10s\n" % (self.name,"Motor","User","Dial")
    #keys = self.motors.keys()
    #keys.sort()
    #for key in keys:
       #m = self.motors[key]
       #str += "\t%10s\t%+10.4f\t%+10.4f\n" % (key,m.wm(),m.wm_dial())
    #return str
  
  #def __repr__(self):
    #return self.status()

picker_params = {
    'home':        ('FW_MEANS',  'find homeswitch forward'),	
    'reset':       ('RESET_PG',  'set position zero'),	
    'normal_speed':('SETUP_30HZ',  'set to the normal speed'),	
    'setmode':     ('SET_SE',  'set the running mode'),	
    'rdmode':      ('SE',  'read the running mode'),	
    'setarm':     ('SET_TG',  'set armed'),	
    'rdarm':      ('TG',  'read armed '),	
    'setgo':     ('SET_GO',  'set armed'),	
    'rdgo':      ('GO',  'read armed '),	
    'setNshots':   ('SET_N',  'set N shots (burst)'),	
    'rdNshots':    ('N',  'read N shots (burst)')
    }
modes = ['single', 'reduction', 'burst']
class pickerRotation(psmotor):
   #def __init__(pvname, ):


  def home(self):
    self.pp_put_par('home',1)

  def _set_mode(self,value,silent = False):

    if value in [1,2,3]:
      if not silent:
        print "Setting pulse picker to %s mode" %(modes[value])
      value = long(value)
      self.pp_put_par('setmode',value)
    else:
      print "Mode must be 1, 2 or 3"
    
  def _get_mode(self,silent = False):
    value = self.pp_get_par('rdmode')
    return value
  mode = property(_get_mode,_set_mode)
    

  def reset(self,silent = False):
    if not silent:
      print "Resetting pulse picker rotation"
    self.pp_put_par('reset',1)
    

  def _set_armed(self,val,silent = True):
    if not silent:
      print "Arming pulse picker"
    self.pp_put_par('setarm',val)
    
  def _get_armed(self,silent = True):
    armed = self.pp_get_par('rdarm')
    return armed
  armed = property(_get_armed,_set_armed)

  def _set_go(self,val,silent = True):
    if not silent:
      print "pp action"
    self.pp_put_par('setgo',val)
    
  def _get_go(self,silent = True):
    go = self.pp_get_par('rdgo')
    return armed
  gofield = property(_get_go,_set_go)


  def _set_N(self,val,silent = True):
    if not silent:
      print ""
    self.pp_put_par('setNshots',val)
    
  def _get_N(self,silent = True):
    N = self.pp_get_par('rdNshots')
    return N
  Nshots = property(_get_N,_set_N)



  def pp_get_pvname(self,parname,sep=":"):
    return self.pvname + sep + picker_params[parname][0]

  def pp_get_par(self,parname,sep=":"):
    pv = self.pp_get_pvname(parname,sep)
    return pypsepics.get(pv)

  def pp_get_par_silent(self,parname,sep=":"):
    try:
      val = self.pp_get_par(parname,sep)
    except pyexc, e:
      val = numpy.nan
    return val

  def pp_get_pv(self,pvpar,sep=":"):
    return pypsepics.get(self.pvname + sep + pvpar)

  def pp_put_par(self,parname,value):
    pv = self.pp_get_pvname(parname)
    return pypsepics.put(pv,value)
