#!/bin/env python
#
# Note: modified by Tomy again for SXR
# Author: Zhou Xing
# Email: zxing@slac.stanford.edu
#
# Any change to this script should be sent to MEC staff member:
#Z. Xing, B. Nagler, E. Galtier 
#
# Date: 05 March 2015
# Original princeton.py script written by Tomy Tsai and MEC staff.  
# Modified by Ankush Mitra for use in SXR.
# - To allow two Andor cameras to be read out one after the other, add
#   option include camera readout time. To make two cameras readout
#   one after the other, 
#     - set camera A exposure time : tA
#     - set camera B exposure time : tA + readout-time 



import sys
import os
import getopt
import time
import datetime

try:
  import pydaq
except:
  print "pydaq module is not found"
  print "Please run \"source pydaq_setup.bash\", or update your env path"
  print "ERROR:",sys.exc_info()[0]
  sys.exit(1)

import pycdb
import traceback
from sequenceLoad import SequenceLoad
from cafunctions import caget, caput
from seqDefs     import *
#from mecShutter import ShutterInit, ShutterArm
import daqlog



class MccBurst:
  def __init__(self, bSimMode):
    self.bSimMode        = bSimMode
    self.bMccBurstRunning    = False
    self.dictBeamToBurstRate = { 120: 0, 30: 1, 10: 2, 5: 3, 1: 4, 0.5: 5, 0:0, 60:0 }

  def isLegalBeamRate(self, fRate):
    return self.dictBeamToBurstRate.has_key(fRate)

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

  def mccBurstSetNumShot(self, iNumShots, fBurstRate):
    if self.bSimMode:
      return False
    print "Settings Mcc Burst Shot %d rate %f (%d)" % (iNumShots, fBurstRate, self.dictBeamToBurstRate[fBurstRate])
    caput(pvMccBurstNumShot, iNumShots)  # Set # of bursts
    self.mccBurstSetRate(fBurstRate)
    return 0

  def mccBurstSetRate(self, fBurstRate):
    if self.bSimMode:
      return True
    if caget(pvBeamOwner) != caget(pvHutchId):
      print "Settings Test Burst Rate %f (%d)" % (fBurstRate, self.dictBeamToBurstRate[fBurstRate])
      caput(pvMccTestBurstDep   , 0)
      caput(pvMccTestBurstRate  , self.dictBeamToBurstRate[fBurstRate])
    else:
      print "Settings Mcc Burst Rate %f (%d)" % (fBurstRate, self.dictBeamToBurstRate[fBurstRate])
      caput(pvMccBurstRate   , self.dictBeamToBurstRate[fBurstRate])
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
  def __init__(self, iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode,readout_time=0.0, use_readout_grps=True, fast_newton=False):
    self.iNumShot   = iNumShot
    self.fExpDelay  = fExpDelay
    self.fPostDelay = fPostDelay
    self.fBurstRate = fBurstRate
    self.bSimMode     = (bSimMode or bShutterMode)  # shutter mode use the same sequence as sim mode
    self.bShutterMode = bShutterMode
    self.readout_time = readout_time  # user-defined camera readout time
    self.use_readout_grps = use_readout_grps
    self.fast_newton = fast_newton

    self.daq              = None
    self.bBeginCycle      = False
    self.iNumTotalImage   = 0
    self.mccBurst         = MccBurst(self.bSimMode)

    self.daq_host         = os.popen("hostname").read().strip()
    print "Host: %s" % self.daq_host

    self.daq_platform      = 0 # 0 for MEC, 1 for XCS
    self.iSlowCamOpenDelay = iOpenDelay # unit: 120Hz

    self.eventCameraOpan       = seqEventMin + 5
    self.eventShutterOpenClose = seqEventMin + 0
    self.eventDaqReadout       = seqEventMin + 6
    if not self.bShutterMode:
      self.eventShutterOpenClose = 0

  def getEventNum(self):
    print "Waiting for event"
    #eventnum = self.daq.eventnum()
    #print "Waiting for event", "EVENT:", eventnum
    #return eventnum


    #while True:
    #  eventnum = self.daq.eventnum()
    #  if eventnum < 0xFFFFFFFF and eventnum >= 0:
    #    return eventnum
    #  else :
    #    print "ILLEGAL EVENT NUM",eventnum,"....TRYING AGAIN"


  def setCameraControlSequence(self):
    print "Settings camera control sequence...\n"

    iBurstInterval    = int(120 / self.fBurstRate)
    iInitDelay        = (iBurstInterval - self.iSlowCamOpenDelay) % iBurstInterval
    if self.bSimMode:
      iShutterOpenDelay = 2 # for both single shot and burst mode
      iInitToShutter    = self.iSlowCamOpenDelay - iShutterOpenDelay

      event_codes      = [self.eventCameraOpan, self.eventShutterOpenClose, self.eventDaqReadout]
      beam_delays      = [iInitDelay          , iInitToShutter            , iShutterOpenDelay   ]

      if self.iNumShot > 1:
        event_codes   += [self.eventDaqReadout] * (self.iNumShot-2)
        beam_delays   += [iBurstInterval      ] * (self.iNumShot-2)

        event_codes   += [self.eventShutterOpenClose, self.eventDaqReadout]
        beam_delays   += [iBurstInterval-1          , 1                   ]

      burst_requests     = [0]* len(event_codes)
      fiducial_delays    = [0]* len(event_codes)
    else:
      iInitToBeamReq     = self.iSlowCamOpenDelay - 1
      event_codes        = [self.eventCameraOpan, 0, self.eventDaqReadout]
      beam_delays        = [iInitDelay       , iInitToBeamReq,   (self.iNumShot-1)*iBurstInterval+1]
      burst_requests     = [0                , self.iNumShot]

      burst_requests    += [0]* ( len(event_codes) - len(burst_requests) )
      fiducial_delays    = [0]* len(event_codes)

    seq = SequenceLoad(event_codes, beam_delays, fiducial_delays, burst_requests)
    seq.load(verbose=False)
    return 0

  def init(self, controls = None, bDaqBegin = True):
    while True:
      fBeamFullRate = float(caget(pvBeamRate));
      if fBeamFullRate == 0.5 or float(int(fBeamFullRate)) == fBeamFullRate:
        break

    if not self.bSimMode:
      if not (self.mccBurst.isLegalBeamRate(fBeamFullRate)):
        print "!!! Beam rate %g is not stable, please wait for beam to stablize and run the script again" % (fBeamFullRate)
        return 1
      self.mccBurst.mccBurstCheckInit()

    if self.fBurstRate == -1:
      self.fBurstRate = fBeamFullRate

    if not (self.fBurstRate in dictRateToSyncMarker):
      print "!!! Burst rate %g not supported" % (self.fBurstRate)
      return 1

    caput(pvPlayMode         , 0) # PlayMode = Once
    caput(pvMccSeqSyncMarker , dictRateToSyncMarker[self.fBurstRate]) 
    caput(pvMccSeqBeamRequest, 0) # Set seuqencer rate to be 120Hz (TS4|TS1)

    caget(pvMccSeqSyncMarker) # caget bug: need to get twice to have latest value
    print "\n## Beam rate = %g HZ, Sync marker = %g HZ" % (fBeamFullRate, dictSyncMarkerToRate[int(caget(pvMccSeqSyncMarker,bGetNumEnum=True))])

    if not self.bSimMode:
      if caget(pvBeamOwner) != caget(pvHutchId):
        if self.fBurstRate == 60:
          print "!!! Test Burst rate %g is not supported by MCC" % (self.fBurstRate)
          return 1
        self.mccBurst.mccBurstSetRate(self.fBurstRate)
      elif self.fBurstRate == fBeamFullRate:
        self.mccBurst.mccBurstSetRate(0)
      elif self.fBurstRate < fBeamFullRate:
        if self.fBurstRate == 60:
          print "!!! Burst rate %g is not supported by MCC" % (self.fBurstRate)
          return 1
        self.mccBurst.mccBurstSetRate(self.fBurstRate)
      else:
        print "!!! Burst rate %g is faster than Beam rate %g" % (self.fBurstRate, fBeamFullRate)
        return 1

    print "## Multiple shot: %d" % (self.iNumShot)

    # Exposure Time =
    #     camear open (clean CCD) delay ( self.iSlowCamOpenDelay: 0 for PI, 5*120Hz for FLI)
    #     + manual sleep (fExpDelay)
    #     + exposure Time ((self.iNumShot / self.fBurstRate) second)
    #   = 0.0 + max(1, self.iSlowCamOpenDelay)/120.0 + (self.iNumShot / self.fBurstRate) + fExpDelay  second
    self.fExposureTime = 0.0 + self.iSlowCamOpenDelay/120.0 + self.fExpDelay + self.iNumShot / float(self.fBurstRate)

    print "CREATE DAQ CONTROL OBJECT"
    self.daq = pydaq.Control(self.daq_host, self.daq_platform)
    try:
      print "daq connect...",
      sys.stdout.flush()
      self.daq.connect() # get dbpath and key from DAQ
      print " done."
    except:
      print "!! daq.connect() failed"
      print "!! Possibly because 1. DAQ devices has NOT been allocated"
      print "!!               or 2. You are running DAQ control GUI in remote machines"
      print "!! Please check 1. DAQ is in good state and re-select the devices"
      print "!!              2. If the restart script actually runs DAQ in another machine"
      print "ERROR",sys.exc_info()[0]
      return 1

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

    print "CONFIGURE DAQ"
    if controls is None:
      iFail = self.configure(controls=[])
    else:
      iFail = self.configure(controls=controls)
    if iFail != 0:
      print "daq disconnect...",
      sys.stdout.flush()
      self.daq.disconnect()
      print " done."
      return 3

    if self.bShutterMode:
     if ShutterInit(self.iNumShot) != 0:
       print "Shutter Init Failed"
       return 4

    print "SET CAMERA CONTROL SEQUENCE"
    self.setCameraControlSequence()

    self.iNumTotalImage = 0

    print "## Please make sure"
    if not self.bSimMode:
      print "##   - MCC has switched to Burst Mode,"
    print "##   - Andor/Princeton camera is selected (if you need it),"
    print "##   - chiller is running and the cooling temperature is set properly."

    if bDaqBegin:
      # cpo changed this line
      self.beginCycle(controls)
    return 0

  def configure(self, controls = None):
    cdb = pycdb.Db(self.daq.dbpath())
    newkey = cdb.get_key(self.alias)
    print "db path = %s  key = 0x%x" % (self.daq.dbpath(), self.daq.dbkey())

    partition = self.daq.partition()
    lAllocatedPrinceton = []
    lAllocatedFli       = []
    lAllocatedAndor     = []
    lAllocatedPimax     = []
    for daqNode in partition['nodes']:
      # example of daqNode: {'record': True, 'phy': 256L, 'id': 'NoDetector-0|Evr-0', 'readout': True}
      phy = daqNode['phy']
      devId = ((phy & 0x0000FF00) >> 8)
      devNo = (phy & 0x000000FF)
      if devId == 6: # Princeton
        lAllocatedPrinceton.append((phy,devNo))
      elif devId == 23:
        lAllocatedFli.append((phy,devNo))
      elif (devId == 25) or (devId == 38):
        lAllocatedAndor.append((phy,devNo))
      elif devId == 32:
        lAllocatedPimax.append((phy,devNo))

    fMaxReadoutTime = 0
    lSpeedTable     = [ 0.1, 1, 0, 0, 1, 2 ]
    for cam_index,(phy,iCamera) in enumerate(lAllocatedPrinceton):
      lXtcPrinceton = cdb.get(key=newkey,src=phy)
      print "Princeton %d (detector id: 0x%x)" % (iCamera, phy)
      if len(lXtcPrinceton) != 1:
        print "!! Error: Princeton %d should only have one config, but found %d configs" % (iCamera, len(lXtcPrinceton))
        continue
      xtc              = lXtcPrinceton[0]
      configPrinceton  = xtc.get()
      fOrgExposureTime = float(configPrinceton['exposureTime'])
      width            = configPrinceton['width']
      height           = configPrinceton['height']
      speed            = configPrinceton['readoutSpeedIndex']
      code             = configPrinceton['exposureEventCode']
      kineticHeight    = configPrinceton['kineticHeight']

      configPrinceton['exposureEventCode'] = self.eventCameraOpan

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
        configPrinceton['exposureTime']     = self.fExposureTime + (cam_index * self.readout_time)
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
          self.iNumShot = iNumKineticShot

      if self.use_readout_grps:
        configPrinceton['numDelayShots'] = 1
      else:
        configPrinceton['numDelayShots'] = self.iNumShot
      print "  Number of Delayed Shots: [%d]: %d" % (iCamera, configPrinceton['numDelayShots'])

      xtc.set(configPrinceton)      
      cdb.set(xtc = xtc, alias = self.alias)

    lSpeedTable     = [ 0.2, 1 ]
    for cam_index,(phy,iCamera) in enumerate(lAllocatedFli):
      lXtcFli = cdb.get(key=newkey,src=phy)
      print "Fli %d (detector id: 0x%x)" % (iCamera, phy)
      if len(lXtcFli) != 1:
        print "!! Error: Fli %d should only have one config, but found %d configs" % (iCamera, len(lXtcFli))
        continue
      xtc              = lXtcFli[0]
      configFli        = xtc.get()
      fOrgExposureTime = float(configFli['exposureTime'])
      width            = configFli['width']
      height           = configFli['height']
      speed            = configFli['readoutSpeedIndex']
      code             = configFli['exposureEventCode']

      configFli['exposureEventCode'] = self.eventCameraOpan

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
      configFli['exposureTime']     = self.fExposureTime + (cam_index * self.readout_time)
      print "  Exposure time (New)      [%d]: %.3f s" % (iCamera, configFli['exposureTime'])

      if self.use_readout_grps:
        configFli['numDelayShots'] = 1
      else:
        configFli['numDelayShots'] = self.iNumShot
      print "  Number of Delayed Shots: [%d]: %d" % (iCamera, configFli['numDelayShots'])

      xtc.set(configFli)
      cdb.set(xtc = xtc, alias = self.alias)

    lSpeedTable     = [ 1, 0.6, 0.2, 0.01 ]
    for cam_index,(phy,iCamera) in enumerate(lAllocatedAndor):
      lXtcAndor = cdb.get(key=newkey,src=phy)
      print "Andor %d (detector id: 0x%x)" % (iCamera, phy)
      if len(lXtcAndor) != 1:
        print "!! Error: Andor %d should only have one config, but found %d configs" % (iCamera, len(lXtcAndor))
        continue
      xtc              = lXtcAndor[0]
      configAndor      = xtc.get()
      fOrgExposureTime = float(configAndor['exposureTime'])
      width            = configAndor['width']
      height           = configAndor['height']
      speed            = configAndor['readoutSpeedIndex']
      code             = configAndor['exposureEventCode']

      # check if the camera is in external trigger moded
      if self.fast_newton and configAndor['numDelayShots'] == 0:
        print "Andor %d (detector id: 0x%x) is in externally triggered mode - skipping config!" % (iCamera, phy)
        continue

      configAndor['exposureEventCode'] = self.eventCameraOpan

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
      configAndor['exposureTime']     = self.fExposureTime + (cam_index * self.readout_time)
      print "  Exposure time (New)      [%d]: %.3f s" % (iCamera, configAndor['exposureTime'])

      if self.use_readout_grps:
        configAndor['numDelayShots'] = 1
      else:
        configAndor['numDelayShots'] = self.iNumShot
      print "  Number of Delayed Shots: [%d]: %d" % (iCamera, configAndor['numDelayShots'])

      xtc.set(configAndor)
      cdb.set(xtc = xtc, alias = self.alias)

    for cam_index,(phy,iCamera) in enumerate(lAllocatedPimax):
      lXtcPimax = cdb.get(key=newkey,src=phy)
      print "Pimax %d (detector id: 0x%x)" % (iCamera, phy)
      if len(lXtcPimax) != 1:
        print "!! Error: Pimax %d should only have one config, but found %d configs" % (iCamera, len(lXtcPimax))
        continue
      xtc              = lXtcPimax[0]
      configPimax      = xtc.get()
      fOrgExposureTime = float(configPimax['exposureTime'])
      width            = configPimax['width']
      height           = configPimax['height']
      speed            = configPimax['readoutSpeed']
      code             = configPimax['exposureEventCode']

      configPimax['exposureEventCode'] = self.eventCameraOpan

      fReadoutTime = 1 / speed
      if fReadoutTime > fMaxReadoutTime:
        fMaxReadoutTime = fReadoutTime

      print "  W %d H %d speed %d code %d readout %.3f" % (width, height, speed, configPimax['exposureEventCode'], fReadoutTime)
      print "  Exposure time (Original) [%d]: %.3f s" % (iCamera, fOrgExposureTime)
      configPimax['exposureTime']     = self.fExposureTime + (cam_index * self.readout_time)
      print "  Exposure time (New)      [%d]: %.3f s" % (iCamera, configPimax['exposureTime'])

      if self.use_readout_grps:
        configPimax['numIntegrationShots'] = 1
      else:
        configPimax['numIntegrationShots'] = self.iNumShot
      print "  Number of Integration Shots: [%d]: %d" % (iCamera, configPimax['numIntegrationShots'])

      xtc.set(configPimax)
      cdb.set(xtc = xtc, alias = self.alias)
      
    cdb.commit()
    newkey = cdb.get_key(self.alias)
    cdb.unlock()

    print "setting exposure time to %.2f s" % (self.fExposureTime)

    #
    #    self.daq.configure(events=options.events,
    #                  controls=[('EXAMPLEPV1',0),('EXAMPLEPV2',0)],
    #                  monitors=[('BEAM:LCLS:ELEC:Q',options.qbeam,1.)])
    #
    #    self.daq.configure(record=do_record,
    #                  events=options.events,
    #                  controls=[('EXAMPLEPV1',0),('EXAMPLEPV2',0)])
    print "CONTROLS LIST:",controls
    print "daq configure...",
    sys.stdout.flush()
    # cpo changed this line
    #print "()()()\n",controls
    if controls is None :
      self.daq.configure(key=newkey, events=0, controls=[])
    else :
      self.daq.configure(key=newkey, events=0, controls=controls)
    print " done."

    return 0

  def getMoreImages(self, iNumImage, x_motor=None, token_x=None, destination=None, delayT=None):
    for iImage in xrange(iNumImage):
      if (not self.bShutterMode) and self.mccBurst.mccBurstCheckStatusChange():
        print "Burst Mode status changed"
        break

      timeBeforeImage = time.time()

      print "# Image %d/%d (%d Shots) [total images: %d]" % (1+iImage, iNumImage, self.iNumShot, self.iNumTotalImage)
      iEventStart = self.getEventNum()

      timeAfterImageBegin = time.time()

      if x_motor is not None:
        # should be close to the 1st event
        print "Scan on X starts now from %s mm to %s mm" % (token_x, destination)
        print "DAQ starts recording 1st event %s s after motor started." % delayT
        print "Time right before moving motor ", datetime.datetime.now().time()
        x_motor.mv( destination )           
        
        # user specficy delay in distance
        time.sleep(delayT)
        print "Motor position before first DAQ event:" , float( caget("MEC:USR:MMS:17.RBV") ), " mm"

      caput(pvPlayCtrl, 1) # PlayCtrl = Play


      timeAfterPlay = time.time()
      print "###################### Event sequence played at:", timeAfterPlay

      time.sleep(0.02)
      while True:
        if caget(pvPlayStat).find("Stopped") != -1:
          break
        if self.bShutterMode:
          iSeqStep = int(caget(pvPlayCurStep))
          print "Sequence step: %d\r" % (iSeqStep),
          sys.stdout.flush()
        time.sleep(0.05)

      timeBeforeBurst = time.time()

      if not self.bShutterMode and caget(pvBeamOwner) == caget(pvHutchId):
        time.sleep(0.02)
        while True:
          if self.mccBurst.mccBurstIsComplete():
            break
          iNumBurstCount = self.mccBurst.mccBurstCount()
          print "Burst count: %d / %d\r" % (iNumBurstCount, self.iNumShot),
          sys.stdout.flush()
          time.sleep(0.05)

      timeAfterBurstComplete = time.time()

      print "Waiting for device readout... "
      if self.fPostDelay > 0:
        print "Sleeping for %.1f seconds... " % (self.fPostDelay),
        sys.stdout.flush()
        time.sleep(self.fPostDelay) # post delay: wait for DAQ to really ends if data valume is too large
        print "done."

      print "Waiting for DAQ event: %d" % self.iNumShot
      time.sleep(1)

