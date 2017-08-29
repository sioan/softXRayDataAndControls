#!/bin/env python
#

import sys
import os
import getopt
import time
import pydaq
import pycdb
import traceback
from sequenceLoad import SequenceLoad
from cafunctions import caget, caput
from seqDefs     import *

class MccBurst:
  def __init__(self, bSimMode):
    self.bSimMode         = bSimMode
    self.bMccBurstRunning = False

  def mccBurstCheckInit(self):
    self.bMccBurstRunning   = not (caget(pvMccBurstReqBykik).find("No") != -1 and caget(pvMccBurstReqPoc).find("No") != -1)
    print "Mcc Burst Mode: %s" % ("Yes" if self.bMccBurstRunning else "No")

  def mccBurstCheckStatusChange(self):
    if self.bSimMode:
      return False
    bMccBurstCheck   = not (caget(pvMccBurstReqBykik).find("No") != -1 and caget(pvMccBurstReqPoc).find("No") != -1)
    if bMccBurstCheck != self.bMccBurstRunning:
      print "Original Burst mode: %s  Current: %s" % (("Yes" if self.bMccBurstRunning else "No"), ("Yes" if bMccBurstCheck else "No"))
      return True
    return False

  def mccBurstSetNumShot(self, iNumShots, iBurstRate):
    if self.bSimMode:
      return False
    print "Settings Mcc Burst Shot %d rate %d" % (iNumShots, iBurstRate)
    caput(pvMccBurstNumShot, iNumShots)  # Set # of bursts
    caput(pvMccBurstRate   , iBurstRate)
    return 0

  def mccBurstIsComplete(self):
    if self.bSimMode:
      return True
    return caget(pvMccBurstCtrl).find("Off") != -1

  def mccBurstCount(self):
    if self.bSimMode:
      return 0
    return int(caget(pvMccBurstCount))

  #def mccBurstRun(self):
  #  if self.bSimMode:
  #    return False
  #  caput(pvMccBurstCtrl, 1) # Burst Mode

  #def mccBurstOneShot(self):
  #  if self.bSimMode:
  #    return False
  #  caput(pvMccBurstNumShot, 1)  # Set # of burst = 1
  #  caput(pvMccBurstCtrl, 1)    # Burst Mode
  # return 0

