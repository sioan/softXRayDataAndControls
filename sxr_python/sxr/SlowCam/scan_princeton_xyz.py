#!/bin/env python

import sys

from numpy import *
import os
import getopt
import time
import traceback


#from princeton import MccBurst, PrincetonDaqMultipleShot, DaqMultipleShotNonInteractive
import princeton 

import pyca
from Pv import Pv
import threading


# Special PV names
beamCount   = "SXR:R24:EVR:40:EVENT1CNT"
burstCount  = "SXR:R24:EVR:40:EVENT6CNT"
burstCtrl   = "PATT:SYS0:1:MPSBURSTCTRL"
feeGasSetPt = "VGPR:FEE1:311:PSETPOINT_DES"
gasAttRdbk  = "GATT:FEE1:310:R_ACT"
gasAttPres  = "GATT:FEE1:310:P_DES"

# globals
evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM

# trimmedLines - generator for de-commented file
def trimmedLines(filename):
  try:
    fd = open(filename)
  except:
    print 'Error: failed to open', filename
    error=1
  else:
    error=0

  if error:
    yield None
  else:
    for line in open(filename).xreadlines():
      trimmed = line.strip()
      if len(trimmed) > 0:
        if trimmed.startswith('#'):
          continue
        yield trimmed

#
# Calib - class for motor calibration
#
class Calib:
  def __init__(self, calibfile, pvnames, origin):
    self._file = calibfile
    self._pvnames = pvnames
    if origin == None:
      self._originX = 0
      self._originY = 0
    else:
      self._originX = origin[0]
      self._originY = origin[1]
    # defaults
    self._x1 = 1.0
    self._x2 = 0.0
    self._x3 = 0.0
    self._y1 = 0.0 
    self._y2 = 1.0
    self._y3 = 0.0
    self._xOrigin = 0.0 
    self._yOrigin = 0.0
    self._zOrigin = 0.0
    # process calibration file
    if (self._file):
      readcalib = trimmedLines(self._file)
      try:
        first = readcalib.next()
        if first == None:
          # Error
          sys.exit(1)

        dx = float(first)
        dy = float(readcalib.next())
        xa, xb, xc =  map(float,readcalib.next().split())
        ya, yb, yc =  map(float,readcalib.next().split())
        za, zb, zc =  map(float,readcalib.next().split())
      except StopIteration:
        print 'Error: calibration file too short'
        sys.exit(1)
      except ValueError, e:
        print 'Value Error in calibration file:', e
        sys.exit(1)
      self._x1 = (xb - xa) / dx
      self._x2 = (yb - ya) / dx
      self._x3 = (zb - za) / dx
      self._y1 = (xc - xa) / dy
      self._y2 = (yc - ya) / dy
      self._y3 = (zc - za) / dy
      self._xOrigin = xa
      self._yOrigin = ya
      self._zOrigin = za

  def dump(self):
    print "Calibration file:", self._file
    print "Motor PV names:", self._pvnames
    print "Motor coord for sample (0,0) = %5.3f, %5.3f, %5.3f" % ( self._xOrigin, self._yOrigin, self._zOrigin )
    print "Coefficients x1 x2 x3: %7.4e, %7.4e, %7.4e" % ( self._x1, self._x2, self._x3 )
    print "Coefficients y1 y2 y3: %7.4e, %7.4e, %7.4e" % ( self._y1, self._y2, self._y3 )

  def test(self, x, y):
    cmds = self.convert( x, y )
    print   'Calib Test: Sample coords (%5.3f,%5.3f) ==> motor coords: ( %7.4f, %7.4f, %7.4f )\n' \
            % ( x, y, cmds[0][1], cmds[1][1], cmds[2][1] )

  def convert(self, x, y):
    x += self._originX
    y += self._originY
    d1 = (x * self._x1) + (y * self._y1)
    d2 = (x * self._x2) + (y * self._y2)
    d3 = (x * self._x3) + (y * self._y3)
    motorCommands = [   (self._pvnames[0], d1 + self._xOrigin ),
                        (self._pvnames[1], d2 + self._yOrigin ),
                        (self._pvnames[2], d3 + self._zOrigin ) ]
    return motorCommands

#
# doneMoving - class for motor movement
#
class doneMoving(Pv):
  def __init__(self, name):
    Pv.__init__(self, name)
    self.monitor_cb = self.monitor_handler
    self.__sem = threading.Event()

  def wait_for_done(self):
    moving = False
    while not moving:
      self.__sem.wait(0.1)
      if self.__sem.isSet():
        self.__sem.clear()
        if self.value == 0:
          moving = True
      else:
        print 'timedout while waiting for moving'
        break
    while moving:
      self.__sem.wait(1000)
      if self.__sem.isSet():
        self.__sem.clear()
        if self.value == 1:
          moving = False
      else:
        print 'timedout while waiting for done'
        break

  def monitor_handler(self, exception=None):
    try:
      if exception is None:
#         print 'pv %s is %d' %(self.name, self.value)
        self.__sem.set()
      else:
        print "%-30s " %(self.name), exception
    except Exception, e:
      print e