#      while True:
#        print "GOING TO READOUT EVENTNUM"
#        eventnum = self.getEventNum()
#        if eventnum >= iEventStart + self.iNumShot:
      #    if x_motor is not None:
      #      print "Time after DAQ ", datetime.datetime.time(datetime.datetime.now())
      #      print "Motor position after last DAQ event:" , float( caget("MEC:USR:MMS:17.RBV") ), " mm"
#          break
#        print "DAQ event: %d / %d\r" % (eventnum, iEventStart + self.iNumShot),
#        sys.stdout.flush()
#        time.sleep(0.05)
#      print "                           \r",

      if self.bShutterMode:
        if ShutterArm(self.iNumShot) != 0:
          print "\nShutter Arm Failed"
          break

      timeEndImage = time.time()
      print "time (sec): Image %.2f Begin %.2f SeqPvSet %.2f PlaySeq %.2f Burst %.2f End %.2f" %\
       (timeEndImage-timeBeforeImage,  \
        timeAfterImageBegin - timeBeforeImage, timeAfterPlay - timeAfterImageBegin, \
        timeBeforeBurst - timeAfterPlay, timeAfterBurstComplete - timeBeforeBurst,  \
        timeEndImage-timeAfterBurstComplete )

      self.iNumTotalImage += 1
    # end: for iImage in xrange(iNumImage)

  def numTotalImage(self):
    return self.iNumTotalImage

  # cpo changed this line
  def beginCycle(self,controls = None, events=0):
    print "BEGINCYCLE"
    if self.daq == None:
      return
    if self.bBeginCycle:
      return

    try:
      print "daq begin...",
      sys.stdout.flush()
      # cpo changed this line
      print '---', controls
      if controls is None :
        self.daq.begin(events=events,controls=[])
      else:
        self.daq.begin(events=events,controls=controls) # run until we call daq.stop()
      #self.daq.begin(events=0) # run until we call daq.stop()
      print " done."
    except :      
      print "daq.begin() timeout"
      print "ERROR:",sys.exc_info()[0]
      return

    self.bBeginCycle = True
    time.sleep(0.5) # wait for EVR to enable. Not needed for new DAQ release

  def endCycle(self):
    print "ENDCYCLE"
    if self.daq == None:
      return
    if not self.bBeginCycle:
      return

    try:
      print "daq stop...",
      sys.stdout.flush()
      self.daq.stop()
      print " done."
    except:
      print "daq.stop() timeout"
      print "ERROR:",sys.exc_info()[0]

    print self.getEventNum()

    #try:
    #  print "daq end... waiting for daq to finish...",
    #  sys.stdout.flush()
    #  self.daq.end()
    #  print " done."
    #except:
    #  print " done (already stopped)."
    #  print "ERROR:",sys.exc_info()[0]
    #  return

    self.bBeginCycle = False

  def nextCycle(self,controls = None):
    print "NEXTCYCLE"
    if self.daq == None:
      return
    self.endCycle()
    # cpo changed this line
    self.beginCycle(controls)

  def deinit(self):
    if self.daq == None:
      return

    self.endCycle()

    try:
      print "daq disconnect...",
      sys.stdout.flush()
      self.daq.disconnect()
      print " done."
    except:
      print "daq.disconnect() timeout"
      print "ERROR:",sys.exc_info()[0]
      return

