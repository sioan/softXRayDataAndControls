#!/bin/env python
# Script to control DAQ and sample stage scan
# running at 120Hz with cspad, opal etc, with integrated shots for slow device Princeton 
# Author: Zhou Xing
# Email: zxing@slac.stanford.edu



# Import standard python modules
import sys
import os
import getopt
import time
import datetime
import traceback
from numpy import *


# Import the Princeton module
from princeton import PrincetonDaqMultipleShot


# Import EPICS and DAQ utilities modules
from cafunctions import caget, caput
import daqlog


# Import MEC python
import mecload
#from experiments.LC21.lc21  import *
from common.motor import Motor as psmotor
from common.pv2motor import PV2Motor as pv2motor
from mecbeamline  import shutter1, shutter2, shutter3, att # for mec
from mecfunctions import beam2mec, beam2cxi
from mecfunctions import lights_on, lights_off



# Customized motor definition

x_motor  = psmotor("MEC:USR:MMS:17",'tgx',home='low') # x-direction is psmotor
y_motor  = pv2motor("MEC:HEX:01:Ypr","MEC:HEX:01:Ypr:rbv","hexy") # y-direction is pv2motor



# wait function for hexpod motor only
def wait(motor):
  time.sleep(0.8)
  while(True):
    status = caget("MEC:HEX:01:moving")
    if status == "In Position":
      break
    time.sleep(0.02)



class PrincetonMultipleShotInteractive:
  ''' iNumShot : number of beam integrations for each PI image, set with -m when calling routine from command line
      shots_per_motorposition: number of PI images per motor position
  '''
  def __init__(self):
    pass

  def run(self, iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode, fUpDown):
    

    # parameterize the scan on X
    x0 = x_motor.wm() 
    y0 = y_motor.wm()
    #x0           = float( caget("MEC:NOTE:DOUBLE:61") )
    #y0           = float( caget("MEC:NOTE:DOUBLE:62") )
    predelay     = float( caget("MEC:NOTE:DOUBLE:63") )
    travel_range = float( caget("MEC:NOTE:DOUBLE:64") )
    postdelay    = float( caget("MEC:NOTE:DOUBLE:65") )
    ystepsize    = float( caget("MEC:NOTE:DOUBLE:66") )
    steps        = int( caget("MEC:NOTE:DOUBLE:67") )

    # running at 120 Hz or 60Hz etc ?
    daqrate = fBurstRate
    # default to beam rate
    if daqrate == -1:
      daqrate = float(caget("EVNT:SYS0:1:LCLSBEAMRATE"));
      

    motor_speed = float( caget("MEC:USR:MMS:17.VELO") )

    xend = x0 + predelay + travel_range + postdelay
    
    print "\nInitial position of target is set to: x0 = %s mm, y0 = %s mm" % (x0, y0)
    print "Scan on x-direction to: xend = %s mm with DAQ running at 120Hz " % xend
    print "with predelay = %s mm; postdelay = %s mm; travel range = %s mm" % (predelay, postdelay, travel_range)
    print "Scan on y-direction: %s steps with step size %s mm\n" % (steps, ystepsize)

    print "\nGiven the nominal speed of the motor, which is %s mm/s," % motor_speed
    Nevents    = int( (abs(travel_range)/motor_speed)*daqrate)
    predelayT  = predelay/motor_speed
    postdelayT = postdelay/motor_speed
    print "Number of events (shots) for a single row is computed to be: %s with DAQ running at %s Hz" % (Nevents,daqrate)
    print "When moving forward from x0 to xend:"
    print "Pre  delay: DAQ will record first event %s s after the motor started." % (predelayT)
    print "Post delay: DAQ will record last event more or less %s s before the motor stopped." % (postdelayT)

    print "When moving backword from xend to x0:"
    print "Post  delay: DAQ will record first event %s s after the motor started." % (postdelayT)
    print "Pre   delay: DAQ will record last event more or less %s s before the motor stopped." % (predelayT)
    
    
    # update token position
    token_x = x_motor.wm()
    token_y = y_motor.wm()
    timeBeforeInitialize = time.time()


    # Initialization
    if( abs(token_x-x0)>0.01 or abs(token_y-y0)>0.01 ):
      print '\nTarget is not currently at (x0 = %s mm, y0 = %s mm)! Will start initialization now!' % (x0,y0)
      print 'Target at : (x = %s mm, y = %s mm) before initialization' % (token_x,token_y)
      
      # move motor to the initial position 
      # start moving motor
      x_motor.mv(x0)
      y_motor.mv(y0)
      x_motor.wait()   
      wait(y_motor)    
          

      # update token position
      token_x = x_motor.wm()
      token_y = y_motor.wm()
      print 'Target at : (x = %s mm, y = %s mm) after initialization\n' % (token_x,token_y)
    
    else:
      print '\nTarget is in position at (x0 = %s, y0 = %s). Will start scan now.\n' % (x0,y0)
    
    timeAfterInitialize = time.time()


    #Pre-defined number of events (triggers) for Princeton device
    iNumShot = Nevents

    princetonDaq = PrincetonDaqMultipleShot(iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode)

    try:

      # Loops of scan on y-direction starts here
      timeBeforeScanonY = time.time()
      
      for iScan in xrange( steps ):
      
        print "Step #%s on Y starts now:" % (iScan+1)

        if iScan!=0:
          print "Moving target %s to the next row now." % ("Up" if fUpDown>0 else "Down")
          y_motor.mv(token_y+fUpDown*(1.0)*ystepsize)
          wait(y_motor)
          token_y = y_motor.wm()
          print "Target now at (x = %s mm, y = %s mm)" % (token_x, token_y)
      
        # define movement on x-direction now
        destination = (xend if (iScan%2 ==0) else x0 )
        delayT = (predelayT if (iScan%2 ==0) else postdelayT )

        # connect to DAQ
        iFail = princetonDaq.init(bDaqBegin = False)
        if iFail != 0:
          return 1    

        # calibration cycle ready
        princetonDaq.nextCycle()

        # Move motor right before start DAQ, no need to move during beginCycle()
        timeBeforeScanonX = time.time()

        # motor movement in sub-routine getMoreImage()
        princetonDaq.getMoreImages(1, x_motor, token_x, destination, delayT)
        
        timeAfterScanonX = time.time()
               

        daq = princetonDaq.daq
        print "# (If Record Run is ON) Experiment %d Run %d (%d images)" % (daq.experiment(),daq.runnumber(), princetonDaq.numTotalImage())

        princetonDaq.deinit()



        # check if motor has been moved to the end position xend #
        while(True):
          if not x_motor.ismoving():
            print "Motor reaches xend now!"
            break
          else:
            time.sleep(0.02)


        # updating token
        token_x = destination
        print "Scan on X ends at (x = %s mm, y = %s mm)" % (token_x, token_y)
        print "Time for this scan on X: %3.2f s\n" % (timeAfterScanonX-timeBeforeScanonX)
        

        time.sleep(0.5)

        # Loops of scan on y-direction ends here
        

      timeAfterScanonY = time.time()
      
      print "\nTime for the whole scan on both X and Y: %3.2f s" % (timeAfterScanonY-timeBeforeScanonY)
      print "Final position of the target is (x = %s mm, y = %s mm)" % (token_x, token_y)
        
        
    except:
      traceback.print_exc(file=sys.stdout)
      princetonDaq.deinit()
      time.sleep(0.5)
        
    return 0




