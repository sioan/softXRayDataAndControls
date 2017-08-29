#from sxrbeamline import *
from sxrbeamline import lcls_linac, sxrdaqconfig, sxrevent, sxrdaq
import pyca
from common.donemoving import donemoving
import sys
import time
import signal
from caget import caget
from math import fabs
from Pv import Pv
from common.smartMotor import SmartMotor
from common.virtualmotor import VirtualMotor
from common.scan import AScan, A2Scan, DScan, D2Scan
from common import pypsepics
from sxrShutter import ShutterInit, ShutterArm

print "Loading sxr princeton v1.12 ... ",

class Config: pass

overhead_delay = 0.0

class Global:
  nshotsPrev = 0
  iSignalInt = 0

def setup(nimages,nshots,config,calibcontrols=[]):
  try:
    pypsepics.put("SXR:VARS:DAQ:PI_SHOTS",nshots)
    pypsepics.put("SXR:VARS:DAQ:PI_FRAMES",nimages)
    pass
  except:
    print "Unable to write nshots/nimages to DAQ-datastream"
    pass

  bSim      = config.bSim
  bShutter  = config.bShutter
  burstRate = config.burstRate

  #Global.nshotsPrev = nshots
  beamRate = sxrevent.beamrate()
  if burstRate==0:    
    rate = beamRate
  else:
    rate = burstRate

  if bSim:
    alias = "PRINCETON_SIM"
  else:
    alias = "PRINCETON_BURST"
    if rate == beamRate:
      if sxrevent.is_beam_owner():
        lcls_linac.set_burst_rate(0) # Set to "Full" rate
      else:
        sxrevent.set_testburst_rate(0)
    elif rate < beamRate:
      if rate == 60:
        print "!!! burst rate %d is not supported by MCC" % (rate)
        return 1   
      if sxrevent.is_beam_owner():
        lcls_linac.set_burst_rate(rate)
      else:
        sxrevent.set_testburst_rate(rate)
    else:
      print "!!! burst rate %d is faster than beam rate %d" % (rate, beamRate)
      return 1   


  if rate == 0:
    print "!!! beam rate is 0. Cannot setup princeton camera."
    return 1   

  sxrevent.setSyncMarker(rate)

  # Exposure time =
  #     sleep between "real" princeton open and PlayCtrl changed to "Stopped" (0.5 second)
  #     + delay from setting BurstState and MCC begin to fire beam (0.5 second)
  #     + exposure Time ((nshots/rate) second)
  #     + single shot exposure tolerance (0.1 second)
  #   = 1 + (nshots/rate) + 0.1  second
  #fExposureTime = 0.5 + nshots/rate
  fExposureTime = 0.02 + nshots/float(rate)

  sxrdaq.connect()  
  config.beamRate = rate

  if sxrdaq.dbalias() != alias:
    print "!!! the current DAQ config type is %s" % (sxrdaq.dbalias())
    print "!!! please switch to %s to run this script" % (alias)
    sxrdaq.disconnect()
    return 2

  db = sxrdaqconfig.setPrincetonConfig(fExposureTime, nshots, config = config, alias = alias, detn=0 )
  if config.bKinetics:
    print "Kinetics mode: %d shots" % (config.nshots)
    nshots = config.nshots

  beamInterval = 120 / rate

  if bSim:

    if bShutter:
      if ShutterInit(nshots) != 0:
        print "Shutter Init Failed"
        return 2

    eventShutterOpen = 84 if bShutter else 0

    if nshots == 1:
      sxrevent.setnsteps(2 + nshots)
    else:
      sxrevent.setnsteps(3 + nshots) # mode 3.3

    if nshots == 1:
      if beamInterval < 2:
        sxrevent.setstep(0,83,0,0,0)
      else:
        sxrevent.setstep(0,83,beamInterval-2,0,0)
      sxrevent.setstep(1,eventShutterOpen,0,0,0)
      sxrevent.setstep(2,85,2,0,0)
    else:
      if beamInterval < 2:
        sxrevent.setstep(0,83,0,0,0)
      else:
        sxrevent.setstep(0,83,beamInterval-2,0,0)
      sxrevent.setstep(1,eventShutterOpen,0,0,0)
      sxrevent.setstep(2,85,2,0,0)

      for iEvent in range(3, nshots+3):
        if iEvent == nshots + 1:
          sxrevent.setstep(iEvent,eventShutterOpen,beamInterval-1,0,0) 
        elif iEvent == nshots + 2:
          sxrevent.setstep(iEvent,85,1,0,0)
        else:
          sxrevent.setstep(iEvent,85,beamInterval,0,0)
    # event:
    #   83: start princeton exposure
    #   84: open/close shutter trigger
    #   85: DAQ readout 

    # nshots == 1
    # seq:
    #      event code   beam delay   fiducial delay(360Hz)
    #      83           Interval     0
    #      84           0            0
    #      85           1            0

    # nshots == 2 (old motor, which doesn't need close trigger)
    # seq:
    #      event code   beam delay   fiducial delay(360Hz)
    #      83           Interval-1   0
    #      84           0            0
    #      85           2            0
    #      84           Interval-1   0
    #      85           1            0

    # nshots == 3 or more
    # seq:
    #      event code   beam delay   fiducial delay(360Hz)
    #      83           Interval-1   0
    #      84           0            0
    #      85           2            0
    #      85           Interval     0  
    #      84           Interval-1   0  
    #      85           1            0

    # nshots == 4 or more
    # seq:
    #      event code   beam delay   fiducial delay(360Hz)
    #      83           Interval-1   0
    #      84           0            0
    #      85           2            0
    #      85           Interval     0  
    #      85           Interval     0  
    #      84           Interval-1   0  
    #      85           1            0

  else:
    sxrevent.setnsteps(2)  
    sxrevent.setstep(0,83,beamInterval-1,0,nshots)
    sxrevent.setstep(1,85,(nshots-1)*beamInterval+1,0,0)
  
  sxrevent.update() 
  sxrevent.modeOnce()

  # Cycle time =
  #  Delay between setting pvPlayCtrl and princeton open (0.5 second) +
  #  fExposureTime +
  #  Princeton camera readout time (4.7 second for 2048x2048 @ 1M) +
  #  Tolerance (0.3 second) +
  #  Min (
  #        Network data transfer delay (Number of shots / 100) ,
  #        Max limit (20 seconds) )
  #   + manual delay (overhead_delay)
  #
  fNetworkDelay = nshots/100.0
  if fNetworkDelay > 20: fNetworkDelay = 20
  config.fCycleTime = 0.5 + fExposureTime + 5 + fNetworkDelay + overhead_delay
  if config.fCycleTime < 0: config.fCycleTime = 0

  config.fCycleTime_seconds = int(config.fCycleTime)
  config.fCycleTime_nanoseconds = int((config.fCycleTime - float(config.fCycleTime_seconds))*1.e9)
  
  sxrevent.getSyncMarker()
  print "Beam rate = %s HZ, Sync marker = %s HZ" % (beamRate, sxrevent.getSyncMarker())
  print "Starting to take %d images (each image has %d shots)" % ( nimages, nshots )

  if calibcontrols==[]:
    calibcontrols=[('nimages',nimages),('nshots',nshots)]
    pass
  #sxrdaq._Daq__daq.configure(key=db,controls=calibcontrols)
  sxrdaq.configure(key=db,controls=calibcontrols,events=0)
  sxrdaq.begin(events=0,controls=calibcontrols)
  #sxrdaq.begin(events=0)
  #time.sleep(0.5) # Overhead for DAQ (EVR config), fixed by Matt

  return 0

