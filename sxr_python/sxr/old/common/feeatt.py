from periodictable import xsf
from periodictable import formula as ptable_formula
import utilitiesAttenuators as utilAtt
import numpy as np
import sys
import utilities as util
import pypsepics
from pypslog import logprint
from time import sleep

class Filter(object):
  """ Class to define filter properties """
  def __init__ (self,pv,material,thickness,invert=False):
    self.pv  = pv
    self.pv_write  = pv + ":CMD"
    self.pv_status = pv + ":STATE"
    self.d   = thickness
    self.material  = material
    self.__Eused = None
    self.__att_len = None
    self.last_command = None
    if (invert):
      self.inpos = 0
    else:
      self.inpos = 1
    self.outpos = not self.inpos
  def att_len(self,E):
    if (E != self.__Eused):
      self.__att_len = utilAtt.getAttLen(E,self.material)
      self.__Eused = E
    return self.__att_len
  def transmission(self,E):
    att_len = self.att_len(E)
    return np.exp(-self.d/att_len)
  def wm(self):
    v = pypsepics.get(self.pv_status)
    if (v == 2):
      return "OUT"
    elif (v == 1):
      return "IN"
    else:
      return "?"
  def movein(self):
    """ move the filter in the defined `in` position
        does not wait for completion of movement"""
#    print "moving in %s" % self.pv
    pypsepics.put(self.pv_write,self.inpos)
  def moveout(self):
    """ move the filter in the defined `out` position
        does not wait for completion of movement"""
#    print "moving out %s" % self.pv
    pypsepics.put(self.pv_write,self.outpos)
  def isin(self):
    """ return True if the filter is in """
    return (self.wm() == "IN")
  def isout(self):
    """ return True if the filter is out """
    return (self.wm() == "OUT")
  def wait(self):
    """ wait for motor to stop moving """
    while (self.wm() == "?"): sleep(0.1)

class Feeatt(object):
  """ module to control the Fee attenuators.
  main user interface:
  defined somewhere att=feesiatt.Feeatt()
  - att.getT();  # returns dictionary with attenuations at fundamental, 3rd
                 # harmonic, total, etc.; also print on screen attenuator
                 #  status
  - att.getTvalue(); # returns total transmission at the working energy as float
  - att.setT(T); # change the atenuators to best mach the required 
                 # transmission value `T`; filters are changed in a "safe" way
                 # first new filters are inserted, then the one not needed are
                 # removed; in this way the transmission is never bigger
                 # than the current or requested value
  - att.setT(T,fast=1): # as above but do ot wait for filter and move all
                 # filters at the same time; good when the beam is stopped in
                 # some way (shutter and or burst mode)
  - att.wait
  - att.setE(E): # set the current working energy to E, if called att.setE()
                 # gets the value from the machine. E can be in eV or keV
  """
  def __init__(self,lclsinstance):
    """ init function; not to be used in an explicit call """
    self.__lcls = lclsinstance
    self.__E = None
    diamond = ptable_formula("C",density=3.515)
    glass   = ptable_formula("SiO2",density=2.201)
    al2o3   = ptable_formula("Al2O3",density=3.98)
    # FIXME:  Removing att[6] temporarily as the motor is broken... (2012/03/05)
    #self.n = 8
    self.n = 9
    self.att=range(self.n)
    self.att[0] = Filter("SATT:FEE1:321",diamond,1.5e-6)
    self.att[1] = Filter("SATT:FEE1:322",diamond,13e-6)
    self.att[2] = Filter("SATT:FEE1:323",diamond,62e-6)
    self.att[3] = Filter("SATT:FEE1:324",diamond,62e-6)
    self.att[4] = Filter("SATT:FEE1:325",diamond,124e-6)
    self.att[5] = Filter("SATT:FEE1:326",diamond,240e-6)
    # for some reason the last 3 attenuators have inverted CMD logic # No more as of 2012-11-20
#    self.att[6] = Filter("SATT:FEE1:327",glass,76e-6,invert=True); changed to 500um diamond on Aug. 24th 2011
    # FIXME:  Removing att[6] temporarily as the motor is broken... (2012/03/05)
    self.att[6] = Filter("SATT:FEE1:327",diamond,500e-6) #2012-11-20# ,invert=True)
    self.att[7] = Filter("SATT:FEE1:328",al2o3,127e-6) #2012-11-20# ,invert=True)
    self.att[8] = Filter("SATT:FEE1:329",al2o3,250e-6) #2012-11-20# ,invert=True)
    # FIXME:  Uncomment above lines and delete below lines
    #self.att[6] = Filter("SATT:FEE1:327",diamond,500e-6,invert=True)
    #self.att[6] = Filter("SATT:FEE1:328",al2o3,127e-6,invert=True)
    #self.att[7] = Filter("SATT:FEE1:329",al2o3,250e-6,invert=True)
    # FIXME: Delete lines above when motor 7 fixed!
    self.setE()

  def allIN(self):
    """ Move all filters in the beam """
    utilAtt.moveIN(self.att)

  def allOUT(self):
    """ Move all filters out of the beam """
    utilAtt.moveOUT(self.att)

  def wait(self):
    """ waits for the motors to stop moving """
    for i in range(self.n):
       self.att[i].wait()

  def setE(self,E=None):
    """ set the energy (in keV) for calculation of transmission
        if called without parameter, it reads the value from the
        machine """
    if ( E is None ):
      self.__E = self.__lcls.getXrayeV()/1e3
    else:
      self.__E=E
    logprint("lusiatt: setting energy for transmission calculation to %.3f keV" % self.__E)
    return self.__E

  def getT(self,E=None,printit=1):
    """ Check which filters are `in` and calculate the transmission
        for the energy defined with the `setE` command
        The finding is returned as dictionary """
    self.wait()
    if (E is None): E = self.__E
    return utilAtt.getT(self.att,E,printit=printit)

  def getTvalue(self,E=None):
    """ returns float with current transmission. (for the energy previously set)
    """
    if (E is None): E = self.__E
    return utilAtt.getTvalue(self.att,E)


  def status(self):
    (v,s)=self.getT(printit=0)
    return s

  def __repr__(self):
    return self.status()

  def setTfast(self,transmission,E=None,printit=0,domove=1):
    """ as setT but it dows not wait for motors ... (and IN and OUT commands
        are sent at the sae time"""
    self.setT(transmission,fast=True,E=E,printit=printit,domove=domove)

  def setT(self,transmission,fast=False,E=None,printit=1,domove=1):
    """ Determines which filters have to be moved in othe beam to
        achieve a transmission as close as possible to the requested one.
  Note : the function moves the filters
  Note2: use the `setE` command before to choose which energy 
         to use for calculation"""
    if (transmission==1):
      self.allOUT()
      return 1.
    if ( (E is None) and  (self.__E is None) ) : 
      self.setE()
      E=self.__E
    elif ( (E is None) and (self.__E is not None) ):
      E=self.__E
    T=utilAtt.setT(self.att,transmission,E,fast,printit,domove)
    return T
