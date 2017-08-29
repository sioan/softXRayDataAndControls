#from motor import Motor
def __unsupported__(*args):
  print "Unsupported Operation"
  return None
  

class VirtualMotor(object):
  def __init__(self,
               motorsobj,
               name,
               move,
               wm,
               wait=__unsupported__,
               set=__unsupported__,
               set_hilim=__unsupported__,
               get_hilim=__unsupported__,
               set_lowlim=__unsupported__,
               get_lowlim=__unsupported__,
               get_uhilim=__unsupported__,
               get_ulowlim=__unsupported__,
               wm_dial=None,
               egu="mm"):
#    Motor.__init__(self,None,name,readbackpv=None,has_dial=False)
    self.name   = name
    self.motor_name = name
    self.move   = move
    self.wm     = wm
    if wm_dial is None:
      self.wm_dial = self.wm
    self.wait   = wait
    self.set    = set
    self.set_hilim    = set_hilim
    self.set_lowlim    = set_lowlim
    self.get_hilim    = get_hilim
    self.get_lowlim    = get_lowlim
    self.get_uhilim = get_uhilim
    self.get_ulowlim = get_ulowlim
    self.move_silent = move
    self.pvname = 'virtual motor'
    self.egu=egu
    motorsobj.__setattr__(self.name,self)

    self.motors=[]


  def __call__(self,value):
    self.move(value)

  def __repr__(self):
    return self.status()

  def status(self):
    s  = "virtual motor %s\n" % self.name
    s += "  current position %.5g\n" % self.wm()
    return s

  def move_relative(self,howmuch):
    p = self.wm()
    self.move(p+howmuch)

  def mvr(self,howmuch): self.move_relative(howmuch)

  def mv(self,value):    self.move(value)

  def move_wait(self,value):
    self.move(value)
    self.wait()
    pass

  def set(self,value):   self.set(value)

  def get_position(self): return self.wm()

  def is_in_range(self,pos):
    return not (pos < self.get_lowlim() or pos > self.get_hilim())

  def why_outside_range(self,pos):
    if (pos < self.get_ulowlim()):
      return "Position (%f%s) exceeds user low-limit (%f%s) for '%s.'" % (pos, self.egu, self.get_ulowlim(), self.egu, self.motor_name())
    elif (pos > self.get_uhilim()):
      return "Position (%f%s) exceeds user high-limit (%f%s) for '%s.'" % (pos, self.egu, self.get_uhilim(), self.egu, self.motor_name())
    else:
      return "Position (%f%s) is within user limits [%f,%f]%s for '%s.'" % (pos, self.egu, self.get_ulowlim(), self.get_uhilim(), self.egu, self.motor_name())
    pass
  

  def checkLimits(self):
    # TODO: Fix this, it could cause problems in coordinated motion
    return 0