def getimage(nshots,config,controls=[],monitors=[]):
  eventStart = sxrdaq.eventnum()

  sxrevent.start()
  sxrevent.wait()  

  t0 = time.time()
  last_shots_recvd = -1
  while True:
    dtime = time.time()-t0
    shots_recvd = sxrdaq.eventnum() - eventStart
    if shots_recvd != last_shots_recvd:
      #print "DEBUG: received %d/%d shots after %fs" % (shots_recvd,nshots,dtime)
      #sys.stdout.flush()
      last_shots_recvd = shots_recvd
      pass
    if sxrdaq.eventnum() >= eventStart + nshots:
      break
    time.sleep(0.1)
  #print "DEBUG: received %d shots" % shots_recvd    

  if config.bShutter:
    if ShutterArm(nshots) != 0:
      print " Shutter Arm Failed",
      return 1

  return 0

def sigIntHandler(signal, frame):
  Global.iSignalInt += 1

def ccdtake(nshots = 1,nimages = 1, bShutter = False, burstRate=0, bSim = False):
   config = Config()
   config.bSim      = (bSim or bShutter)
   config.bShutter  = bShutter
   config.burstRate = burstRate

   if setup(nimages,nshots,config) != 0:
     print "setup failed"
     return 1

   Global.iSignalInt = 0
   signal.signal(signal.SIGINT, sigIntHandler)

   if config.bKinetics:           # added for kinetics
     nshots = config.nshots
     pass
   times=list()
   ntaken=0
   try:
     for i in range(nimages):
       t0 = time.time()
       print "getting image %d/%d ..." % (i+1,nimages),
       iFail = getimage(nshots,config)
       	   
       ntaken+=1
       times.append(time.time()-t0)
       print "... done %.1fs" % (times[-1])
       sys.stdout.flush()

       if iFail == 1 or Global.iSignalInt > 0:
         break
     pass
   finally:
     sxrdaq.stop()
     ttot=0.
     for t in times:
       ttot+=t
       pass
     if ntaken > 0:
       print "average image acquisition time: %.1fs" % (ttot/ntaken)
       pass
     else:
       print "no shots taken"
       pass
     pass
   pass

   #sxrdaq.disconnect() # don't disconnect to keep the last PI image on monitoring

   return 0