class PrincetonDaqMultipleShot:
  def __init__(self, iNumShot, fExpDelay, fPostDelay, iShutter, fBurstRate, bDelayMode, bSimMode, controls=None):
    self.iNumShot   = iNumShot
    self.fExpDelay  = fExpDelay
    self.fPostDelay = fPostDelay
    self.iShutter   = iShutter
    self.fBurstRate = fBurstRate
    self.bDelayMode = bDelayMode
    self.bSimMode   = bSimMode
    self.controls   = controls

    self.daq = None
    self.iNumTotalImage   = 0
    self.mccBurst         = MccBurst(self.bSimMode)
    self.dictBeamToBurstRate = { 120: 0, 60: 0, 30: 1, 10: 2, 5: 3, 1: 4, 0.5: 5 }

    self.daq_host      = os.popen("hostname").read().strip()
    print "Host: %s" % self.daq_host
    self.daq_platform  = 0 # for MEC
    #self.lPvShutter    = [ "SXR:EXP:AOT:01", "SXR:EXP:AOT:02" ] # 0: THz shutter, 1: 800nm shutter
    self.lPvShutter    = [ "" ]
    self.iShutterOpenVal  = 5
    self.iShutterCloseVal = 0

    # Note: after SEB event, it takes 5 fiducials (13.89 ms) to receive the burst
    # Assumption: 1. Beam rate is 120Hz, 2. the SEB event is fired 1 fiducial after the 120Hz beam
    # If Beam rate is 60Hz or slower, the burst comes at the NEXT beam rate
    self.iSlowCamOpenDelay = 15  # unit: 360Hz

  def setPrincetonExposureSequence(self):
    print "Settings sequence for Princeton Start Exposure...\n"

    seq = SequenceLoad(iGroupNo)

    princetonExposure = seqGroupMin[iGroupNo] + 0
    mccBurstReadout   = seqGroupMin[iGroupNo] + 1
    sebBurstStart     = seqGroupMin[iGroupNo] + 13

    if self.bSimMode:
      iBurstDelay          = int(120 / self.fBurstRate)
      print "Burst rate %.1f delay %d" % (self.fBurstRate, iBurstDelay)
      seq.event_codes      = [princetonExposure] + [mccBurstReadout] * self.iNumShot
      seq.beam_delays      = [0, 2] + [iBurstDelay] * (self.iNumShot-1)
      seq.fiducial_delays  = [1, self.iSlowCamOpenDelay]
      seq.fiducial_delays  += [0]* ( len(seq.event_codes) - len(seq.fiducial_delays) )
    else:
      seq.event_codes      = [princetonExposure, sebBurstStart]
      seq.beam_delays      = [0, 0]
      seq.fiducial_delays  = [1, self.iSlowCamOpenDelay]

    seq.length = len(seq.event_codes)
    seq.load(verbose=True)
    return princetonExposure

  def init(self):
    self.pvLaserShutter = None
    if self.iShutter > 0 and self.iShutter <= len(self.lPvShutter):
      self.pvLaserShutter = self.lPvShutter[self.iShutter-1]

    fBeamFullRate = float(caget(pvBeamRate));
    if not self.bSimMode:
      print "\n## Beam rate = %.1f HZ" % (fBeamFullRate)
      if not (self.dictBeamToBurstRate.has_key(fBeamFullRate)):
        print "!!! Beam rate is not stable, please wait for beam to stablize and run the script again"
        return 1
      self.mccBurst.mccBurstCheckInit()

    caput(pvPlayMode         , 0) # PlayMode = Once
    caput(pvMccSeqSyncMarker , 6) # Set sequencer sync marker to 120Hz
    caput(pvMccSeqBeamRequest, 0) # Set seuqencer rate to be 120Hz (TS4|TS1)
    if self.bSimMode:
      caput(pvMccSynEvtBurst   , 0) # Diable SEB support
    else:
      caput(pvMccSynEvtBurst   , 1) # Enable SEB support

    if self.fBurstRate == -1:
      if self.bSimMode:
        self.fBurstRate = 120.0
      else:
        self.fBurstRate = fBeamFullRate

    if not self.bSimMode:
      self.mccBurst.mccBurstSetNumShot(self.iNumShot, self.dictBeamToBurstRate[self.fBurstRate])

    print "## Burst rate = %.1f HZ"   % (self.fBurstRate)
    print "## Multiple shot: %d" % (self.iNumShot)

    self.codeCommand = self.setPrincetonExposureSequence()

    # Exposure Time =
    #     delay from "real" princeton open and SEB burst start event (0 second)
    #     delay from SEB burst start event and MCC firing beam ( max( 1/60, 1/self.fBurstRate) )
    #     (x) + laser shutter open delay (Pv set + shutter physical open) (0.5 second)
    #     + manual sleep (fExpDelay)
    #     + exposure Time ((self.iNumShot / self.fBurstRate) second)
    #   = 0.0 + (self.iNumShot / self.fBurstRate) + fExpDelay  second

    # Setup Time =
    #     delay between setting pvPlayCtrl and the "real" princeton open (0.2 second)
    #   = 0.2

    self.fSetupTime    = 0.1
    self.fExposureTime = 0.0 + self.fExpDelay + self.iNumShot / float(self.fBurstRate) + max(1.0/120, 1.0/self.fBurstRate) + self.iSlowCamOpenDelay / 360.0

    self.daq = pydaq.Control(self.daq_host, self.daq_platform)

    print ' *** PrincetonDaqMultipleShot.init(): self.controls =', self.controls

    #
    #  Send the structure the first time to put the control variables
    #    in the file header

    print "daq connect...",
    sys.stdout.flush()
    try:
      self.daq.connect() # get dbpath and key from DAQ
    except Exception, e:
      print e
      print "Please select devices and click Select button in DAQ Control window"
    print " done."

    if self.bSimMode:
      self.alias = "SLOW_CAMERA"
    else:
      self.alias = "SLOW_CAMERA"

    if self.daq.dbalias() != self.alias:
      print "!!! the current DAQ config type is %s" % (self.daq.dbalias())
      print "!!! please switch to %s to run this script" % (self.alias)

      print "daq disconnect...",
      sys.stdout.flush()
      self.daq.disconnect()
      print " done."
      return 2

    iFail = self.configure()
    if iFail != 0:
      print "daq disconnect...",
      sys.stdout.flush()
      self.daq.disconnect()
      print " done."
      return 3

    self.iNumTotalImage = 0

    print "## Please make sure"
    if not self.bSimMode:
      print "##   1. MCC has switched to Burst Mode,"
    print "##   2. Princeton camera is selected,"
    print "##   3. only one processing node is selected,"
    print "##   4. chiller is running and the cooling temperature is set properly."

    time.sleep(0.5) # wait for EVR to enable
    return 0

  def begin(self, controls):
    print "daq begin...",
    sys.stdout.flush()
