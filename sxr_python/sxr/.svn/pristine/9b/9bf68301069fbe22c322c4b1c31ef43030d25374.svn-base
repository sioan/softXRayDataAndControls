# v1.0, 2011/04/13, Marco Cammarata, first release

""" 
  pypsepics module
  calls to put(pvname),get(pvname), monitor_*(pvname) add the pvname to
  a list of PVs that are cached (meaning the connections are kept open
  for faster access);
  monitor_* functions are currently used for waiting motors to stop
  and to get data from the DAQ (diodes reaing send out as PV)
  Functions can be accessed two ways
  1. pypsepics.{get|put|monitor_*}(pvname)
  2. pypsepics.g_pv_chache_list[pvname].{get|put|monitor_*}()
  The second method might be convenient if used as follow:
    mypv = pypsepics.g_pv_chache_list[mypvname]
    and then mypv.monitor_start(), mypv.monitor_stop(), etc..
  To add a pv to the cache list you can use pypsepics.add_pv_to_cache(mypvname)

  Usage example:
  import pypsepics
  import time
  pvname = "XPP:SB3:MMS:01"
  pypsepics.get(pvname);
  pypsepics.put(pvname,3);
  pypsepics.monitor_start(pvname);
  time.sleep(3); # do something with the PV
  pypsepics.monitor_stop(pvname);
  print pypsepics.monitor_get(pvname)
  pypsepics.monitor_clear(pvname)
  
  import pypsepics
  import time
  pvname = "XPP:SB3:MMS:01"
  pv =pypsepics.add_pv_to_cache(pvname);
  pv.get()
  pv.put(3);
  pv.monitor_start();
  time.sleep(3); # do something with the PV
  pv.monitor_stop();
  print pv.monitor_get()
  pv.monitor_clear()
"""

import pyca
from psp.Pv import Pv as pycaPv
from pypslog import logprint
import config
import time
import numpy

g_pv_chache_list={}
time_out_connect = 1.
#time_out_get = 1.
time_out_get = 1. # temporary because of saxs.samx
DEBUG=0

def add_pv_to_cache(pvname):
  """ Check if pvname is in cache list and adds it if not present """
  if not (pvname in g_pv_chache_list):
    g_pv_chache_list[pvname]=PV(pvname)
  return g_pv_chache_list[pvname]

def is_debug_on():
  """ Return debug level based on local or global DEBUG """
  return 0
  return max(DEBUG,config.DEBUG)

class PV(pycaPv):
  """ defines PV class; it wraps the pyca Pv class addind monitoring 
      capabilities """
  def __init__(self, name):
    pycaPv.__init__(self, name)
    self.connect(time_out_connect)
    self.monitor_cb = self.monitor_handler
    self.values=[]
    self.ismonitored=False
    self.last_update="Never"

  def isconnected(self):
    """ returns 1 if connected (more tests are needed) """
    try:
      state = self.state()
      return True
    except:
      return False

  def timestr(self):
    """ make a time string (with ns resolution) using PV time stamp """
    ts = time.localtime(self.secs+pyca.epoch)
    tstr = time.strftime("%Y-%m-%d %H:%M:%S", ts)
    tstr = tstr + ".%09d" % self.nsec
    return tstr

  def monitor_handler(self, exception=None):
    """ monitor handler, defines what happens when a new value arrives;
        Currently a new values is added to the `values` list """
    try:
      if exception is None:
#        if self.status == pyca.NO_ALARM:
          self.last_update = self.timestr()
          self.values.append(self.value)
          if ( is_debug_on() ):
            print "monitoring %s %s" % (self.name,self.timestr()),
            print self.value
      else:
        print "%-30s " %(self.name), exception
    except Exception, e:
      print e

  def get(self,handle_no_ioc=True):
    """ returns current value for the Pv """
    if ( is_debug_on() ):
      logprint("caget %s: " % self.name)
    try:
      pycaPv.get(self,False,time_out_get)
      self.last_update = self.timestr()
      if ( is_debug_on() ):
        logprint("got %s\n" % self.value.__str__())
      return self.value
    except pyca.pyexc:
        logprint("caget %s: " % self.name,newline=False)
        logprint("failed (PV timed out) !!, returning nan")
        return numpy.nan
      
  def put(self,value):
    """ put value to the Pv, returns the value itself """
    if ( is_debug_on() ):
      logprint("caput %s in %s\n" % (value,self.name))
    pycaPv.put(self,value,time_out_get)
    return value

  def monitor_start(self):
    """ start monitoring for the Pv, new values are added to the `values` 
        list """
    evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM
    self.monitor(evtmask, ctrl=False)
    self.ismonitored=True
    pyca.flush_io()