def showUsage():
  sFnCmd = os.path.basename( sys.argv[0] )
  print(
    "Usage: %s [-h | --help] [-m|--mshot <NumShots>] [-e|--expdelay <Delay>] [-p|--post <postDealy>]\n"
    "    [-o|--opendelay <Tick>] [-r|--rate <rate>] [-s|--shutter]" % sFnCmd )
  print( "    -h | --help                   Show usage information" )
  print( "    -m | --mshot     <NumShots>   Run multiple shot integration of <NumShots>. Default: 1" )
  print( "    -e | --expdelay  <Delay>      Set exposure time delay to <Delay> second. Default: 0" )
  print( "    -p | --post      <PostDelay>  Set post delay to <Delay> second. Default: 0" )
  print( "    -o | --opendelay <Tick>       Set camera open delay to <Tick>/120 seconds. Default: 5")
  print( "    -r | --rate      <Rate>       Set burst rate to <rate>. Default: use Beam Rate" )
  print( "    -s | --shutter                Run in shutter mode. No Mcc Burst is called.")
  print( "         --sim                    Run in simulation mode: No Mcc burst, and no shutter.")
  print( "         --updown                 Define Up/Down (1/-1) for the scan on Y direction, default = 1 Up" )
  print( " ver beta")

def main():
  (llsOptions, lsRemainder) = getopt.getopt(sys.argv[1:], \
      'hm:e:r:p:o:s', \
      ['help', 'mshot=', 'expdelay=', 'opendelay=', 'rate=', 'post=', 'shutter', 'sim', 'updown='] )

  iNumShot   = 1
  fExpDelay  = 0
  fPostDelay = 0
  iOpenDelay = 5

  fBurstRate   = -1
  bSimMode     = False
  bShutterMode = False

  fUpDown = 1.0
  
  for (sOpt, sArg) in llsOptions:
    if sOpt in ('-h', '--help' ):
      showUsage()
      return 1
    elif sOpt in ('-m', '--mshot'):
      iNumShot   = int(sArg)
    elif sOpt in ('-e', '--expdelay'):
      fExpDelay  = float(sArg)
    elif sOpt in ('-p', '--post'):
      fPostDelay = float(sArg)
    elif sOpt in ('-o', '--opendelay'):
      iOpenDelay = int(sArg)
    elif sOpt in ('-r', '--rate'):
      fBurstRate   = float(sArg)
    elif sOpt == '-s' or sOpt == '--shutter':
      bShutterMode = True
    elif sOpt == '--sim':
      bSimMode     = True
    elif sOpt in ('--updown'):
      fUpDown = float(sArg)


  print "Command line: NumShot %d ExpDelay %g PostDelay %g OpenDelay %d Rate %g SimMode %s Shutter %s UpDown %s" % \
    (iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode, fUpDown)
  try:
    PrincetonMultipleShotInteractive().run(iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode, fUpDown)
  except:
    traceback.print_exc(file=sys.stdout)
  return

if __name__ == '__main__':
  status = main()
  sys.exit(status)
