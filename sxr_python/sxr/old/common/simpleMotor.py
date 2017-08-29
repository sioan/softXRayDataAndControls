import numpy as np
import sys
import utilities as util
import pypsepics
from pypslog import logprint

class SimpleMotor(object):
  """ Class to run a simple motor """
  def __init__ (self,motor,inpos=20,outpos=0.5):
    self.motor  = motor
    self.inpos=inpos
    self.outpos=outpos
  def wm(self):
    return self.motor.wm()
  def move(self,val):
    return self.motor.move(val)
  def mv(self,val):
    return self.motor.mv(val)
  def mvr(self,val):
    return self.motor.mvr(val)
  def movein(self):
    """ move the motor in the defined `in` position
        does not wait for completion of movement"""
    self.motor.move(self.inpos)
  def moveout(self):
    """ move the motor in the defined `out` position
        does not wait for completion of movement"""
    self.motor.move(self.outpos)
  def isin(self,pos=None):
    """ return True if the motor is within 100um from 
        the predined `in` position"""
    if (pos == None):
      pos = self.motor.wm()
    return ( abs(pos-self.inpos)<0.1 )
  def isout(self,pos=None):
    """ return True if the motor is within 100um from 
        the predined `out` position"""
    if (pos== None): pos = self.motor.wm()
    return ( abs(pos-self.outpos)<0.1 )
  def wait(self):
    """ wait for motor to stop moving """
    return self.motor.wait()

  def status(self):
    return self.motor.status()

  def __repr__(self):
    return self.status()