#    self.daq.begin(events=0) # run until we call daq.stop()
    self.daq.begin(events=0,controls=controls) # run until we call daq.stop()
    print " done."

  def configure(self):
    cdb = pycdb.Db(self.daq.dbpath())
    newkey = cdb.get_key(self.alias)
    print "db path = %s  key = 0x%x" % (self.daq.dbpath(), self.daq.dbkey())

    lXtcPrinceton = cdb.get(key=newkey,typeid=0x00050012) # PrincetonConfig, V5

    fMaxReadoutTime = 0
    lSpeedTable     = [ 0.1, 1, 0, 0, 1, 2 ]
    print "Found %d Princeton Configs" % (len(lXtcPrinceton))
    for iCamera in range(len(lXtcPrinceton)):
      print "Princeton %d:" %(iCamera)
      xtc              = lXtcPrinceton[iCamera]
      configPrinceton  = xtc.get()
      fOrgExposureTime = float(configPrinceton['exposureTime'])
      width            = configPrinceton['width']
      height           = configPrinceton['height']
      speed            = configPrinceton['readoutSpeedIndex']
      code             = configPrinceton['exposureEventCode']
      kineticHeight    = configPrinceton['kineticHeight']

      configPrinceton['exposureEventCode'] = self.codeCommand

      if speed < 0 or speed > len(lSpeedTable) or lSpeedTable[speed] == 0:
        #print "*** Princeton %d configuation error: Unknown speed setting %d\n"\
        #  "Please check the readout speed index in the configuration window\n"\
        #  % (iCamera, speed)
        speed = 1
        #return 1

      #fReadoutTime = 4.7 * width * height / ( lSpeedTable[speed] * 2048 * 2048 )
      fReadoutTime = 4.7 / lSpeedTable[speed]
      if fReadoutTime > fMaxReadoutTime:
        fMaxReadoutTime = fReadoutTime

      print "  W %d H %d speed %d code %d readout %.3f" % (width, height, speed, configPrinceton['exposureEventCode'], fReadoutTime)

      if kineticHeight == 0:
        print "  Exposure time (Original) [%d]: %.3f s" % (iCamera, fOrgExposureTime)
        configPrinceton['exposureTime']     = self.fExposureTime
        print "  Exposure time (New)      [%d]: %.3f s" % (iCamera, configPrinceton['exposureTime'])
      else:
        if height % kineticHeight != 0:
          print "!!! Princeton %d Illegal kinetics height %d (Image height %d)" \
           % (iCamera, kineticHeight, height)
          return 2
        iNumKineticShot = height / kineticHeight
        print "  Kinetic mode: shots = %d" % (iNumKineticShot)
        if self.fBurstRate * fOrgExposureTime >= 1:
          print "!!! Princeton %d exposure time %f slower than beam rate %f. Not okay for kinetics mode" \
           % (iCamera, fOrgExposureTime, self.fBurstRate)
          return 2
        if self.iNumShot != iNumKineticShot:
          self.iNumShot = iNumKineticShot
          if self.bSimMode:
            self.codeCommand = self.setPrincetonExposureSequence()
          else:
            self.mccBurst.mccBurstSetNumShot(self.iNumShot, self.dictBeamToBurstRate[self.fBurstRate])

      configPrinceton['numDelayShots'] = self.iNumShot
      print "  Number of Delayed Shots: [%d]: %d" % (iCamera, configPrinceton['numDelayShots'])

      xtc.set(configPrinceton)
      cdb.set(xtc = xtc, alias = self.alias)

    lSpeedTable     = [ 0.2, 1 ]
    lXtcFli = cdb.get(key=newkey,typeid=0x00010037) # FliConfig, V1
    print "Found %d Fli Configs" % (len(lXtcFli))
    for iCamera in range(len(lXtcFli)):
      print "Fli %d:" %(iCamera)
      xtc              = lXtcFli[iCamera]
      configFli        = xtc.get()
      fOrgExposureTime = float(configFli['exposureTime'])
      width            = configFli['width']
      height           = configFli['height']
      speed            = configFli['readoutSpeedIndex']
      code             = configFli['exposureEventCode']

      configFli['exposureEventCode'] = self.codeCommand

      if speed < 0 or speed > len(lSpeedTable) or lSpeedTable[speed] == 0:
        print "*** Fli %d configuation error: Unknown speed setting %d\n"\
          "Please check the readout speed index in the configuration window\n"\
          % (iCamera, speed)
        return 1

      #fReadoutTime = 4.3 * width * height / (4096 * 4096)
      fReadoutTime = 4.3 / lSpeedTable[speed]
      if fReadoutTime > fMaxReadoutTime:
        fMaxReadoutTime = fReadoutTime

      print "  W %d H %d speed %d code %d readout %.3f" % (width, height, speed, configFli['exposureEventCode'], fReadoutTime)
      print "  Exposure time (Original) [%d]: %.3f s" % (iCamera, fOrgExposureTime)
      configFli['exposureTime']     = self.fExposureTime
      print "  Exposure time (New)      [%d]: %.3f s" % (iCamera, configFli['exposureTime'])

      configFli['numDelayShots'] = self.iNumShot
      print "  Number of Delayed Shots: [%d]: %d" % (iCamera, configFli['numDelayShots'])

      xtc.set(configFli)
      cdb.set(xtc = xtc, alias = self.alias)

    lSpeedTable     = [ 1, 0.6, 0.2, 0.01 ]
    lXtcAndor = cdb.get(key=newkey,typeid=0x0001003C) # AndorConfig, V1
    print "Found %d Andor Configs" % (len(lXtcAndor))
    for iCamera in range(len(lXtcAndor)):
      print "Andor %d:" %(iCamera)
      xtc              = lXtcAndor[iCamera]
      configAndor      = xtc.get()
      fOrgExposureTime = float(configAndor['exposureTime'])
      width            = configAndor['width']
      height           = configAndor['height']
      speed            = configAndor['readoutSpeedIndex']
      code             = configAndor['exposureEventCode']

      configAndor['exposureEventCode'] = self.codeCommand

      if speed < 0 or speed > len(lSpeedTable) or lSpeedTable[speed] == 0:
        print "*** Andor %d configuation error: Unknown speed setting %d\n"\
          "Please check the readout speed index in the configuration window\n"\
          % (iCamera, speed)
        return 1

      fReadoutTime = 1.1 / lSpeedTable[speed]
      if fReadoutTime > fMaxReadoutTime:
        fMaxReadoutTime = fReadoutTime

      print "  W %d H %d speed %d code %d readout %.3f" % (width, height, speed, configAndor['exposureEventCode'], fReadoutTime)
      print "  Exposure time (Original) [%d]: %.3f s" % (iCamera, fOrgExposureTime)
      configAndor['exposureTime']     = self.fExposureTime
      print "  Exposure time (New)      [%d]: %.3f s" % (iCamera, configAndor['exposureTime'])

      configAndor['numDelayShots'] = self.iNumShot
      print "  Number of Delayed Shots: [%d]: %d" % (iCamera, configAndor['numDelayShots'])

      xtc.set(configAndor)
      cdb.set(xtc = xtc, alias = self.alias)

    cdb.commit()
    newkey = cdb.get_key(self.alias)

    # Image time =
    #  fSetupTime
    #  fExposureTime +
    #  camera readout time (4.7 second for 2048x2048 @ 1M, or fMaxReadoutTime) +
    #  Tolerance (0.3 second) +
    #  Min (
    #        Network data transfer delay (Number of shots / 100) ,
    #        Max limit (20 seconds) )
    #   + manual delay (overhead_delay)
    #   + delay for multiple princeton program (traffic shaping) (1 second for 3 programs)
    #
    if self.bDelayMode:
      fNetworkDelay = 0
    else:
      fNetworkDelay = self.iNumShot/100.0
    self.fImageTime = self.fSetupTime + self.fExposureTime + fMaxReadoutTime + 0.3 + fNetworkDelay + self.fPostDelay + 1
    if self.fImageTime < 0: self.fImageTime = 0

    # Post Sleep time =
    #  Image time -
    #    ( Delay between setting pvPlayCtrl and princeton open (0.5 second) +
    #      fExposureTime )
    #
    self.fPostSleep = self.fImageTime - 0.5 - self.fExposureTime

    print "setting exposure time to %.2f s. Expected image time %.2f s postSleep %.2f s" % (self.fExposureTime, self.fImageTime, self.fPostSleep)

    self.fImageTime_seconds = int(self.fImageTime)
    self.fImageTime_nanoseconds = int((self.fImageTime - float(self.fImageTime_seconds))*1.e9)

    #
    #    self.daq.configure(events=options.events,
    #                  controls=[('EXAMPLEPV1',0),('EXAMPLEPV2',0)],
    #                  monitors=[('BEAM:LCLS:ELEC:Q',options.qbeam,1.)])
    #
    #    self.daq.configure(record=do_record,
    #                  events=options.events,
    #                  controls=[('EXAMPLEPV1',0),('EXAMPLEPV2',0)])

    print "daq configure...",
    sys.stdout.flush()
    self.daq.configure(key=newkey,controls=self.controls)
    print " done."

    return 0

  def getMoreImages(self, iNumImage):
    for iImage in xrange(iNumImage):
      if (not self.bSimMode) and self.mccBurst.mccBurstCheckStatusChange():
        print "Burst Mode status changed"
        break

      timeBeforeImage = time.time()

      print "# Image %d/%d (%d Shots) [total images: %d]" % (1+iImage, iNumImage, self.iNumShot, self.iNumTotalImage)
      iEventStart = self.daq.eventnum()

      timeAfterImageBegin = time.time()

