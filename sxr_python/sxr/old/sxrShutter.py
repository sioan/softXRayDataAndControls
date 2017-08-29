from common import pypsepics
import time
from sxrbeamline import pp, sxrevent

print "Loading sxr shutter v1.11 ... ",

SHUTTER_PV_PRE       = "SXR:SB2:MMS:09:"

SHUTTER_PV_SE_L      = SHUTTER_PV_PRE + "SE_L" # mode status
SHUTTER_PV_SE        = SHUTTER_PV_PRE + "SE" # mode status
SHUTTER_PV_SPOS_OPEN = SHUTTER_PV_PRE + "S_POS_OPEN" # last encoder position
SHUTTER_PV_SPOS_CLOSE= SHUTTER_PV_PRE + "S_POS_CLOSE" # last encoder position
SHUTTER_PV_SET_TG    = SHUTTER_PV_PRE + "SET_TG" 
SHUTTER_PV_M_ONESHOT = SHUTTER_PV_PRE + "RUN_ONESHOT"
SHUTTER_PV_M_FLIPFLOP= SHUTTER_PV_PRE + "RUN_FLIPFLOP"
SHUTTER_PV_M_BURST   = SHUTTER_PV_PRE + "RUN_BURSTMODE"
SHUTTER_PV_STATUS    = SHUTTER_PV_PRE + "SD_L"
SHUTTER_PV_SLIT_STAT = SHUTTER_PV_PRE + "DF"
SHUTTER_PV_RESET_PG  = SHUTTER_PV_PRE + "RESET_PG" # reset program

class Shutter:
  iNumMaxTry          = 50
  fTimeTry            = 0.2  
  lSlitOpen           = []
  numImage            = 0

def ShutterWaitUntilMode( iModeTarget ):
  iTry = 0
  while iTry < Shutter.iNumMaxTry:
    #print "Get SE_L = %d (try %d)" % (pypsepics.get(SHUTTER_PV_SE_L), iTry)
    if pypsepics.get(SHUTTER_PV_SE_L) == iModeTarget:
      return 0
    time.sleep(Shutter.fTimeTry)  
    iTry += 1
  return 1
  
def ShutterEvrInit(nshots):
  pp.setevrmode( nshots )
  return 0

def ShutterInit(nshots):

  Shutter.lSlitOpen = []
  Shutter.numImage  = 0

  if ShutterModeReset() != 0:
    return 1 

  if ShutterEvrInit(nshots) != 0:
    return 2

  if nshots == 1:
    pypsepics.put(SHUTTER_PV_M_FLIPFLOP, 1)

    if ShutterWaitUntilMode(2) != 0:
      return 3
  else:
    pypsepics.put(SHUTTER_PV_M_BURST, 1)

    if ShutterWaitUntilMode(3) != 0:
      return 3

  #print "Shutter setup finished"
  #raw_input("Press Enter to continue...")
  
  return 0

def ShutterArm( nshots ):
  # print SD DF SXR:SB2:MMS:09:SD SXR:SB2:MMS:09:DF https://confluence.slac.stanford.edu/display/PCDS/Pulse+Picker+MCode+Pseudocode
  # to read DF, need to caput DF 1 , then caget 
  #time.sleep(0.15) # !!debug

  Shutter.numImage += 1

  #pypsepics.put( SHUTTER_PV_SLIT_STAT, 1)
  #slitStat = pypsepics.get( SHUTTER_PV_SLIT_STAT)
  #if slitStat == 0:
  #  Shutter.lSlitOpen += [Shutter.numImage]

  if len(Shutter.lSlitOpen) > 0:
    print Shutter.lSlitOpen,
	  
  if nshots == 1:
    pass
  else:
    pass
  return 0

def ShutterModeReset():
  pypsepics.put(SHUTTER_PV_RESET_PG, 1)

  if ShutterWaitUntilResetDone() != 0:    
    print "Reset failed"
    return 1

  return 0

def ShutterWaitUntilResetDone():
  iTry = 0
  while iTry < Shutter.iNumMaxTry:    
    if pypsepics.get(SHUTTER_PV_STATUS) == 0:
      return 0
    time.sleep(Shutter.fTimeTry)  
    iTry += 1
  return 1

def ShutterSetSeq(nshots, delay):
    if nshots == 1:
      sxrevent.setnsteps(2 + nshots)
    else:
      sxrevent.setnsteps(3 + nshots) # mode 3.3
    sxrevent.setstep(0,83,delay,0)
    sxrevent.setstep(1,84,0,0)
    if nshots == 1:
      #sxrevent.setstep(2,85,2,0)
      sxrevent.setstep(2,85,1,0)
    else:
      sxrevent.setstep(2,85,2,0)

    #if nshots == 2:
    #  for iEvent in range(3, nshots+2):
    #    sxrevent.setstep(iEvent,85,1,0)
    #elif nshots > 2:
    if nshots >= 2:
      for iEvent in range(3, nshots+3):
        if iEvent == nshots + 1:
          sxrevent.setstep(iEvent,84,0,0) # mode 3.3
        else:
          sxrevent.setstep(iEvent,85,1,0)
    sxrevent.modeOnce()

print "done"
