#!/bin/env python
# Author: Zhou Xing                                               
# Email: zxing@slac.stanford.edu                     
#
# This script will scan the targer sample along X-direction with a specified number of steps with some certain step size
# At each step, short pulse laser will be fired once with a FEL X-ray probe.
#
# Any change to this script should be sent to MEC staff member: Z. Xing, B. Nagler, E. Galtier              


import sys
from numpy import *
import os
import getopt
import time
import traceback
from cafunctions import caget, caput
from laser_princeton import Laser1

import mecload
from common.motor import Motor as psmotor
from common.pv2motor import PV2Motor as pv2motor
from mecbeamline  import shutter1, shutter2, shutter3, shutter4, att # for mec
#from mecfunctions import beam2mec, beam2cxi
from mecfunctions import lights_on, lights_off
from experiments.LG06.lg06 import delay, mecmotors



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



class LaserInteractive:
  def __init__(self):
    return

  def run(self, iNumPreDark, iNumPostDark, iNumPreX, iNumPostX, iNumPreO, iNumPostO, iNumDuring, fBurstRate, bSimMode, bShutterMode, bNoPI, fExpDelay, fPostDelay, iOpenDelay, bNoShutter12, bNoXCheck, iDebug, bInteracvive, bBeamShare, fGasDetector, fAttPreX , fAttDuring, iPreLaserTrig, fLeftRight):
    
    laser1 = Laser1(iNumPreDark, iNumPostDark, iNumPreX, iNumPostX, iNumPreO, iNumPostO, iNumDuring, fBurstRate, bSimMode, bShutterMode, bNoPI, fExpDelay, fPostDelay, iOpenDelay, bNoXCheck, iDebug, bBeamShare, fGasDetector, fAttPreX , fAttDuring, iPreLaserTrig)


    x0 = x_motor.wm()
    y0 = y_motor.wm()
    #x0           = float( caget("MEC:NOTE:DOUBLE:61") )
    #y0           = float( caget("MEC:NOTE:DOUBLE:62") )
    xstepsize    = float( caget("MEC:NOTE:DOUBLE:68") )
    steps        = int( caget("MEC:NOTE:DOUBLE:69") )
    xend = x0 + fLeftRight*xstepsize*steps
    print "\nInitial position of target is set to: x0 = %s mm, y0 = %s mm" % (x0, y0)
    print "Scan on x-direction to: xend = %s mm" % xend
    print "with %s steps at step size = %s mm" % (steps, xstepsize )

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


    iFail = laser1.init(bDaqBegin = False)
    if iFail != 0:
      return 1

    print shutter1.status()
    print shutter2.status()
    print shutter3.status()
    print shutter4.status()

    if not bNoShutter12 and (shutter1.isopen() or shutter2.isopen() or shutter3.isopen() or shutter4.isopen()):
      print "!!! Shutter 1 , 2 , 3 or 4 is still open, try to close it again for 2 seconds"
      #shutter1.close()
      shutter2.close()
      shutter3.close()
      shutter4.close()
      time.sleep(2)
      if shutter2.isopen() or shutter3.isopen() or shutter4.isopen():      
        print "!!! Shutter 1, 2 , 3 or 4 is still open"
        return 2

    try:
      shots_per_motorposition=1
      number_of_motorpositions=steps+1
      
      for n in range(0,number_of_motorpositions):

        if n==0:
          print "\nImage #%s at (x0 = %s mm,y0 = %s mm)\n" % (n, x0, y0)
        else:
          x_motor.mv(x0+fLeftRight*n*xstepsize)
          x_motor.wait()
          token_x = x0+fLeftRight*n*xstepsize
          print "\nImage #%s at (x = %s mm,y = %s mm)\n" % (n, token_x , token_y)
          
        #delay(1e-12)
        laser1.nextCycle()
        laser1.runMoreRounds(shots_per_motorposition) #this lines runs the DAQ 

      daq = laser1.daq
      print "# (If Record Run is ON) Experiment %d Run %d (%d Rounds)" % (daq.experiment(),daq.runnumber(), laser1.numTotalRounds())

      print('--Press <Enter> to exit--'),
      sMoreRun = raw_input(">")

      laser1.deinit()
      time.sleep(0.5)
    except:
      traceback.print_exc(file=sys.stdout)
      laser1.deinit()
      time.sleep(0.5)

    return 0