class ScanVars:
  def __init__(self, nshots, nimages, calibcontrols=[], bShutter = False, burstRate = 0, bSim = False):
    self.nimages = nimages
    self.nshots = nshots
    self.motors = []
    self.calibcontrols=calibcontrols
    self.step = 0

    self.config      = Config()
    config.bSim      = (bSim or bShutter)
    config.bShutter  = bShutter
    config.burstRate = burstRate

  def add_motor(self, m):
    self.motors.append(m)
    if isinstance(m,VirtualMotor):
      for mm in m.motors:
        self.motors.append(m)

  def get_controls(self):
    controls=[]
    for m in self.motors:
      controls.append((m.motor_name,m.get_position()))
    return controls
  
  def pre_scan(self, scan):
    try:
      print "Configuring Princeton..."
      setup(self.nimages, self.nshots, self.config, self.calibcontrols)
      if self.config.bKinetics:          # added for kinetics
        self.nshots = self.config.nshots
      sys.stdout.flush()
      
    except Exception, e:
      print "ERROR:\tUnable to configure Princeton, detailed error below."
      print e
      pass

  def post_scan(self, scan):
    sxrdaq.stop()

  def post_move(self, scan):
    position = "step: %5d \t position: " % self.step; self.step += 1
    for m in self.motors:
      position += "\t%10.4f" % (m.get_position())
      pass
    print position
    
    for i in range(self.nimages):
      print "\tGetting image %d of %d ..." % (i+1, self.nimages)
      sys.stdout.flush()
      controls=self.get_controls()
      getimage(self.nshots, self.config, controls=controls)
      pass
    pass
  pass

def __cast_motor(motor):
  if isinstance(motor,VirtualMotor):
    return motor
  else:
    return SmartMotor(motor.pvname)
  

