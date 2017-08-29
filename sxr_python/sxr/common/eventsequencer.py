import pypsepics
from numpy import floor_divide
from time  import sleep
class EventSequencer:
  def __init__(self,local_iocbase="SXR:ECS:IOC:01:",sequence_group=4):
    #self.iocbase = "IOC:IN20:EV01:ECS" 
    self.iocbase = "ECS:SYS0:%d" % (sequence_group)
    self.local_iocbase = local_iocbase
    self.sequence_group = sequence_group
    self.__mode = ["Once","Repeat N Times","Repeat Forever"]
    self.__status = ["Stopped","Waiting","Playing"]
    self.__beamrate="EVNT:SYS0:1:LCLSBEAMRATE"
    self.define_pvnames()
    self.dictRateToSyncMarker = {0.5:0, 1:1, 5:2, 10:3, 30:4, 60:5, 120:6, 360:7, 0:6}
    self.setSyncMarker(self.beamrate())
    pypsepics.put(self.__pv_beamrequest,0) # TimeSlot

    self.maxEventCount = 2048
    self.__ec = [0] * self.maxEventCount
    self.__bd = [0] * self.maxEventCount
    self.__fd = [0] * self.maxEventCount
    self.__bc = [0] * self.maxEventCount

  def define_pvnames(self):
    ioc = self.iocbase
    self.__pv_beam_owner     = "ECS:SYS0:0:BEAM_OWNER_ID"
    self.__pv_testburst_dep  = "PATT:SYS0:1:TESTBURST.N"
    self.__pv_testburst_rate = "PATT:SYS0:1:TESTBURSTRATE"
    self.__pv_nsteps         = "%s:LEN"          % (ioc)
    self.__pv_playmode       = "%s:PLYMOD"       % (ioc)
    self.__pv_playcount      = "%s:PLYCNT"       % (ioc)
    self.__pv_playcontrol    = "%s:PLYCTL"       % (ioc)
    self.__pv_playstatus     = "%s:PLSTAT"       % (ioc)
    self.__pv_nrepeats_to_do = "%s:REPCNT"       % (ioc)
    self.__pv_total_count    = "%s:TPLCNT"       % (ioc)
    self.__pv_notify         = "%s:SEQ.PROC"     % (ioc)    
    self.__pv_syncmarker     = "%s:SYNCMARKER"   % (ioc) # 0:0.5 1:1 2:5 3:10 4:30 5:60 6:120 7:360
    self.__pv_beamrequest    = "%s:BEAMPULSEREQ" % (ioc) # 0: TimeSlot 1: Beam
    self.__pv_hutch_id       = "%s:HUTCH_ID"     % (ioc)
    self.__pv_EC_array       = "%s:SEQ.A"        % (ioc) # Event Codes
    self.__pv_BD_array       = "%s:SEQ.B"        % (ioc) # Beam Delays
    self.__pv_FD_array       = "%s:SEQ.C"        % (ioc) # Fiducial Delays
    self.__pv_BC_array       = "%s:SEQ.D"        % (ioc) # Burst Counts. -1: forever, -2: stop

  def beamrate(self):
    while True:
      rate = pypsepics.get(self.__beamrate)
      if rate == 0.5 or int(rate) == rate:
        break
      sleep(0.1)      
    return float(rate)

  def is_beam_owner(self):
    return pypsepics.get(self.__pv_beam_owner) == pypsepics.get(self.__pv_hutch_id)

  def set_testburst_rate(self,rate):
    dictRateToEnum = {0.5:5, 1:4, 5:3, 10:2, 30:1, 120:0, 0:0}
    if not (rate in dictRateToEnum):
      print "!! Rate should be one of:",
      print dictRateToEnum.keys()
    else:
      pypsepics.put(self.__pv_testburst_dep , 0)
      pypsepics.put(self.__pv_testburst_rate, dictRateToEnum[rate])

  def setSyncMarker(self,rate):
    pypsepics.put(self.__pv_syncmarker, self.dictRateToSyncMarker[rate])     

  def getSyncMarker(self):
    val = pypsepics.get(self.__pv_syncmarker)
    return self.dictRateToSyncMarker.keys()[self.dictRateToSyncMarker.values().index(val)]

  def setnsteps(self,nsteps):
    pypsepics.put(self.__pv_nsteps,nsteps)  

  def getnsteps(self):
    return pypsepics.get(self.__pv_nsteps)  

  def __beamcode_at_step(self,stepn,eventcode):
    #pvname = "%s:EC_%d:%02d" % (self.local_iocbase,self.sequence_group,stepn)
    #pypsepics.put(pvname,int(eventcode))

    self.__ec[stepn] = eventcode


  def __deltabeam_at_step(self,stepn,delta):
    #pvname = "%s:BD_%d:%02d" % (self.local_iocbase,self.sequence_group,stepn)
    #pypsepics.put(pvname,int(delta))

    self.__bd[stepn] = delta


  def __comment_at_step(self,stepn,comment):
    # Example: SXR:ECS:IOC:01:EC_4:00.DESC
    pvname = "%s:EC_%d:%02d.DESC" % (self.local_iocbase,self.sequence_group,stepn)
    pypsepics.put(pvname,comment)

  def __deltafiducial_at_step(self,stepn,delta=0):
    #pvname = "%s:FD_%d:%02d" % (self.local_iocbase,self.sequence_group,stepn)
    #pypsepics.put(pvname,int(delta))

    self.__fd[stepn] = delta


  def __burst_at_step(self,stepn,delta=0):
    #pvname = "%s:BC_%d:%02d" % (self.local_iocbase,self.sequence_group,stepn)
    #pypsepics.put(pvname,int(delta))

    self.__bc[stepn] = delta

  def setstep(self, stepn, beamcode, deltabeam, fiducial=0, burst=0, comment=""):
    print "Setting step #%d to beamcode %d, beam delay %d, fid %d, burst %d" % (stepn,beamcode,deltabeam,fiducial,burst)
    self.__beamcode_at_step     (stepn,beamcode)
    self.__deltabeam_at_step    (stepn,deltabeam)
    self.__deltafiducial_at_step(stepn,fiducial)
    self.__burst_at_step        (stepn,burst)
    if comment != "":
      self.__comment_at_step(stepn,comment)

  def modeOnce(self):
    self.__setmode("Once")

  def modeNtimes(self,N=1):
    self.__setmode("Repeat N Times",N)

  def modeForever(self):
    self.__setmode("Repeat Forever")

  def __setmode(self,mode,Ntimes=1):
    pvname=self.__pv_playmode
    if (mode == "Once"):
      pypsepics.put(pvname,0)
    elif (mode == "Repeat N Times"):
      pypsepics.put(pvname,1)
      pypsepics.put(self.__pv_nrepeats_to_do,Ntimes)
    elif (mode == "Repeat Forever"):
      pypsepics.put(pvname,2)
    else:
      print "mode must be Once|Repeat N Tiems|Repeat Forever"
      return
    self.update()

  def __getnpulses_in_play(self):
    return pypsepics.get(self.__pv_playcount)

  def __getnrepeats_to_do(self):
    return pypsepics.get(self.__pv_nrepeats_to_do)

  def getmode(self):
    pvname=self.__pv_playmode
    ret=pypsepics.get(pvname)
    return self.__mode[ret]

  def start(self):
    self.__total_count = pypsepics.get(self.__pv_total_count)
    pypsepics.put(self.__pv_playcontrol,1)

  def stop(self):
    pypsepics.put(self.__pv_playcontrol,0)

  def status(self,verbose=True):
    ret=pypsepics.get(self.__pv_playstatus)
    ret = self.__status[ret]
    if (verbose):
      print "Mode: %s" % self.getmode()
      print "Current status: %s" % ret
    else:
      return ret

  def wait(self,verbose=False):
    ntodo  = self.__getnrepeats_to_do()
    mode = self.getmode()
    if (mode  == "Repeat N Times"):
      while ( (pypsepics.get(self.__pv_playstatus) != 0) or (pypsepics.get(self.__pv_total_count) < ntodo) ):
        n = self.__getnpulses_in_play()
        if (verbose):
          print "running (%d of %d) ...\r" % (n,ntodo)
        sleep(0.01)
      n = self.__getnpulses_in_play()
      if (verbose): print "done (%d) ...\r" % n
      return
    elif (mode == "Once"):
      while ( (pypsepics.get(self.__pv_playstatus) != 0) or (pypsepics.get(self.__pv_total_count) != self.__total_count+1) ):
        if (verbose):
          print "running (%d) ...\r" % (ntodo)
        sleep(0.01)
      if (verbose): print "done (%d) ...\r" % n
      return


  def update(self):
    # notify the machine EVG of the changes
    pypsepics.put(self.__pv_EC_array, tuple(map(int,self.__ec)))
    pypsepics.put(self.__pv_BD_array, tuple(map(int,self.__bd)))
    pypsepics.put(self.__pv_FD_array, tuple(map(int,self.__fd)))
    pypsepics.put(self.__pv_BC_array, tuple(map(int,self.__bc)))

    #nstep = int( pypsepics.get(self.__pv_nsteps) )    
    #ec = pypsepics.get(self.__pv_EC_array)
    #bd = pypsepics.get(self.__pv_BD_array)
    #fd = pypsepics.get(self.__pv_FD_array)
    #print "Seq [%d]:" % nstep
    #print "EC: ",
    #print ", ".join(map(str,ec[0:nstep]))
    #print ", ".join(map(str,self.__ec[0:nstep]))
    #print "BD: ",
    #print ", ".join(map(str,bd[0:nstep]))
    #print ", ".join(map(str,self.__bd[0:nstep]))
    #print "FD: ",
    #print ", ".join(map(str,fd[0:nstep]))
    #print ", ".join(map(str,self.__fd[0:nstep]))

    pypsepics.put(self.__pv_notify,1)