#    self.values=[]
    if ( is_debug_on() ): logprint("start monitoring for %s" % self.name)

  def monitor_stop(self):
    """ stop  monitoring for the Pv, note that this does not clear the 
        `values` list """
    self.unsubscribe()
    self.ismonitored=False
    if ( is_debug_on() ): logprint ("stop monitoring for %s" % self.name)

  def monitor_clear(self):
    """ clear the `values` list """
    self.values=[]
    if ( is_debug_on() ): logprint( "clear monitoring for %s" % self.name)

  def monitor_get(self):
    """ retuns statistics for the current `values` list as dictionary """
    # skip first 'pulse' because its values comes from before monitoring ..
    a=numpy.array(self.values[1:])
    ret = {}
    if (len(a)==0):
      ret["mean"]=ret["std"]=ret["num"]=ret["err"]=numpy.nan
      ret["num"]=0
      if ( is_debug_on() ):
        logprint("No pulses.... while monitoring %s" % self.name)
      return ret
    # remove "bad readings"
    ret["mean"]=a.mean()
    ret["std"] =a.std()
    ret["num"] =len(a)
    ret["err"] =ret["std"]/numpy.sqrt(ret["num"])
    if ( is_debug_on() ):
      logprint("get monitoring for %s" % self.name)
    return ret

def monitor_start(pvname):
  """ start monitoring for pvname, pvname is added to the cache list """
  add_pv_to_cache(pvname)
  g_pv_chache_list[pvname].monitor_start()
  
def monitor_stop(pvname):
  """ stop monitoring for pvname, pvname is added to the cache list """
  add_pv_to_cache(pvname)
  g_pv_chache_list[pvname].monitor_stop()
  
def monitor_clear(pvname):
  """ clear the `values` list for pvname, pvname is added to the cache list """
  add_pv_to_cache(pvname)
  g_pv_chache_list[pvname].monitor_clear()

def monitor_get(pvname):
  """ returns statistics for pvname, pvname is added to the cache list """
  add_pv_to_cache(pvname)
  return g_pv_chache_list[pvname].monitor_get()

def monitor_stop_all(clear=False):
  """ stop monitoring for all PVs defined in cache list """
  for pv in g_pv_chache_list:
    g_pv_chache_list[pv].monitor_stop()
    if (clear): g_pv_chache_list[pv].monitor_clear()
    logprint("stopping monitoring for %s" % pv)

def get(pvname,as_string=False):
  """ returns current value for the pvname, if as_string is True values
      are converted to string """
  add_pv_to_cache(pvname)
  v = g_pv_chache_list[pvname].get()
  if (as_string):
    return str(v)
  else:
    return v

def put(pvname,value):
  """ write value to pvname; returns the value itself """
  add_pv_to_cache(pvname)
  g_pv_chache_list[pvname].put(value)
  return value

def wait_until_change(pvname,timeout=60):
  """ wait until value of pvname changes (default timeout is 60 sec), check 
      every 10ms, could be improved with semaphore ..."""
  monitor_start(pvname)
  t0=time.time()
  print len(g_pv_chache_list[pvname].values)
  while ( (time.time()-t0) < timeout):
    time.sleep(0.01)
    if ( len(g_pv_chache_list[pvname].values) > 1): break
  monitor_stop(pvname)
  monitor_clear(pvname)
  return
  

def monitor_until_value(pvname,value,timeout=60):
  """ wait until pvname is exactly value (default timeout is 60 sec) """
  t0 =time.time()
  add_pv_to_cache(pvname)
  pvvalue=get(pvname)
  if (pvvalue==value): return
  monitor_start(pvname)
  try:
    while ( (time.time()-t0) < timeout):
      time.sleep(0.010)
      if (len(g_pv_chache_list[pvname].values)!=0):
        if (g_pv_chache_list[pvname].values[-1]==value): break
    if ((time.time()-t0) > timeout):
      print "waiting for pv %s to become %s timedout" % (pvname,value)
  finally:
    monitor_stop(pvname)
    monitor_clear(pvname)
  return

def clear():
  """ stop monitoring and disconnect PV, to use as kind of reset """
  for pv in g_pv_chache_list:
    monitor_stop(pv)
    monitor_clear(pv)
    g_pv_chache_list[pv].disconnect()
  g_pv_chache_list.clear()

def what_is_monitored():
  """ print list of PVs that are currently monitored """
  for pv in g_pv_chache_list:
    if (g_pv_chache_list[pv].ismonitored):
      print "pv %s is currently monitored" % g_pv_chache_list[pv].name
