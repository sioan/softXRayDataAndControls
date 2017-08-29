import pypsepics
from numpy import sqrt
import time
from donemoving import donemoving

class Linac:
  def __init__(self):
    ## machine parameters
#    self.sim_mode    = False
    self.__evpv        = "SIOC:SYS0:ML00:AO627"
    self.__BeTpv       = "SATT:FEE1:320:RACT"
    self.__BeMilspv    = "SATT:FEE1:320:TACT"
    self.__ebeamratepv = "EVNT:SYS0:1:LCLSBEAMRATE"
    self.__isburstmodeenabled_pv = "IOC:BSY0:MP01:REQBYKIKBRST"
    self.__burstDelivered_pv = donemoving("PATT:SYS0:1:MPSBURSTCTRL")
    self.__freqs={}
    self.__freqs["Full"]=0
    self.__freqs["full"]=0
    self.__freqs["30Hz"]=1
    self.__freqs["10Hz"]=2
    self.__freqs["5Hz"]=3
    self.__freqs["1Hz"]=4
    self.__freqs["0.5Hz"]=5
    self.__dictRateToEnum = {0.5:5, 1:4, 5:3, 10:2, 30:1, 120:0, 0:0}

  def getBeL(self):
    return pypsepics.get(self.__BeMilspv)/1e3*25.4e-3

  def getBeT(self):
    return pypsepics.get(self.__BeTpv)

  def getXrayeV(self):
    return pypsepics.get(self.__evpv)

  def isburstenabled(self):
    v = pypsepics.get(self.__isburstmodeenabled_pv)
    if (v == 1):
      return True
    else:
      return False

  def get_shot(self):
    self.set_nburst(1)
    time.sleep(0.03); # make sure PV is written before executing
    pypsepics.put("PATT:SYS0:1:MPSBURSTCTRL",1)

  def get_burst(self,n=None,wait=False):
    if n is not None:
      self.set_nburst(n)
      time.sleep(0.03); # make sure PV is written before executing
#    if wait:
#      pypsepics.
    pypsepics.put("PATT:SYS0:1:MPSBURSTCTRL",1)

  def stop_burst(self):
    pypsepics.put("PATT:SYS0:1:MPSBURSTCTRL",0)
    self.set_nburst(1)

  def burst_forever(self):
    self.set_nburst(-1)
    pypsepics.put("PATT:SYS0:1:MPSBURSTCTRL",1)

  def set_nburst(self,n):
    if (n=="forever"): n=-1
    pypsepics.put("PATT:SYS0:1:MPSBURSTCNTMAX",int(n))

  def set_fburst(self,f="Full"):
    f.replace(" ",""); # remove spaces
    if not (f in self.__freqs):
      print "!! Frequency should be one of:",
      print self.__freqs.keys()
    else:
      pypsepics.put("PATT:SYS0:1:MPSBURSTRATE",self.__freqs[f])

  def set_burst_rate(self,rate):
    if not (rate in self.__dictRateToEnum):
      print "!! Rate should be one of:",
      print self.__dictRateToEnum.keys()
    else:
      pypsepics.put("PATT:SYS0:1:MPSBURSTRATE",self.__dictRateToEnum[rate])

  def get_fburst(self):
      v=pypsepics.get("PATT:SYS0:1:MPSBURSTRATE")
      if (v==0): 
        return self.get_ebeamrate()
      elif (v==1):
        return 30.
      elif (v==2):
        return 10.
      elif (v==3):
        return 5.
      elif (v==4):
        return 1.
      elif (v==5):
        return 0.5
      else:
        return 0.

  def get_ebeamrate(self):
      return pypsepics.get(self.__ebeamratepv)


  def get_xraybeamrate(self):
      if (self.isburstenabled()):
        return self.get_fburst()
      else:
        return self.get_ebeamrate()

  def wait_burst(self, timeout=1.0):
    self.__burstDelivered_pv.wait_for_done(float(timeout))
    time.sleep(0.2)
    #while(pypsepics.get("PATT:SYS0:1:MPSBURSTCTRL") != 0):
    #  time.sleep(0.02)
    #  print "wait"

  def wait_for_shot(self,verbose=False):
    # to make sure the PV is written (otherwise a sequence get_shot(); wait_for_shot()
    # may fail
    time.sleep(0.03);
    t0 = time.time()
    while( pypsepics.get("PATT:SYS0:1:MPSBURSTCTRL") != 0):
      time.sleep(0.02)
    if (verbose):
      print 'waited %.3f secs for shots' % (time.time()-t0)

  def GeV_to_keV(self,Eelectron_in_GeV):
    und_period = 3; # in cm
    und_K = pypsepics.get("USEG:UND1:150:KACT")
    return 0.95*Eelectron_in_GeV**2/(1+und_K**2/2)/und_period

  def KeV_to_GeV(self,Exray_in_keV):
    und_period = 3; # in cm
    und_K = pypsepics.get("USEG:UND1:150:KACT")
    return sqrt( (1+und_K**2/2)*und_period*Exray_in_keV/0.95 )