#
#  Add a retry loop in case the EVR isn't ready when the sequence runs
#
      while True:

        caput(pvPlayCtrl, 1) # PlayCtrl = Play

        timeAfterPlay = time.time()

        time.sleep(0.05)
        while True:
          if caget(pvPlayStat).find("Stopped") != -1:
            break
          if self.bSimMode:
            iSeqStep = int(caget(pvPlayCurStep))
            print "Burst count: %d / %d\r" % (iSeqStep, self.iNumShot),
            sys.stdout.flush()
          time.sleep(0.05)

        if self.pvLaserShutter:
          caput(self.pvLaserShutter, self.iShutterOpenVal)
          time.sleep(0.5)
          iLaserShutterState = int(caget(self.pvLaserShutter))
          if iLaserShutterState != self.iShutterOpenVal:
            print "!!! Shutter %s Not Open: Current value = %d (expected %d)" % (self.pvLaserShutter, iLaserShutterState, self.iShutterOpenVal)

        timeBeforeBurst = time.time()

        if not self.bSimMode:
          time.sleep(0.02)
          while True:
            if self.mccBurst.mccBurstIsComplete():
              break
            iNumBurstCount = self.mccBurst.mccBurstCount()
            print "Burst count: %d / %d\r" % (iNumBurstCount, self.iNumShot),
            sys.stdout.flush()
            time.sleep(0.05)

        timeAfterBurstComplete = time.time()

        if self.pvLaserShutter:
          caput(self.pvLaserShutter, self.iShutterCloseVal)
          time.sleep(0.5)
          iLaserShutterState = int(caget(self.pvLaserShutter))
          if iLaserShutterState != self.iShutterCloseVal:
            print "!!! Shutter %s Not Closed: Current value = %d (expected %d)" % (self.pvLaserShutter, iLaserShutterState, self.iShutterCloseVal)

        print "Waiting for device readout... "
        if self.fPostDelay > 0:
          print "Sleeping for %.1f seconds... " % (self.fPostDelay),
          sys.stdout.flush()
          time.sleep(self.fPostDelay) # post delay: wait for DAQ to really ends if data valume is too large
          print "done."

        print "Waiting for princeton images (* may not wait long enough with multiple readout groups)"

        timeToRetry = time.time() + 15
      
        while True:
          nevents = self.daq.eventnum()
          if nevents >= iEventStart + self.iNumShot:
            break
          if time.time() > timeToRetry:
            break
          print "DAQ event: %d / %d\r" % (self.daq.eventnum(), iEventStart + self.iNumShot),
          sys.stdout.flush()
          time.sleep(0.05)
        print "                           \r",

        timeEndImage = time.time()
        print "time (sec): Image %.2f Begin %.2f SeqPvSet %.2f PlaySeq %.2f Burst %.2f End %.2f" %\
              (timeEndImage-timeBeforeImage,  \
               timeAfterImageBegin - timeBeforeImage, timeAfterPlay - timeAfterImageBegin, \
               timeBeforeBurst - timeAfterPlay, timeAfterBurstComplete - timeBeforeBurst,  \
               timeEndImage-timeAfterBurstComplete )
        
        if nevents >= iEventStart + self.iNumShot:
          self.iNumTotalImage += 1
          break

        print "Failed to receive image... moving on."
        break
        
    # end: for iImage in xrange(iNumImage)

  def numTotalImage(self):
    return self.iNumTotalImage

  def deinit(self):
    if self.daq == None:
      return

    try:
      print "daq stop...",
      sys.stdout.flush()
      self.daq.stop()
      print " done."
    except:
      print "self.daq.stop() timeout"

    try:
      print "daq end...",
      sys.stdout.flush()
      self.daq.end()
      print " done."
    except:
      print "self.daq.end() timeout"

    print "daq disconnect...",
    sys.stdout.flush()
    self.daq.disconnect()
    print " done."

