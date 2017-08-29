import pypsepics
import time
class motorPV(object):
  def __init__(self,pv,name):
#    Motor.__init__(self,None,name,readbackpv=None,has_dial=False)
    self.name   = name
    self.pvname = pv

  def __call__(self,value):
    self.move(value)

  def __repr__(self):
    return self.status()

  def status(self):
    s  = "Pv motor %s\n" % self.name
    s += "  current position %.4g\n" % self.wm()
    return s

  def move_relative(self,howmuch):
    p = self.wm()
    return self.move(p+howmuch)

  def move_silent(self,value): return self.move(value)

  def mvr(self,howmuch): return self.move_relative(howmuch)

  def  move(self,value): return  pypsepics.put(self.pvname,value)

  def  mv(self,value): return self.move(value)

  def  wm(self): return pypsepics.get(self.pvname)

  def  wait(self): time.sleep(0.02)

