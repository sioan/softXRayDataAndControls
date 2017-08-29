import config
import pypsepics
import utilities
from time import time,sleep

class LaserSystem:

  def __init__(self,system=2):
    self.system=system
    self.timeout=20
    self.__pvnames(self.system)

  def use_system(self,system):
    self.system=system
    self.__pvnames(self.system)

  def __pvnames(self,system=None):
    if system is None: system = self.system
    self.__pv_angleshift="LAS:FS%d:Angle:Shift:Ramp:Target" % system
    self.__pv_angleshift_rbv="LAS:FS%d:REG:Angle:Shift:rd" % system
    self.__pv_gain="LAS:FS%d:REG:kp_vcxo:rd" % system
    self.__pv_error="LAS:FS%d:alldiff_fs" % system
    
  def lowgain(self):
    self.gain(1000)

  def higain(self):
    self.gain(18600)

  def gain(self,value=None):
    if (value is None):
      return pypsepics.get(self.__pv_gain)
    else:
      pypsepics.put(self.__pv_gain,value)

  def error(self):
    return pypsepics.get(self.__pv_error)*1e-15
    
  def delay(self,value=None):
    if (value is None):
      return pypsepics.get(self.__pv_angleshift_rbv)*1e-15
    else:
      pypsepics.put(self.__pv_angleshift,value*1e15)

  def wait(self):
    target = pypsepics.get(self.__pv_angleshift)
    t0=time()
    while ( ( abs(self.delay()*1e15-target)>100) & (time()-t0)<self.timeout):
      sleep(0.1)

  def status(self):
    str ="Laser system in use: %s\n" % self.system
    delay = self.delay()
    str+=" current delay (s): %e (%s)\n" % (delay,utilities.time_to_text(delay))
    error = self.error()
    str+=" current phase error (s): %e (%s)\n" % (error,utilities.time_to_text(error))
    gain = self.gain()
    if (gain ==0):
      gain_str="UNLOCKED"
    elif (gain <2000):
      gain_str="LOW"
    else:
      gain_str="HIGH"
    str+=" gain: %f (%s)\n" % (gain,gain_str)
    return str

  def __repr__(self):
    return self.status()

laser=LaserSystem()