def showUsage():
  sFnCmd = os.path.basename( sys.argv[0] )
  print("Usage: %s OPTION...\n" % sFnCmd)
  print( "    -h | --help                            Show usage information" )
  print( "    -m | --mshot     <NumShots>            Run multiple shot integration of <NumShots>. Default: 1" )
  print( "    -e | --expdelay  <Delay>               Set exposure time delay to <Delay> second. Default: 0" )
  print( "    -p | --post      <PostDelay>           Set post delay to <Delay> second. Default: 0" )
  print( "    -r | --rate      <Rate>                Set burst rate to <rate>. Default: use Beam Rate" )
  print( "    -s | --sim                             Run in simulation mode. No Mcc Burst is called.")
  print( "    -v | --verbose                         Be verbose")
  print( "    -q | --nodaq                           Run without affecting DAQ")
  print( "    -t | --nomotors                        Run without affecting motors")
  print( "    -F | --first     <Count>               Start scan at this step count")
  print( "    -L | --last      <Count>               End scan at this step count")
  print( "    --motorpvname    <x>,<y>,<z>           x/y/z motor PV names")
  print( "    --gridorigin     <X>,<Y>               Grid Offset X/Y (sample coords). Default: 0,0")
  print( "    --xfrom          <Pos>                 X starting position (sample coords)")
  print( "    --xto            <Pos>                 X ending position (sample coords)")
  print( "    --xsteps         <Count>               X number of steps. Default: 0")
  print( "    --yfrom          <Pos>                 Y starting position (sample coords)")
  print( "    --yto            <Pos>                 Y ending position (sample coords)")
  print( "    --ysteps         <Count>               Y number of steps. Default: 0")
  print( "    --calib          <Filename>            Motor calibration file")

def toInt(x):
  return int(x)

def main():
  try:
    (llsOptions, lsRemainder) = getopt.getopt(sys.argv[1:], \
        'hm:e:r:p:svqtF:L:', \
        ['help', 'mshot=', 'verbose', 'nodaq', 'nomotors', 'expdelay=', 'shutter=', 'rate=', 'post=', 'delaymode=', 'sim',
         'motorpvname=', 'xfrom=', 'xto=', 'yfrom=', 'yto=', 'first=', 'last=',
         'calib=', 'gridorigin=',
         'xsteps=', 'ysteps='])
  except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    showUsage()
    sys.exit(2)

  iNumShot   = 1
  iFirst     = 0
  iLast      = 1000000000
  fExpDelay  = 0
  fPostDelay = 0
  iShutter   = 5

  fBurstRate = 30 # for Opal 4K camera
  bDelayMode = True
  bSimMode   = False

  motorpvnames = None
  xfrom = None
  xto = None
  yfrom = None
  yto = None
  iXsteps = 0
  iYsteps = 0
  calibfile = None
  gridorigin = None
  verbose = False
  nodaq = False
  nomotors = False

  argErr = 0

  try:
    for (sOpt, sArg) in llsOptions:
      if sOpt in ('-h', '--help' ):
        showUsage()
        return 1
      elif sOpt in ('-m', '--mshot'):
        iNumShot   = int(sArg)
      elif sOpt in ('-F', '--first'):
        iFirst   = int(sArg)
      elif sOpt in ('-L', '--last'):
        iLast   = int(sArg)
      elif sOpt in ('-v', '--verbose'):
        verbose = True
      elif sOpt in ('-q', '--nodaq'):
        nodaq = True
      elif sOpt in ('-t', '--nomotors'):
        nomotors = True
      elif sOpt in ('-e', '--expdelay'):
        fExpDelay  = float(sArg)
      elif sOpt in ('-p', '--post'):
        fPostDelay = float(sArg)
      #elif sOpt in ('-s', '--shutter'):
      #  iShutter   = int(sArg)
      elif sOpt in ('-r', '--rate'):
        fBurstRate = float(sArg)
      elif sOpt in ('-d', '--delaymode'):
        bDelayMode = (int(sArg) != 0)
      elif sOpt in ('-s', '--sim'):
        bSimMode   = True
      elif sOpt in ('--motorpvname'):
        motorpvnames = sArg.split(',')
      elif sOpt in ('--xfrom'):
        xfrom = float(sArg)
      elif sOpt in ('--xto'):
        xto = float(sArg)
      elif sOpt in ('--xsteps'):
        iXsteps = int(sArg)
      elif sOpt in ('--yfrom'):
        yfrom = float(sArg)
      elif sOpt in ('--yto'):
        yto = float(sArg)
      elif sOpt in ('--ysteps'):
        iYsteps = int(sArg)
      elif sOpt in ('--calibfile'):
        calibfile = sArg
      elif sOpt in ('--gridorigin'):
        gridorigin = map(float,sArg.split(','))
  except ValueError, e:
    argErr = 1
    print "Value Error:", e
  except:
    argErr = 1
    print "Unexpected error:", sys.exc_info()[0]

  if motorpvnames is None:
    print 'missing option: --motorpvname'
    argErr = 1
  elif len(motorpvnames) != 3:
    print 'error: --motorpvname must have 3 elements'
    argErr = 1
  if xfrom is None:
    print 'missing option: --xfrom'
    argErr = 1
  if yfrom is None:
    print 'missing option: --yfrom'
    argErr = 1
  if (iXsteps > 0) and (xto is None):
    print 'missing option: --xto'
    argErr = 1
  if (iYsteps > 0) and (yto is None):
    print 'missing option: --yto'
    argErr = 1
  if iXsteps < 0:
    print 'error: --xsteps must be greater than or equal to 0'
    argErr = 1
  if iYsteps < 0:
    print 'error: --ysteps must be greater than or equal to 0'
    argErr = 1
  if gridorigin != None:
    if len(gridorigin) != 2:
      print 'error: --gridorigin must have 2 elements'
      argErr = 1

  if argErr:
    showUsage()
    return 1

  motorpv={}
  dmovpv={}

  calibrate = Calib(calibfile, motorpvnames, gridorigin)
  if verbose:
    calibrate.dump()
    calibrate.test( 0, 0 )
    calibrate.test( 0, 1 )
    calibrate.test( 1, 0 )

  if nomotors:
    if verbose:
      print 'Skip connecting motors'
  else:
    try:
      for (motorpvname, ignore) in calibrate.convert(0,0):
        if verbose:
          print 'Connecting to motor:', motorpvname
        motorpv[motorpvname] = Pv(motorpvname)
        motorpv[motorpvname].connect(1.0)
        dmovpv[motorpvname] = doneMoving(motorpvname + '.DMOV')
        dmovpv[motorpvname].connect(1.0)
        dmovpv[motorpvname].monitor(evtmask, ctrl=False)
    except:
      print 'Error occured while connecting motors'
      raise

  #
  #  Create template controlPV list for DAQ
  #
  saveList = list()
  motorCommands = calibrate.convert(xfrom, yfrom)
  for pv, position in motorCommands:
      saveList.append((pv, position))
      