class DaqMultipleShotInteractive:
  def __init__(self):
    pass

  def run(self, princetonDaq, iShutter):
    iFail = princetonDaq.init()
    if iFail != 0:
      return 1

    princetonDaq.begin(princetonDaq.controls)
    
    try:
      while True:
        #
        #  Wait for the user to continue
        #
        print('--Enter a number + <Enter> to get more images, or just Hit <Enter> to end run and exit--')
        sMoreImage = raw_input("> ")

        try:
          iMoreImage = int(sMoreImage)
        except:
          iMoreImage = 0

        if iMoreImage <= 0:
          break

        print("Will get %d more images..." % iMoreImage)
        princetonDaq.getMoreImages(iMoreImage)
        # go to next loop to get more Images
      #end of while True:

      daq = princetonDaq.daq
      print "# (If Record Run is ON) Experiment %d Run %d (%d images)" % (daq.experiment(),daq.runnumber(), princetonDaq.numTotalImage())
      princetonDaq.deinit()
      time.sleep(0.5)
    except:
      print
      if iShutter != 0:
        for pvLaserShutter in princetonController.lPvShutter:
          caput(pvLaserShutter, princetonController.iShutterCloseVal)
          time.sleep(0.5)
          iLaserShutterState = int(caget(pvLaserShutter))
          if iLaserShutterState != princetonController.iShutterCloseVal:
            print "!!! Shutter %s Not Close: Current value = %d (expected %d)" % (pvLaserShutter, iLaserShutterState, princetonController.iShutterCloseVal)
        print "!!! Please remember to check if laser shutters are closed"
        print "!!! Script exits abnormally (may be interrupted by user)"

    return 0

