#from sxrbeamline import *
from sxrbeamline import lcls_linac, sxrdaqconfig, sxrevent, sxrdaq
import pyca
from donemoving import donemoving
import sys
import time
from caget import caget
from math import fabs
from Pv import Pv
from smartMotor import SmartMotor
from scan import AScan, A2Scan, DScan, D2Scan
import pypsepics

#mlist = [ sxrmotors.s1vo ]

#def CrtPV():
#  controls = []
#  for m in mlist:
#    controls.append( [m.name,m.wm() ] )

#class Config: pass

def setupburst(nshots):
  #print "setup"
  if not lcls_linac.isburstenabled():
    print "ERROR: Not in Burst mode!  Call MCC and turn it on..."
    

  lcls_linac.set_fburst("Full")


  lcls_linac.set_nburst(nshots)

  sxrdaq.connect()
  print "connected"

  alias = "BEAM"
#  print "getkey"
#  db = sxrdaqconfig.db.get_key(alias)
#  print "got key %s" % db

#  sxrdaq._Daq__daq.configure(key=db)
  sxrdaq._Daq__daq.configure(events=0)
  print "daq configured"
  
  sxrdaq.begin(events=0)
  print "daq started"
  time.sleep(0.5) # Overhead for DAQ (EVR config)
    
  pass

# depends on DAQ being configured and running.  If not, it will wait forever!
def getshots(nshots):
  eventStart = sxrdaq.eventnum() 
  #print "getshots %f" % time.time()
  lcls_linac.get_burst()

  try:
    lcls_linac.wait_burst(2.0)
    #lcls_linac.wait_for_shot()
  except Exception, e:
    print "WARNING: Did not see burst after 2 seconds, continuing anyway"
    sys.stdout.flush()

#  print "wait daq %f" % time.time()
#  while sxrdaq.eventnum() < eventStart + nshots:
#    time.sleep(0.1)
#    pass

  #print "done %f" % time.time()
  
  pass


class ScanVars:
  def __init__(self, nshots):
    #print "scanvars"
    self.nshots = nshots
    self.motors = []
    pass

  def add_motor(self, m):
    self.motors.append(m)
  
  def pre_scan(self, scan):
    try:
      #print "Configuring DAQ..."
      setupburst(self.nshots)
      sys.stdout.flush()
      
    except Exception, e:
      print "ERROR:\tUnable to configure DAQ, detailed error below."
      print e
      sys.stdout.flush()
      pass

  def post_scan(self, scan):
    sxrdaq.stop()
    pass

  def post_move(self, scan):
    position = "position: "
    for m in self.motors:
      position += "\t%10.4f" % (m.get_position())
      pass
    print position
    sys.stdout.flush()
      
    getshots(self.nshots)
  pass


def ascan(motor,pos1,pos2,nIntervals,nshots=1,returnAfter=True):
  retVal = 0
  print "Setting up scan..."
  try:
    scanVars = ScanVars(nshots)
    m = SmartMotor(motor.pvname)
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


def a2scan(motor1,motor1_pos1,motor1_pos2,motor1_nIntervals,motor2,motor2_pos1,motor2_pos2,motor2_nIntervals,nshots=1,returnAfter=True):
  retVal = 0
  print "Setting up scan..."
  try:
    scanVars = ScanVars(nshots)
    m1 = SmartMotor(motor1.pvname)
    scanVars.add_motor(m1)
    m2 = SmartMotor(motor2.pvname)
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