def ascan(motor,pos1,pos2,nIntervals,nshots=1,nimages=1,returnAfter=True):
  retVal = 0
  print "Setting up scan..."
  try:
    calibcontrols=[('motor1_pos1',pos1),
                   ('motor1_pos2',pos2),
                   ('motor1_nIntervals',nIntervals),
                   ('nshots',nshots),
                   ('nimages',nimages)
                   ]
    scanVars = ScanVars(nshots, nimages, calibcontrols)
    #m = SmartMotor(motor.pvname)
    m = __cast_motor(motor)
    scanVars.add_motor(m)
    scan = AScan(m, pos1, pos2, nIntervals, returnAfter)
    scan.set_pre_scan_hook(scanVars.pre_scan)
    scan.set_post_scan_hook(scanVars.post_scan)
    scan.set_post_move_hook(scanVars.post_move)
    print "Starting scan..."
    scan.go()
    pass
  finally:
    pass
  pass

def dscan(motor,d1,d2,nIntervals,nshots=1,nimages=1,returnAfter=True):
  ascan(motor,motor.wm()+d1,motor.wm()+d2,nIntervals,nshots,nimages,returnAfter)
  pass


def a2scan(motor1,motor1_pos1,motor1_pos2,motor1_nIntervals,motor2,motor2_pos1,motor2_pos2,motor2_nIntervals,nshots=1,nimages=1,returnAfter=True):
  retVal = 0
  print "Setting up scan..."
  try:
    calibcontrols=[('motor1_pos1',motor1_pos1),
                   ('motor1_pos2',motor1_pos2),
                   ('motor1_nIntervals',motor1_nIntervals),
                   ('motor2_pos1',motor1_pos1),
                   ('motor2_pos2',motor2_pos2),
                   ('motor2_nIntervals',motor2_nIntervals),
                   ('nshots',nshots),
                   ('nimages',nimages)
                   ]
    scanVars = ScanVars(nshots, nimages, calibcontrols)
    #m1 = SmartMotor(motor1.pvname)
    m1 = __cast_motor(motor1)
    scanVars.add_motor(m1)
    #m2 = SmartMotor(motor2.pvname)
    m2 = __cast_motor(motor2)
    scanVars.add_motor(m2)
    scan = A2Scan(m1, motor1_pos1, motor1_pos2, motor1_nIntervals, m2, motor2_pos1, motor2_pos2, motor2_nIntervals, returnAfter)
    scan.set_pre_scan_hook(scanVars.pre_scan)
    scan.set_post_scan_hook(scanVars.post_scan)
    scan.set_post_move_hook(scanVars.post_move)
    print "Starting scan..."
    scan.go()
    pass
  finally:
    pass
  pass

def DaqSeqStart():
  sxrdaq.begin(0)
  sxrevent.start()

def DaqSeqStop():
  sxrevent.stop()
  sxrevent.wait()  
  sxrdaq.stop()
  sxrdaq.disconnect()

