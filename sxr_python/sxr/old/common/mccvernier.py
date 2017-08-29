import pypsepics
import virtualmotor as vm
import epicsenv as ee
import math
import time

WAIT_TIMEOUT = 10
WAIT_RESOLUTION_THRESHHOLD = 1e-3

class MCCVernier(vm.VirtualMotor):
  def __init__(self, motorsobj, vernier_pv, vernier_ulim_low_pv, vernier_ulim_hi_pv):
    vm.VirtualMotor.__init__(self,
                             motorsobj,
                             "MCC_EPhot",
                             move = self.__move,
                             wm   = self.__wm,
                             wait = self.__wait,
                             set_hilim  = self.__set_hilim,
                             get_hilim  = self.__get_hilim,
                             set_lowlim = self.__set_lowlim,
                             get_lowlim = self.__get_lowlim
                             )
    self.ulim_low_pv = vernier_ulim_low_pv
    self.ulim_hi_pv = vernier_ulim_hi_pv
    self.pvname = vernier_pv
    self.__commanded_position = self.__wm()
    pass

  def __get_lowlim(self):
    return pypsepics.get(self.ulim_low_pv)

  def __get_hilim(self):
    return pypsepics.get(self.ulim_hi_pv)

  def __set_lowlim(self, val):
    pypsepics.put(self.ulim_low_pv, val)

  def __set_hilim(self, val):
    pypsepics.put(self.ulim_hi_pv, val)

  def __move(self, pos):
    ll = self.get_lowlim()
    lh = self.get_hilim()
    if (pos < ll):
      print "ERROR: Commanded position (%.3f) exceeds low soft-limit (%.3f)" % (pos, ll)
      pass
    elif (pos > lh):
      print "ERROR: Commanded position (%.3f) exceeds high soft-limit (%.3f)" % (pos, lh)
      pass
    else:
      pypsepics.put(self.pvname, pos)
      self.__commanded_position = pos
      pass
    pass

  def __wm(self):
    return pypsepics.get(self.pvname)

  def __wait(self):
    ti = time.time()
#    print "xf: %f\nx: %f\ndx: %f\n" % (self.__commanded_position, self.__wm(), math.fabs(self.__wm() - self.__commanded_position))
    while (WAIT_RESOLUTION_THRESHHOLD < math.fabs(self.__wm() - self.__commanded_position)):
      if (WAIT_TIMEOUT < time.time() - ti):
        print "WARNING: timed out before reaching commanded position"
        break
      time.sleep(.1)
      pass
    pass

  pass