class PrincetonMultipleShotInteractive:
  def __init__(self):
    pass

  def run(self, iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode,readout_time=0, use_readout_grp=True, fast_newton=False):
    princetonDaq = PrincetonDaqMultipleShot(iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode,readout_time, use_readout_grp, fast_newton)
    iFail = princetonDaq.init(bDaqBegin=False)
    #iFail = princetonDaq.init(controls=[("A",1),("B",2)],bDaqBegin=False)
    if iFail != 0:
      return 1

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
        ## hack around bad state after runs
        princetonDaq.getEventNum()
        time.sleep(0.5)
        # end hack
        princetonDaq.beginCycle([])
        princetonDaq.getMoreImages(iMoreImage)
        princetonDaq.endCycle()
        # go to next loop to get more Images
      #end of while True:

      daq = princetonDaq.daq
      print "# (If Record Run is ON) Experiment %d Run %d (%d images)" % (daq.experiment(),daq.runnumber(), princetonDaq.numTotalImage())
      princetonDaq.deinit()
      time.sleep(0.5)
    except:
      print "\n!!! Script exits abnormally (may be interrupted by user)"
      print "ERROR:",sys.exc_info()[0]
      daq = princetonDaq.daq
      princetonDaq.deinit()
      time.sleep(0.5)

    return 0

