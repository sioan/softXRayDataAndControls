#!/bin/env python
# Script to control DAQ and sample stage scan
# running with cspad, opal etc and slow device Princeton, each step of motor will have one shot recorded 
# Author: Zhou Xing
# Email: zxing@slac.stanford.edu

import sys
from numpy import *
import os
import getopt
import time
import traceback
from princeton import PrincetonDaqMultipleShot
from cafunctions import caget, caput
import mecload
from common.motor import Motor as psmotor
from common.pv2motor import PV2Motor as pv2motor
from mecbeamline  import shutter1, shutter3 # for mec


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

  def run(self, iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode, fLeftRight):
    princetonDaq = PrincetonDaqMultipleShot(iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode)
    
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





    iFail = princetonDaq.init(bDaqBegin = False)
    if iFail != 0:
      return 1

    try:
      shots_per_motorposition=1      
      number_of_motorpositions=steps+1


      # Scan on X loop starts here
      for n in range(0,number_of_motorpositions):

        if n==0:
          print "\nImage #%s at (x0 = %s mm,y0 = %s mm)\n" % (n, x0, y0)

        else:
          x_motor.mv(x0+fLeftRight*n*xstepsize)
          x_motor.wait()
          token_x = x0+fLeftRight*n*xstepsize
          print "\nImage #%s at (x = %s mm,y = %s mm)\n" % (n, token_x , token_y)
          
          
        
        princetonDaq.nextCycle()
        princetonDaq.getMoreImages(shots_per_motorposition)
      # Scan on X loops ends here


      daq = princetonDaq.daq
      print "# (If Record Run is ON) Experiment %d Run %d (%d images)" % (daq.experiment(),daq.runnumber(), princetonDaq.numTotalImage())

      print('--Press <Enter> to exit--'),
      sMoreRun = raw_input(">")

      princetonDaq.deinit()
      time.sleep(0.5)
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
  print( "    -m | --mshot     <NumShots>    Run multiple shot integration of <NumShots>. Default: 1" )
  print( "    -e | --expdelay  <Delay>       Set exposure time delay to <Delay> second. Default: 0" )
  print( "    -p | --post      <PostDelay>   Set post delay to <Delay> second. Default: 0" )
  print( "    -o | --opendelay <Tick>       Set camera open delay to <Tick>/120 seconds. Default: 5")
  print( "    -r | --rate      <Rate>        Set burst rate to <rate>. Default: use Beam Rate" )
  print( "    -s | --shutter                 Run in shutter mode. No Mcc Burst is called.")
  print( "         --sim                     Run in simulation mode: No Mcc burst, and no shutter.")
  print( "         --leftright               Define the direction(1.0/-1.0) of movement on X. Default = 1.0")
  print( " ver 1.9")

def main():
  (llsOptions, lsRemainder) = getopt.getopt(sys.argv[1:], \
      'hm:e:r:p:o:s', \
      ['help', 'mshot=', 'expdelay=', 'opendelay=', 'rate=', 'post=', 'shutter', 'sim', 'leftright='] )

  iNumShot   = 1
  fExpDelay  = 0
  fPostDelay = 0
  iOpenDelay = 5

  fBurstRate   = -1
  bSimMode     = False
  bShutterMode = False
  fLeftRight = 1.0
  
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
    elif sOpt == '--leftright':
      fLeftRight     = float(sArg)  


  print "Command line: NumShot %d ExpDelay %g PostDelay %g OpenDelay %d Rate %g SimMode %s Shutter %s LeftRight %s" % \
    (iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode, fLeftRight)
  try:
    PrincetonMultipleShotInteractive().run(iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode, fLeftRight)
  except:
    traceback.print_exc(file=sys.stdout)
  return

if __name__ == '__main__':
  status = main()
  sys.exit(status)
