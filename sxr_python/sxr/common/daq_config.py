import pycdb
import pydaq
import os

def getTypeID(mne="Opal1kConfig"):
  a=os.popen("cat /reg/g/pcds/package/ana/release/pdsdata/xtc/TypeId.hh | sed -n '/enum Type/,/NumberOf};/p'")
  lines=a.readlines()
  a.close()
  idx = -1
  for i in range(len(lines)):
    if (lines[i].find( "Id_%s" % mne ) > 0 ):
      idx = i-1
      break
  if (idx == -1):
    return None
  else:
    return hex(idx) 

class DaqConfig(object):
  def __init__(self,dbpath="/reg/g/pcds/dist/pds/sxr/configdb/current"):
    self.dbpath = dbpath
    self.db = None

  def create(self):
    self.db = pycdb.Db(self.dbpath)

  def unlock(self):
    if self.db is not None:
      self.db.unlock()
      self.db = None
   

  def __getPrincetonCfg(self,alias="PRINCETON_BURST"):
    typeid=0x50012 # PrincetonConfig, V5    
    self.db.sync()
    xtclist=self.db.get(alias=alias,typeid=typeid)
#   xtclist=self.db.get(alias=alias,typeid=getTypeID("PrincetonConfig"))
    return xtclist

  def getPrinceton(self,alias="PRINCETON_BURST"):
    ret = []
    for f in self.__getPrincetonCfg(alias):
      ret.append( f.get() )
    return ret

  def getPrincetonExpTime(self,alias="PRINCETON_BURST",detn=0):
    cfgs = self.__getPrincetonCfg()
    if (detn+1 > len(cfgs) ):
      raise "Asked to change Princeton n %d but only %d Princeton(s) are defined" % (detn,len(cfgs))
    cfg = cfgs[detn]
    cfg_pars = cfg.get()
    return cfg_pars["exposureTime"]


  def setPrincetonConfig(self,exptime,nshots, config, alias="PRINCETON_BURST", detn=0, commit=True):
    cfgs = self.__getPrincetonCfg()
    if (detn+1 > len(cfgs) ):
      raise "Asked to change Princeton n %d but only %d Princeton(s) are defined" % (detn,len(cfgs))
    cfg = cfgs[detn]
    cfg_pars = cfg.get()

    if int(cfg_pars["kineticHeight"]) > 0:
      cfg_pars["numDelayShots"] = cfg_pars["height"] / cfg_pars["kineticHeight"]
      config.bKinetics = True
      config.nshots = int(cfg_pars["numDelayShots"])
      
      fOrgExposureTime = float(cfg_pars["exposureTime"])
      if config.beamRate * fOrgExposureTime >= 1:
        print "!!!Warning!!! Kinetics mode: Princeton %d exposure time %f slower than beam rate %f. Will set to 0.001 second" \
         % (detn, fOrgExposureTime, config.beamRate)
        cfg_pars["exposureTime"] = 0.001
    else:
      config.bKinetics = False
      cfg_pars["exposureTime"] = exptime
      cfg_pars["numDelayShots"] = nshots
    print "setting expousure time to %.3f second" % (float(cfg_pars["exposureTime"]))

    cfg.set(cfg_pars)
##    self.db.set(alias=alias,xtc=cfg)
    key = self.db.clone(alias)
    self.db.substitute(key,cfg)

    if (commit):
      self.db.commit()

    return key