def showUsage():
  sFnCmd = os.path.basename( sys.argv[0] )
  print(
    "Usage: %s [-h | --help] [-m|--mshot <NumShots>] [-e|--expdelay <Delay>] [-p|--post <postDealy>]\n"
    "    [-o|--opendelay <Tick>] [-r|--rate <rate>] [-s|--shutter] [--readout <readout_time>]" % sFnCmd )
  print( "    -h | --help                   Show usage information" )
  print( "    -m | --mshot     <NumShots>   Run multiple shot integration of <NumShots>. Default: 1" )
  print( "    -e | --expdelay  <Delay>      Set exposure time delay to <Delay> second. Default: 0" )
  print( "    -p | --post      <PostDelay>  Set post delay to <Delay> second. Default: 0" )
  print( "    -o | --opendelay <Tick>       Set camera open delay to <Tick>/120 seconds. Default: 5")
  print( "    -r | --rate      <Rate>       Set burst rate to <rate>. Default: use Beam Rate" )
  print( "    -s | --shutter                Run in shutter mode. No Mcc Burst is called.")
  print( "         --sim                    Run in simulation mode: No Mcc burst, and no shutter.")
  print( "    --readout <readout_time>      Set readout-time per camera, if readout in series.")
  print( "    --nogroups                    Run without readout groups (legacy only).")  
  print( "    --fast-newton                 Allow Newton camera to run in fast full-vertical binning mode.")
  print( " ver 1.11")