def showUsage():
  sFnCmd = os.path.basename( sys.argv[0] )
  print(
    "Usage: %s [-h | --help] [--predark <num>] [--prex <num>] [--preo <num>] [--during <num>]\n"
    "    [--postx <num>] [--posto <num>] [--postdark <num>] [--nofel] [--nopi] [-r|--rate <LaserRate>]\n"
    "    [-s|--shutter] [--sim] [-n | --nonintact]" % sFnCmd )
  print( "    -h | --help                   Show usage information" )
  print( "         --predark  <NumData>     Record <NumData> dark shots (No X-ray, no optical) before the during shot. Default: 0" )
  print( "         --prex     <NumData>     Record <NumData> X-ray only shots (no optical laser) before the during shot. Default: 0" )
  print( "         --preo     <NumData>     Record <NumData> optical laser only shots (no X-ray) before the during shot. Default: 0" )
  print( "         --during   <NumData>     Record 1 during image that integrates <NumData> (optical+x-ray laser) shots. Default: 1" )
  print( "         --posto    <NumData>     Record <NumData> optical laser only shots (no X-ray) after the during shot. Default: 0" )
  print( "         --postx    <NumData>     Record <NumData> X-ray only shots (no optical laser) after the during shot. Default: 0" )
  print( "         --postdark <NumData>     Record <NumData> dark shots (No X-ray, no optical) after the during shot. Default: 0" )
  print( "         --nopi                   Run without PI or FLI camera" )
  print( "    -r | --rate     <LaserRate>   Run with Optical Laser rate <LaserRate>. Default: 10" )
  print( "    -s | --shutter                Run in shutter mode. No Mcc Burst is called.")
  print( "    -e | --expdelay <Delay>       Add extra <Delay> seconds to exposure time. Default: 0" )
  print( "    -p | --post     <PostDelay>   Add extra <Delay> seconds to post-delay time. Default: 0" )
  print( "    -o | --opendelay <Tick>       Set camera open delay to <Tick>/120 seconds. Default: 5")
  print( "    -d | --debug                  Show debug messages" )
  print( "         --nonintact              Noninteractive mode" )
  print( "         --sim                    Run in simulation mode: No Mcc burst, and no shutter" )
  print( "         --noshutter              Run without closing shutter 1 2 3 and 4" )
  print( "         --beamshare              Run with beam2mec/cxi functions" )
  print( "         --noxcheck               Don't check for FEL rate drop" )
  print( "         --gasdetector <mJ>       Check if gas detector pulse energy larger than <mJ>. Default: 0.05" )
  print( "         --attbeforeprex <T>      Set transmission before preX shot. Default: -1.0 (Not moving any attenuators)" )
  print( "         --attbeforeduring <T>    Set transmission before during shot. Default: -1.0 (Not moving any attenuators)" )
  print( "         --prelasertrig <N>       Sending a prelaser trigger which is  N x 8 ms earlier. Default: -1 meaning no prelaser trigger will be sent out" )
  print( "         --leftright              Define the direction(1.0/-1.0) of movement on X. Default = 1.0")
  print( " ver 1.3")