class DaqMultipleShotNonInteractive:
  def __init__(self,daq,iShutter):
    self.daq = daq
    self.iShutter = iShutter
    if self.daq.init() != 0:
      raise RuntimeError
    pass

  def run(self, controls):

    self.daq.begin(controls)
    time.sleep(0.10);     #  Wait for EVR to finish enable (sync with slaves)
    self.daq.getMoreImages(1)
    self.daq.daq.stop()
    self.daq.daq.end()

#    except:
#      print
#      if iShutter != 0:
#        for pvLaserShutter in princetonController.lPvShutter:
#          caput(pvLaserShutter, princetonController.iShutterCloseVal)
#          time.sleep(0.5)
#          iLaserShutterState = int(caget(pvLaserShutter))
#          if iLaserShutterState != princetonController.iShutterCloseVal:
#            print "!!! Shutter %s Not Close: Current value = %d (expected %d)" % (pvLaserShutter, iLaserShutterState, princetonController.iShutterCloseVal)
#        print "!!! Please remember to check if laser shutters are closed"
#        print "!!! Script exits abnormally (may be interrupted by user)"
#
    return 0

class DaqMultipleShot:
  def __init__(self, iNumShot, fExpDelay, fPostDelay, iShutter, fBurstRate, bDelayMode, bSimMode, controls=None):
    self.iNumShot   = iNumShot
    self.iShutter   = iShutter
    self.fBurstRate = fBurstRate
    self.bSimMode   = bSimMode
    self.controls   = controls
    
    self.daq = None
    self.iNumTotalImage   = 0
    self.mccBurst         = MccBurst(self.bSimMode)
    self.dictBeamToBurstRate = { 120: 0, 60: 0, 30: 1, 10: 2, 5: 3, 1: 4, 0.5: 5 }

    self.daq_host      = os.popen("hostname").read().strip()
    print "Host: %s" % self.daq_host
    self.daq_platform  = 0 # for MEC
    #self.lPvShutter    = [ "SXR:EXP:AOT:01", "SXR:EXP:AOT:02" ] # 0: THz shutter, 1: 800nm shutter
    self.lPvShutter    = [ "" ]
    self.iShutterOpenVal  = 5
    self.iShutterCloseVal = 0
  def init(self):
    self.pvLaserShutter = None
    if self.iShutter > 0 and self.iShutter <= len(self.lPvShutter):
      self.pvLaserShutter = self.lPvShutter[self.iShutter-1]

    fBeamFullRate = float(caget(pvBeamRate));
    if not self.bSimMode:
      print "\n## Beam rate = %.1f HZ" % (fBeamFullRate)
      if not (self.dictBeamToBurstRate.has_key(fBeamFullRate)):
        print "!!! Beam rate is not stable, please wait for beam to stablize and run the script again"
        return 1
      self.mccBurst.mccBurstCheckInit()

    if self.fBurstRate == -1:
      if self.bSimMode:
        self.fBurstRate = 120.0
      else:
        self.fBurstRate = fBeamFullRate

    if not self.bSimMode:
      self.mccBurst.mccBurstSetNumShot(self.iNumShot, self.dictBeamToBurstRate[self.fBurstRate])

    print "## Burst rate = %.1f HZ"   % (self.fBurstRate)
    print "## Multiple shot: %d" % (self.iNumShot)

    self.daq = pydaq.Control(self.daq_host, self.daq_platform)

    print ' *** DaqMultipleShot.init(): self.controls =', self.controls

    #
    #  Send the structure the first time to put the control variables
    #    in the file header

    print "daq connect...",
    sys.stdout.flush()
    try:
      self.daq.connect() # get dbpath and key from DAQ
    except Exception, e:
      print e
      print "Please select devices and click Select in the DAQ Control window"
    print " done."

    iFail = self.configure()
    if iFail != 0:
      print "daq disconnect...",
      sys.stdout.flush()
      self.daq.disconnect()
      print " done."
      return 3

    self.iNumTotalImage = 0

    print "## Please make sure"
    if not self.bSimMode:
      print "##   1. MCC has switched to Burst Mode,"
    print "##   2. Desired device is selected,"
    print "##   3. only one processing node is selected,"

    time.sleep(0.5) # wait for EVR to enable
    return 0

  def begin(self, controls):
    print "daq begin...",
    sys.stdout.flush()