def main():
  (llsOptions, lsRemainder) = getopt.getopt(sys.argv[1:], \
      'hm:e:r:p:o:s', \
      ['help', 'mshot=', 'expdelay=', 'rate=', 'post=', 'opendelay=', 'shutter', 'sim','readout=', 'nogroups', 'fast-newton'] )

  iNumShot   = 1
  fExpDelay  = 0
  fPostDelay = 0
  iOpenDelay = 5

  fBurstRate   = -1
  bSimMode     = False
  bShutterMode = False
  bReadoutGroups = True
  bFastNewton = False
  readout_time = 0.0
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
    elif sOpt == '--readout' :
      readout_time = float(sArg)
    elif sOpt == '--nogroups' :
      bReadoutGroups = False
    elif sOpt == '--fast-newton':
      bFastNewton = True


  print "Command line: NumShot %d ExpDelay %g PostDelay %g OpenDelay %d Rate %g SimMode %s Shutter %s readout-time %s" % \
    (iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode,readout_time)
  try:
    PrincetonMultipleShotInteractive().run(iNumShot, fExpDelay, fPostDelay, iOpenDelay, fBurstRate, bSimMode, bShutterMode, readout_time, bReadoutGroups, bFastNewton)
  except:
    traceback.print_exc(file=sys.stdout)
    print "ERROR:",sys.exc_info()[0]
  return

if __name__ == '__main__':
  status = main()
  sys.exit(status)
