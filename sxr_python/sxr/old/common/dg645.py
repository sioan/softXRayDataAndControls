import pypsepics 
from pypslog import logprint


class DG645_delay_channel(object):
  def __init__ (self,unit="XPP:MOB:DDG:01",channel="A"):
    self.unit=unit+":"+channel.lower()
    r={}; r["T0"]=0; r["A"]=1; r["B"]=2; r["C"]=3; r["D"]=4
    r["E"]=5; r["F"]=6; r["G"]=7; r["H"]=8
    self.__dict_refs=r
  def __pvname(self,what):
    if (what=="delay_ref"): pvname=self.unit+"ReferenceMO"
    elif (what=="delay"):   pvname=self.unit+"DelayAO"
    else: return None
    return pvname
  def get(self,what):
    pvname=self.__pvname(what)
    return pypsepics.get(pvname)
  def set(self,what,value):
    pvname=self.__pvname(what)
    return pypsepics.put(pvname,value)
  def get_delay(self):
    return self.get("delay")
  def set_delay(self,value):
    return self.set("delay",value)
  def set_reference(self,value):
    return self.set("delay_ref",self.__dict_refs[value])

class DG645_amplitude_channel(object):
  def __init__ (self,unit="XPP:MOB:DDG:01",channel="AB"):
    self.unit=unit+":"+channel.lower()
  def __pvname(self,what):
    if (what=="TTL"):   pvname=self.unit+"OutputModeNimSS.PROC"
    elif (what=="polarity"): pvname=self.unit+"OutputPolarityBO"
    elif (what=="amplitude"): pvname=self.unit+"OutputAmpAO"
    elif (what=="offset"): pvname=self.unit+"OutputOffsetAO"
    else: return None
    return pvname
  def get(self,what):
    pvname=self.__pvname(what)
    return pypsepics.get(pvname)
  def set(self,what,value):
    pvname=self.__pvname(what)
    return pypsepics.put(pvname,value)

class DG645_channel(object):
  def __init__(self,unit="XPP:MOB:DDG:01",channel="AB"):
    self.unit=unit
    self.V = DG645_amplitude_channel(unit,channel)
    self.delay = DG645_delay_channel(unit,channel[0])
    self.delay.set_reference("T0");
    self.width = DG645_delay_channel(unit,channel[1])
    self.width.set_reference(channel[0].upper())
    self.channel=channel
    self.name=unit+":"+channel
  def get_width(self):
    return self.width.get("delay")
  def set_width(self,value):
    return self.width.set("delay",value)
  def get_delay(self):
    return self.delay.get("delay")
  def set_delay(self,value):
    return self.delay.set("delay",value)
  def get_amplitude(self):
    return self.V.get("amplitude")
  def set_amplitude(self,value):
    return self.V.set("amplitude",value)
  def get_offset(self):
    return self.V.get("offset")
  def set_offset(self,value):
    return self.V.set("offset",value)
  def get_polarity(self):
    p = self.V.get("polarity")
    if (p==0): return "neg"
    elif (p==1): return "pos"
    else: return None
  def set_polarity(self,value):
    if (value=="pos"): v=1
    elif (value=="neg"): v=0
    else: return None
    return self.V.set("polarity",v)
  def off(self):
    return self.set_amplitude(0.5)
  def on(self,amplitude=4):
    return self.set_amplitude(amplitude)

class DG645(object):
  """ Classc to control DG645 """
  def __init__ (self,unit="XPP:MOB:DDG:01"):
    self.unit=unit
  def __pvname(self,channel,what):
    unit=self.unit+":"+channel.lower()

