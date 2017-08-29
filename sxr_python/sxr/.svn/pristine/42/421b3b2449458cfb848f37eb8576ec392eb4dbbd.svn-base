from periodictable import xsf
from periodictable import formula as ptable_formula
import utilitiesAttenuators as utilAtt
import numpy as np
import sys
import utilities as util
import pypsepics
from pypslog import logprint

class Filter(object):
  """ Class to define filter properties """
  def __init__ (self,motor,material,thickness,inpos=20,outpos=0.5):
    self.motor  = motor
    self.d   = thickness
    self.material  = material
    self.inpos=inpos
    self.outpos=outpos
    self.__Eused = None
    self.__att_len = None
  def att_len(self,E):
    if (E != self.__Eused):
      self.__att_len = utilAtt.getAttLen(E,self.material)
      self.__Eused = E
    return self.__att_len
  def transmission(self,E):
    att_len = self.att_len(E)
    return np.exp(-self.d/att_len)
  def wm(self):
    return self.motor.wm()
  def movein(self):
    """ move the filter in the defined `in` position
        does not wait for completion of movement"""
    self.motor.move(self.inpos)
  def moveout(self):
    """ move the filter in the defined `out` position
        does not wait for completion of movement"""
    self.motor.move(self.outpos)
  def isin(self,pos=None):
    """ return True if the filter is within 100um from 
        the predined `in` position"""
    if (pos == None):
      pos = self.motor.wm()
    return ( abs(pos-self.inpos)<0.1 )
  def isout(self,pos=None):
    """ return True if the filter is within 100um from 
        the predined `out` position"""
    if (pos== None): pos = self.motor.wm()
    return ( abs(pos-self.outpos)<0.1 )
  def wait(self):
    """ wait for motor to stop moving """
    return self.motor.wait()

class Lusiatt(object):
  """ module to control the Lusi Si attenuators.
  main user interface:
  defined somewhere att=lusisiatt.Lusiatt(m.vector_with_filter,lcls)
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
  def __init__(self,filter_motors,lclsinstance,PVbase=None,minE=0.):
    """ init function; not to be used in an explicit call """
    self.__lcls = lclsinstance
    self.__E = None
    self.att=[]
    self.n = 10
    self.att=range(self.n)
    silicon=ptable_formula("Si")
    self.PVbase = PVbase
    self.minE = minE # minimum allowed energy (in keV) for transmission setting
    for i in range(self.n):
      #filt[i].set_deadband(0.1); # these motors are a bit flacky ..
      self.att[i] = Filter(filter_motors[i],silicon,20e-6*pow(2,i))
    # filter4 has some sort of damage at 20mm

    self.att[3] = Filter(filter_motors[3],silicon,20e-6*pow(2,3),inpos=20)
    self.att[1] = Filter(filter_motors[1],silicon,20e-6*pow(2,1),inpos=20)
    
 #AR: XPP lines for damaged att    self.att[3] = Filter(filter_motors[3],silicon,20e-6*pow(2,3),inpos=19)
 #AR: XPP lines for damaged att    self.att[1] = Filter(filter_motors[1],silicon,20e-6*pow(2,1),inpos=22)
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
    if (E is None):
      E = self.__E
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
#    if (transmission==1):
#      self.allOUT()
#      return 1.
    if ( (E is None) and  (self.__E is None) ) : 
      self.setE()
      E=self.__E
    elif ( (E is None) and (self.__E is not None) ):
      E=self.__E
    # Safety check - don't move attenuators if energy lower than threshold
    if E < self.minE:
        print 'Attenuator movement prohibited!'
        print 'Enery is currently set to %.2f keV which is less than the minimum allowed energy of %.2f keV'%(E, self.minE)
        print 'Please use setE to either re-grab the energy value from the machine or explicitly set an energy value to use.'
        return
    (T,T3)=utilAtt.setT(self.att,transmission,E,fast,printit,domove)
    if (self.PVbase is not None):
      pypsepics.put(self.PVbase + ":ATT:T",T)
      pypsepics.put(self.PVbase + ":ATT:T3",T3)
      pypsepics.put(self.PVbase + ":ATT:E",E)
    return T