#    self.daq.begin(events=0) # run until we call daq.stop()
    self.daq.begin(events=0,controls=controls) # run until we call daq.stop()
    print " done."
    
  def configure(self):
    cdb = pycdb.Db(self.daq.dbpath())
    newkey = self.daq.dbkey()
    print "db path = %s  key = 0x%x" % (self.daq.dbpath(), self.daq.dbkey())

    print "daq configure...",
    sys.stdout.flush()
#    self.daq.configure(key=newkey)
    self.daq.configure(key=newkey,controls=self.controls)
    print " done."

    return 0

  def getMoreImages(self, iNumImage):
    for iImage in xrange(iNumImage):
      if (not self.bSimMode) and self.mccBurst.mccBurstCheckStatusChange():
        print "Burst Mode status changed"
        break

      timeBeforeImage = time.time()

      print "# Image %d/%d (%d Shots) [total images: %d]" % (1+iImage, iNumImage, self.iNumShot, self.iNumTotalImage)
      iEventStart = self.daq.eventnum()

      caput(pvPlayCtrl, 1) # PlayCtrl = Play

      timeAfterPlay = time.time()
      
      time.sleep(0.05)
      while True:
        if caget(pvPlayStat).find("Stopped") != -1:
          break
        if self.bSimMode:
          iSeqStep = int(caget(pvPlayCurStep))
          print "Burst count: %d / %d\r" % (iSeqStep, self.iNumShot),
          sys.stdout.flush()
        time.sleep(0.05)

      if self.pvLaserShutter:
        caput(self.pvLaserShutter, self.iShutterOpenVal)
        time.sleep(0.5)
        iLaserShutterState = int(caget(self.pvLaserShutter))
        if iLaserShutterState != self.iShutterOpenVal:
          print "!!! Shutter %s Not Open: Current value = %d (expected %d)" % (self.pvLaserShutter, iLaserShutterState, self.iShutterOpenVal)

      if not self.bSimMode:
        time.sleep(0.02)
        while True:
          if self.mccBurst.mccBurstIsComplete():
            break
          iNumBurstCount = self.mccBurst.mccBurstCount()
          print "Burst count: %d / %d\r" % (iNumBurstCount, self.iNumShot),
          sys.stdout.flush()
          time.sleep(0.05)

      timeAfterBurstComplete = time.time()

      if self.pvLaserShutter:
        caput(self.pvLaserShutter, self.iShutterCloseVal)
        time.sleep(0.5)
        iLaserShutterState = int(caget(self.pvLaserShutter))
        if iLaserShutterState != self.iShutterCloseVal:
          print "!!! Shutter %s Not Closed: Current value = %d (expected %d)" % (self.pvLaserShutter, iLaserShutterState, self.iShutterCloseVal)

      while True:
        if self.daq.eventnum() >= iEventStart + self.iNumShot:
          break
        print "DAQ event: %d / %d\r" % (self.daq.eventnum(), iEventStart + self.iNumShot),
        sys.stdout.flush()
        time.sleep(0.05)
      print "                           \r",

      self.iNumTotalImage += 1
    # end: for iImage in xrange(iNumImage)

  def numTotalImage(self):
    return self.iNumTotalImage

  def deinit(self):
    if self.daq == None:
      return

    try:
      print "daq stop...",
      sys.stdout.flush()
      self.daq.stop()
      print " done."
    except:
      print "self.daq.stop() timeout"

    try:
      print "daq end...",
      sys.stdout.flush()
      self.daq.end()
      print " done."
    except:
      print "self.daq.end() timeout"

    print "daq disconnect...",
    sys.stdout.flush()
    self.daq.disconnect()
    print " done."