#  daq  = PrincetonDaqMultipleShot(iNumShot, fExpDelay, fPostDelay, iShutter, fBurstRate, bDelayMode, bSimMode, saveList)
#  xact = DaqMultipleShotNonInteractive(daq, iShutter)

  if nodaq is False:
    daq  = princeton.PrincetonDaqMultipleShot(iNumShot, fExpDelay, fPostDelay, iShutter, fBurstRate, bSimMode, False ,0.0)
    success = daq.init(controls=[],bDaqBegin=False)
    if success != 0 :
      print "Failed to initialize DAQ"
      sys.exit(1)


  print "wait for event sequencer...sleep 0.5 seconds"
  time.sleep(0.5)

  #
  # Loop through X,Y positions
  #
  stepTotal = ((iYsteps+1) * (iXsteps+1))
  stepCount = 0
  for yy in xrange(iYsteps+1):
    if iYsteps >= 1:
      ypos = yfrom + (yy * ((yto - yfrom) / iYsteps))
    else:
      ypos = yfrom

    for xx in xrange(iXsteps+1):
      stepCount = stepCount + 1

      # skip beginning (--first) or ending (--last) steps
      if (stepCount < iFirst) or (stepCount > iLast):
        continue

      if iXsteps >= 1:
        xpos = xfrom + (xx * ((xto - xfrom) / iXsteps))
      else:
        xpos = xfrom
      if verbose:
        print 'X,Y = %5.3f,%5.3f' % (xpos, ypos)

      motorCommands = calibrate.convert(xpos, ypos)

      saveList = list()

      xyzString = '  (x, y, z) = (%5.3f, %5.3f, %5.3f) ###' % (motorCommands[0][1], motorCommands[1][1], motorCommands[2][1])
      print '### STEP %d of %d   (x\', y\') = (%5.3f, %5.3f) %s' % (stepCount, stepTotal, xpos, ypos, xyzString)

      if nomotors:
        print 'skip moving motors'
      else:
        try:
          for pv, position in motorCommands:
            roundVal = '%5.3f' % position
            saveList.append((pv, position))
            if verbose:
              print 'Move motor: %s = %s' % (pv, roundVal)
            motorpv[pv].put(position, 1.0)
            pyca.flush_io()
        except:
          print 'Error occured while moving motors'
          raise
    
        ########## Wait for motors ################
        try:
          for pv, ignore in motorCommands:
            dmovpv[pv].wait_for_done() 
            print 'Motor %s done...' % pv
        except:
          print 'Error occured while waiting for motors'
          raise

      if verbose:
        print 'Values to be stored within DAQ calib:', saveList

      ########## Acquire data ###################
      iFail = 0
      if nodaq:
        print 'skip DAQ' 
      else:
        if verbose:
          print ' -- DAQ Begin ---------------'
        try:
          #iFail = xact.run(saveList)
          daq.beginCycle([])
          daq.getMoreImages(1)
          daq.endCycle()
        except:
          print 'Error occured while acquiring data'
          raise
        if iFail != 0:
          return 1
        time.sleep(1)
        if verbose:
          print ' -- DAQ End ---------------'


  if not nodaq :
    daq.deinit()
    time.sleep(0.5)


if __name__ == '__main__':
  status = main()
  sys.exit(status)