def main():
  (llsOptions, lsRemainder) = getopt.getopt(sys.argv[1:], \
      'vhr:e:p:dno:s', \
      ['version', 'help', 'predark=', 'postdark=', 'prex=', 'postx=', 'preo=', 'posto=', 'during=', 'rate=', \
       'expdelay=', 'post=', 'opendelay=', 'nopi', 'debug', 'nonintact', 'sim', 'shutter', 'noshutter', 'beamshare', 'noxcheck', \
       'gasdetector=', 'attbeforeprex=', 'attbeforeduring=', 'prelasertrig=', 'leftright=' ] )

  iNumPreDark     = 0
  iNumPostDark    = 0
  iNumPreX        = 0
  iNumPostX       = 0
  iNumPreO        = 0
  iNumPostO       = 0
  iNumDuring      = 1
  fBurstRate      = 10
  fExpDelay       = 0
  fPostDelay      = 0
  iOpenDelay      = 5
  iDebug          = 0
  bInteracvive    = True
  bSimMode        = False
  bShutterMode    = False
  bNoPI           = False
  bNoShutter12    = False
  bBeamShare      = False
  bNoXCheck       = False
  fGasDetector    = 0.05
  fAttPreX        = -1.0
  fAttDuring      = -1.0
  iPreLaserTrig   = -1
  fLeftRight      = 1.0
  
  for (sOpt, sArg) in llsOptions:
    if sOpt in ('-v', '-h', '--version', '--help' ):
      showUsage()
      return 1
    elif sOpt in ('--predark'):
      iNumPreDark   = int(sArg)
    elif sOpt in ('--postdark'):
      iNumPostDark  = int(sArg)
    elif sOpt in ('--prex'):
      iNumPreX      = int(sArg)
    elif sOpt in ('--postx'):
      iNumPostX     = int(sArg)
    elif sOpt in ('--preo'):
      iNumPreO      = int(sArg)
    elif sOpt in ('--posto'):
      iNumPostO     = int(sArg)
    elif sOpt in ('--during'):
      iNumDuring    = int(sArg)
    elif sOpt in ('--nopi'):
      bNoPI       = True
    elif sOpt in ('-r', '--rate'):
      fBurstRate      = float(sArg)
    elif sOpt in ('-e', '--expdelay'):
      fExpDelay  = float(sArg)
    elif sOpt in ('-p', '--post'):
      fPostDelay = float(sArg)
    elif sOpt in ('-o', '--opendelay'):
      iOpenDelay = int(sArg)
    elif sOpt in ('-d', '--debug'):
      iDebug = 1
    elif sOpt in ('--nonintact'):
      bInteracvive = True
    elif sOpt == '-s' or sOpt == '--shutter':
      bShutterMode = True
    elif sOpt == '--sim':
      bSimMode     = True
    elif sOpt == '--noshutter':
      bNoShutter12 = True
    elif sOpt == '--beamshare':
      bBeamShare   = True
    elif sOpt == '--noxcheck':
      bNoXCheck    = True
    elif sOpt == '--gasdetector':
      fGasDetector = float(sArg)
    elif sOpt == '--attbeforeprex':
      fAttPreX     = float(sArg)
    elif sOpt == '--attbeforeduring':
      fAttDuring   = float(sArg)
    elif sOpt == '--prelasertrig':
      iPreLaserTrig = int(sArg)
    elif sOpt == '--leftright':
      fLeftRight     = float(sArg)  

  if not bNoShutter12:
    #shutter1.close()
    shutter2.close()
    shutter3.close()
    shutter4.close()
    lights_off()

  
  print "Command line: Predark %d Postdark %d PreX %d PostX %d PreO %d PostO %d During %d" % \
    (iNumPreDark, iNumPostDark, iNumPreX, iNumPostX, iNumPreO, iNumPostO, iNumDuring)
  print "  Rate %g  SimMode %s Shutter %s NoPI %s ExpDelay %g PostDelay %g OpenDelay %d" % \
    (fBurstRate, bSimMode, bShutterMode, bNoPI, fExpDelay, fPostDelay, iOpenDelay)
  print "  NoShutter12 %s NoXCheck %s Debug %d Interactive %s BeamShare %s GasDetector %s" % \
    (bNoShutter12, bNoXCheck, iDebug, bInteracvive, bBeamShare, fGasDetector)
  print "  AttBeforePreX %s AttBeforeDuring %s PreLaserTrig %s LeftRight %s" % \
    (fAttPreX, fAttDuring, iPreLaserTrig, fLeftRight)
 
  try:
    LaserInteractive().run(iNumPreDark, iNumPostDark, iNumPreX, iNumPostX, iNumPreO, iNumPostO, iNumDuring, fBurstRate, bSimMode, bShutterMode, bNoPI, fExpDelay, fPostDelay, iOpenDelay, bNoShutter12, bNoXCheck, iDebug, bInteracvive, bBeamShare, fGasDetector, fAttPreX , fAttDuring, iPreLaserTrig, fLeftRight)
  except:
    traceback.print_exc(file=sys.stdout)

  if not bNoShutter12:
    #shutter1.open()
    shutter2.open()
    shutter3.open()
    shutter4.open()
    lights_on()
  

  return

if __name__ == '__main__':
  status = main()
  sys.exit(status)