def showUsage():
  sFnCmd = os.path.basename( sys.argv[0] )
  print(
    "Usage: %s [-h | --help] [-m|--mshot <NumShots>] [-e|--expdelay <Delay>] [-p|--post <postDealy>]\n"
    "    [-r|--rate <rate>] [-s|--sim]" % sFnCmd )
  print( "    -h | --help                   Show usage information" )
  print( "    -m | --mshot     <NumShots>    Run multiple shot integration of <NumShots>. Default: 1" )
  print( "    -e | --expdelay  <Delay>       Set exposure time delay to <Delay> second. Default: 0" )
  print( "    -p | --post      <PostDelay>   Set post delay to <Delay> second. Default: 0" )
  #print( "    -s | --shutter   <0-2>         Select shutter. 0: No shutter, 1: Shutter 1, 2: Shutter 2. Default: 0" )
  print( "    -r | --rate      <Rate>        Set burst rate to <rate>. Default: use Beam Rate" )
  print( "    -s | --sim                     Run in simulation mode. No Mcc Burst is called.")
  #print( "    -d | --delaymode <0/1>         (Default: 1) 0: normal mode 1: delay mode" )

def main():
  (llsOptions, lsRemainder) = getopt.getopt(sys.argv[1:], \
      'hm:e:r:p:s', \
      ['help', 'mshot=', 'expdelay=', 'shutter=', 'rate=', 'post=', 'delaymode=', 'sim'] )

  iNumShot   = 1
  fExpDelay  = 0
  fPostDelay = 0
  iShutter   = 0

  fBurstRate = 120 
  bDelayMode = True
  bSimMode   = False
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
    #elif sOpt in ('-s', '--shutter'):
    #  iShutter   = int(sArg)
    elif sOpt in ('-r', '--rate'):
      fBurstRate = float(sArg)
    elif sOpt in ('-d', '--delaymode'):
      bDelayMode = (int(sArg) != 0)
    elif sOpt in ('-s', '--sim'):
      bSimMode   = True
  try:
    PrincetonMultipleShotInteractive().run(iNumShot, fExpDelay, fPostDelay, iShutter, fBurstRate, bDelayMode, bSimMode)
  except:
    traceback.print_exc(file=sys.stdout)
  return

if __name__ == '__main__':
  status = main()
  sys.exit(status)