"""
def __movetime(dist,speed,accel=0,decel=0):
  return fabs(dist/speed) + accel + decel

def __checkLimits(motorname):
  lim_lo = caget(motorname + '.LLS')
  if (lim_lo == 1):
    return -1
  else:
    lim_hi = caget(motorname + '.HLS')
    if (lim_hi == 1):
      return 1
    else:
      return 0  
  

def ascan(motor,pos1,pos2,nIntervals,nshots=1,nimages=1,returnAfter=True):
  retVal = 0
  ti = time.time()
  daq_time = 0.
  epics_time = 0.
  mname = motor.pvname
  minpos = min(pos1,pos2)
  maxpos = max(pos1,pos2)
  moved = False

  try:
    motorpv = Pv(mname)
    motorpv.connect(1.0)

    egu = caget(mname + '.EGU')
    ulim_lo = caget(mname + '.LLM')
    ulim_hi = caget(mname + '.HLM')

    print "INFO:\tScanning '%s' from %f %s to %f %s in %u intervals" % (motor.name, pos1, egu, pos2, egu, nIntervals)

    if (minpos < ulim_lo):
      print "ERROR:\tLower edge of scan (%f%s) exceeds user low-limit (%f%s), please re-specify parameters" % (minpos, egu, ulim_lo, egu)
      retVal = 1
    if (maxpos > ulim_hi):
      print "ERROR:\tUpper edge of scan (%f%s) exceeds user high-limit (%f%s), please re-specify parameters" % (maxpos, egu, ulim_hi, egu)
      retVal = 1

    if (retVal != 0):
      return retVal

    config = Config()
    try:
      print "Configuring Princeton..."
      ti_daq = time.time()
      setup(nimages,nshots,config)
      delta_daq = time.time() - ti_daq
      daq_time += delta_daq
    except Exception, e:
      print "ERROR:\tUnable to configure Princeton, detailed error below."
      print e
      return 100

    print "Moving motor to scan start position..."
    sys.stdout.flush()
    
    pos = pos0 = caget(mname + '.RBV')
    velo  = caget(mname + '.VELO')
    accel = caget(mname + '.ACCL')
    decel = caget(mname + '.BACC')
    nextpos = pos1
    delta = float(pos2 - pos1) / nIntervals      
    
    dmovpv = donemoving(mname + '.DMOV')
    for step in range(0, nIntervals + 1):
      timeout = 10. + __movetime(pos-nextpos,velo,accel,decel)
      starttime = time.time()
      motorpv.put(nextpos)
      pyca.pend_io(.1)
      dmovpv.wait_for_done(timeout)
      moved=True
      delta_epics = time.time() - starttime
      pos = caget(mname + '.RBV')
      print '%3u\tpos %f %s\tdt %f s' %(step, pos, egu, delta_epics)
      epics_time += delta_epics
      ti_daq = time.time()
      for i in range(nimages):
        print "\tGetting image %d of %d ..." % (i+1,nimages),
        getimage(nshots,config)
        delta_daq = time.time() - ti_daq
        print "Acquisition time %f s" % (delta_daq)
        daq_time += delta_daq

        sys.stdout.flush()
        pass
      
      if (step <= nIntervals):
        lim_status = __checkLimits(mname)
        if (lim_status < 0):
          print "\nWARNING:\tLow limit switch tripped! Scan stopped after %u intervals." % (step)
          retVal = 2
          pass        
        elif (lim_status > 0):
          print "\nWARNING:\tHigh limit tripped! Scan stopped after %u intervals.%s" % (step)
          retVal = 2
          pass
        if (retVal != 0):
          return retVal    
      nextpos += delta
      pass
    pass
  except KeyboardInterrupt:
    print "INFO: Scan interrupted by user"
  except pyca.pyexc, e:
    print 'pyca exception: %s' %(e)
  except pyca.caexc, e:
    print 'channel access exception: %s' %(e)
  except Exception, e:
    print e
  finally:
    # return to original position
    if (returnAfter and moved):
      print "Returning to initial position (%f %s)" % (pos0, egu)
      ti_epics = time.time()
      timeout = 10. + __movetime(pos-pos0,velo,accel,decel)
      motorpv.put(pos0)
      pyca.pend_io(.1)
      dmovpv.wait_for_done(timeout)
      tf = time.time()
      delta_epics += tf - ti_epics
      epics_time += delta_epics
      print "Scan completed in %f s (daq: %f s\tepics: %f s)" % (tf-ti, daq_time, epics_time)
      pass
    return retVal
  

def dscan(motor,dxn,dxp,nIntervals,nshots=1,nimages=1,returnAfter=True):
  try:
    curpos = caget(motor.pvname+'.RBV')
    return ascan(motor,curpos+dxn,curpos+dxp,nIntervals,nshots,nimages,returnAfter)
  except pyca.pyexc, e:
    print 'pyca exception: %s' %(e)
  except pyca.caexc, e:
    print 'channel access exception: %s' %(e)
  except Exception, e:
    print e
"""

print "done"
