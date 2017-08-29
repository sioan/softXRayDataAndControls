#! /bin/env python
import sys, os, errno
from PyQt4 import QtCore
import pyca
from Pv import Pv
import time
import threading


MOTION_SCREENS_PATH = '/reg/neh/home1/paiser/working/ioc/common/xip_pp/current/pyscripts/src'
PP_SIOC_STARTUP = '/reg/d/iocCommon/sioc/ioc-sxr-trigger-ims/startup.cmd'
EPICS_BASE = '/reg/g/pcds/package/epics/3.14/modules/pcds_motion/R2.3.4'
EVR_SCREENS_PATH = './'

def caput(pvname, value, timeout=1.0):
    try:
        pv = Pv(pvname)
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        pv.put(value, timeout)
        pv.disconnect()
        print 'caput', pvname, value
    except pyca.pyexc, e:
        print 'pyca exception: %s' %(e)
    except pyca.caexc, e:
        print 'channel access exception: %s' %(e)
        
def caget(pvname, timeout=1.0):
    try:
        pv = Pv(pvname)
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        v = pv.value
        pv.disconnect()
        print 'caget', pvname, v
        return v
    except pyca.pyexc, e:
        print 'pyca exception: %s' %(e)
        return []
    except pyca.caexc, e:
        print 'channel access exception: %s' %(e)
        return []
 
    def PPEVRinit(self):
        '''Returns a dictionary of EVR pvs and values to be initialized'''
        if not self.readconfig_done or self.sEvrPv == None:
            print '  ERROR: Error reading config file.'
            return None
        # EVR PV's        
        self.EVR['Trg']  = ('%s:CTRL.DG%dE' % (self.sEvrPv, self.EVRchannel), 1)
        self.EVR['Pol']  = ('%s:CTRL.DG%dP' % (self.sEvrPv, self.EVRchannel), 1)
        self.EVR['Wdt']  = ('%s:CTRL.DG%dW' % (self.sEvrPv, self.EVRchannel), 2000)
        self.EVR['Psc']  = ('%s:CTRL.DG%dC' % (self.sEvrPv, self.EVRchannel), 119)
        self.EVR['Dly']  = ('%s:CTRL.DG%dD' % (self.sEvrPv, self.EVRchannel), 0)
        
        EVRpvvals = {}
        for pvval in self.EVR.values():
            EVRpvvals[pvval[0]] = pvval[1] 
        if EVRpvvals == {}:
            return None
        
        return EVRpvvals
        
    
    def PPEVRdelay(self, pp_mode=None):
        '''Returns a tupple EVR Pv and mode correspondent at 
           the EVR correct delay'''
        if not self.EVR:
            print '  ERROR: PPEVRInit must be called first.'
            return None                    
        if not self.readconfig_done:
            print '  ERROR: Error reading EVR delay in config file.'
            return None        
        if pp_mode == 'RUN_MODE1' or pp_mode == 'RUN_MODE2':
            evrdelay  = int(self.sEVS)
        elif pp_mode == 'RUN_MODE3':
            evrdelay  = int(self.sEVB)
        else:
            return None
        return self.EVR['Dly'][0], evrdelay
    
class DoneMoving(Pv):
    def __init__(self, name):
        Pv.__init__(self, name)
        self.monitor_cb = self.monitor_handler
        self.__sem = threading.Event()
        self.__moving = False
        timeout = 1.0
        self.connect(timeout)
        evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM
        self.monitor(evtmask, ctrl=False)

    def wait_for_done(self, timeout):
        self.__sem.wait(timeout)
        if self.__sem.isSet():
            self.__sem.clear()
        else:
            raise Exception, 'Timedout (%d sec) while waiting for stop: %s' %\
                             (timeout, self.name)

    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.value == 1:
                    if self.__moving == True:
                        self.__sem.set()
                    self.__moving = False
                else:
                    self.__moving = True
            else:
                print "%-30s " % (self.name), exception
        except Exception, e:
            print e

class cfginfo():
    def __init__(self):
        self.dict = {}
  
    def read(self, name):
        try:
            cfg = open(name).readlines()
            for line in cfg:
                line = line.lstrip()
                token = line.split()
                if len(token) == 2:
                    self.dict[token[0]] = token[1]
                else:
                    self.dict[token[0]] = token[1:]
            return True
        except:
            return False
  
    def add(self, attr, val):
        self.dict[attr] = val
  
    def __getattr__(self, name):
        if self.dict.has_key(name):
            return self.dict[name]
        else:
            raise AttributeError, name
        
class CAComm(QtCore.QThread):
    def __init__(self, lock, parent):
        super(CAComm, self).__init__(parent)
        self.lock      = lock
        self.mutex     = QtCore.QMutex()
        self.parent    = parent
        self.stopped   = False
        self.completed = False
        self.writePv   = False
        self.readPv    = False
        self.setAlign   = False
        self.setOpen   = False
        self.setAuto   = False
        self.setClose  = False
        self.updatePv  = False
        self.pv        = None
        self.val       = None
        
    def isStopped(self):
        try:
            self.mutex.lock()
            return self.stopped
        finally:
            self.mutex.unlock()

    def stop(self):
        try:
            self.mutex.lock()
            self.stopped = True
        finally:
            self.mutex.unlock()
        
    def run(self):
        pyca.attach_context()
        if self.writePv:
            self.writePv = False
            #print 'here', repr(self.pv), repr(self.val)
            caput(self.pv, self.val)
            #self.emit(QtCore.SIGNAL("_caputdone"))
        elif self.readPv:
            print 'run readPv here'
            self.readPv = False
            val = str(caget(self.pv))
            ##ans = self.pv + ' ' + val
            self.pvval = self.pv + ' ' + val
            #self.emit(QtCore.SIGNAL("_cagetdone"))
        elif self.setAlign:
            self.setAlign = False
            self._ims_align()
        elif self.setAuto:
            self.setAuto = False
            self._ims_setauto()
        elif self.setOpen:
            self.setOpen = False
            #self._ims_openclose('Open')
            self._ims_fastopenclose('Open')
        elif self.setClose:
            self.setClose = False
            #self._ims_openclose('Close')
            self._ims_fastopenclose('Close')
        elif self.updatePv:
            self.updatePv = False
            res = self.updatePv()
            self.emit(QtCore.SIGNAL("_update(bool)"), res)
        else:
            pass
        
    def set_pv(self, pv, val):
        pvvals = {}
        pvvals['SET_EC']    = {}; pvvals['SET_EC']['0']    = '0'; pvvals['SET_EC']['1']    = '1'
        pvvals['RESET_PG']  = {}; pvvals['RESET_PG']['0']  =  0 ; pvvals['RESET_PG']['1']  =  1
        pvvals['RUN_MODE1'] = {}; pvvals['RUN_MODE1']['0'] =  0 ; pvvals['RUN_MODE1']['1'] =  1
        pvvals['RUN_MODE2'] = {}; pvvals['RUN_MODE2']['0'] =  0 ; pvvals['RUN_MODE2']['1'] =  1
        pvvals['RUN_MODE3'] = {}; pvvals['RUN_MODE3']['0'] =  0 ; pvvals['RUN_MODE3']['1'] =  1
        
        
        if 'XPP:TST:MMS:01' in pv:
            pvkey = pv.split('XPP:TST:MMS:01:')[1]
            self.pv = pv
            self.val = pvvals[pvkey][val]
        else:
            try:
                v = float(val)
            except ValueError:
                try:
                    v = str(val)
                except ValueError:
                    print '!! set_pv: value error'
                    return False
            self.pv = pv
            self.val = v
        self.writePv = True

    def get_pv(self, pv):
        self.pv = pv
        self.readPV = True

    def set_align(self):
        self.setAlign = True

    def set_auto(self):
        self.setAuto = True
        
    def set_open(self):
        self.setOpen = True
        
    def set_close(self):
        self.setClose = True

    def set_update(self):
        self.updatePv = True
        
    def _ims_align(self):
        #align_offset = 76.25
        align_offset = 68.1328 + 11.25
        #align_offset = 658.1328 + 11.25
        
        pvname = '%s.HOMF' % self.parent.sPpmPv
        caput(pvname, 1)

        dmovpv = DoneMoving(self.parent.sPpmPv + '.DMOV')
        pyca.pend_io(1.0)
        dmovpv.wait_for_done(20)        

        # tweek -76.25
        pvname = '%s.TWV' % self.parent.sPpmPv
        caput(pvname, align_offset)
        time.sleep(1.5)
        pvname = '%s.TWR' % self.parent.sPpmPv
        caput(pvname, 1)

        dmovpv = DoneMoving(self.parent.sPpmPv + '.DMOV')
        pyca.pend_io(1.0)
        dmovpv.wait_for_done(20)        

        # Clear all errors and reset counter values
        pvname = '%s:RESET_PG' % self.parent.sPpmPv
        caput(pvname, 1)
        pvname = '%s:SET_C1' % self.parent.sPpmPv
        caput(pvname, 0)
        pvname = '%s:SET_C2' % self.parent.sPpmPv
        caput(pvname, 0)
        time.sleep(2)
        # Set default parameters for 30Hz
        pvname = '%s:SETUP_30HZ' % self.parent.sPpmPv
        caput(pvname, 1)
        self.emit(QtCore.SIGNAL("_onalign"))


    def _ims_fastopenclose(self, position):
        if position == 'Open':
            pvname = '%s:S_OPEN' % self.parent.sPpmPv
            val = self.parent.OpenPos
            sig = "_onOpen"
        elif position == 'Close':
            pvname = '%s:S_CLOSE' % self.parent.sPpmPv
            val = self.parent.ClosePos
            sig = "_onClose"
        else:
            return False
        caput(pvname, val)
        self.emit(QtCore.SIGNAL(sig))
        return True

    
    def _ims_setauto(self):
        self._ims_fastopenclose('Close')
        self.emit(QtCore.SIGNAL('_onAuto'))
        
    def _ims_openclose(self, position):
        if position == 'Open':
            self.emit(QtCore.SIGNAL("_onOpening"))
            pos_offset = 65.0
        elif position == 'Close':
            self.emit(QtCore.SIGNAL("_onClosing"))
            pos_offset = 65.0 + 90.00
        else:
            return False
        pvname = '%s.HOMF' % self.parent.sPpmPv
        caput(pvname, 1)
#        time.sleep(6)
        dmovpv = DoneMoving(self.parent.sPpmPv + '.DMOV')
        pyca.pend_io(1.0)
        dmovpv.wait_for_done(20)        

        # tweek -76.25
        pvname = '%s.TWV' % self.parent.sPpmPv
        caput(pvname, pos_offset)
        time.sleep(1.5)
        pvname = '%s.TWR' % self.parent.sPpmPv
        caput(pvname, 1)
        #time.sleep(1.5)
        
        dmovpv = DoneMoving(self.parent.sPpmPv + '.DMOV')
        pyca.pend_io(1.0)
        dmovpv.wait_for_done(20)        
#        # Clear all errors and reset counter values
#        pvname = '%s:RESET_PG' % self.parent.sPpmPv
#        caput(pvname, 1)
#        time.sleep(2)
        # Set default parameters for 30Hz
        pvname = '%s:SETUP_30HZ' % self.parent.sPpmPv
        caput(pvname, 1)
        
        if position == 'Open':
            self.emit(QtCore.SIGNAL("_onOpen"))
        elif position == 'Close':
            self.emit(QtCore.SIGNAL("_onClose"))
        else:
            return False
        return True
    
    def updatePv(self):
        pass

'''
#-------------------------------------------- Examples in XPP/SXR/CXI/MECpython:
ppcfg = {}
ppcfg['Sequencer Pv']               = 'SXR:RXX:IOC:XX:EV'
ppcfg['Seq play mode Pv']           = 'IOC:IN20:EV01'
ppcfg['PP Rotation motor Pv']       = 'SXR:SB2:MMS:09'
ppcfg['PP Y translation Pv']        = 'SXR:SB2:MMS:21'
ppcfg['PP X translation Pv']        = 'SXR:SB2:MMS:08'
ppcfg['PP ioc name']                = 'ioc-sxr-trigger-ims'
ppcfg['PP ioc server name']         = 'ioc-sxr-mot1'
ppcfg['EVR Pv']                     = 'SXR:R42:EVR:01'
ppcfg['EVR Burst mode delay']       = '0'
ppcfg['EVR Single mode delay']      = '5100'
ppcfg['EVR trigger channel number'] = '2'
ppcfg['EDM PP motor screen script'] = 'ppm_gui.sh'
ppcfg['EVR screen script']          = 'evr_gui.sh'
ppcfg['instr']                      = 'sxr'
ppcfg['Configuration directory']    = './'
ppcfg['Current working directory']  = os.getcwd()
ppcfg['Alignment offset']           = 68.1328 + 11.25
TODO:
align_offset = 68.1328 + 11.25 in the code
#------------------------------------------------------------------------------
 
pp = PPicker(ppcfg)
Picker commands:

pp.start()
pp.stop()

pp.open()
pp.close()
pp.align()
pp.setcheckbounds(True)
pp.iocreset()

pp.setnshots(1)
pp.setfreq(120)
pp.setrepeat(1)
pp.setforever(False)



pp.pstatus('Volatil user message')
pp.setusesequencer(False)
pp.setevrdelay(5300)
pp.hide()
pp.show()
pp.quit()

#------------------------------------------------------------------------------ 
'''

class PPicker():    
    '''Pulse Picker Class'''
    def __init__(self, ppcfg, app=None, parent=None):
        self.cwd         = ppcfg['Current working directory']
        self.instr       = ppcfg['instr']
        self.cfgdir      = ppcfg['Configuration directory']
        self.ppcfg       = ppcfg
        self.parent      = parent
        self.ppCfgFname  = './pp%s.cfg' % ppcfg['instr']
        
        self.fail         = False
        self.running      = False
        self.C2_open      = 655 
        self.C2_close     = self.C2_open + 4096 # open + 90 deg        
        self.C2_delta     = 50 
        self.C2_delta180  = self.C2_delta + 8192 # symmetrical value at 180 deg
        
        # IMS default values for 30 Hz
        self.IMS_VM   =  5000000
        self.IMS_VI   =   100000
        self.IMS_A    = 30000000
        self.IMS_D    = 30000000
        self.OpenPos  = 2045
        self.ClosePos = 0
        
        self.sh_status = None
        
        self.modes = {}
        self.modes['Mode 1'] = 'Single shot'
        self.modes['Mode 2'] = 'Continuous pulse rate reduction'
        self.modes['Mode 3'] = 'Consecutive pulse'
        
        # GUI related vars:
        self.nshots   = None
        self.freq     = None
        self.forever  = None
        self.repeat   = None
        self.auto     = None
        self.sopen    = None
        self.sclose   = None
        self.evrdelay = None
        self.chkbounds= True
        self.sequencer= False

        # PV names:
        self.runPvname    = 'SE_L' # 0, 1, 2 or 3  = not running or mode n. running
        self.failUDPvname = 'UD' # 1 = out of bounds
        self.failLDPvname = 'LD' # 1 = out of bounds
        self.nshotsPvname = 'N' # Number of shots to count in IMS motor trg in
        # Sequencer
        self.seqcode1     =  84 # first trigger to start moving 
        self.seqcode2     =  85 # trigger code to DAQ and Picker
        self.repeatPvname = 'ECS_REPCNT_2' # repeat n times counter value
        self.plymodPvname = 'ECS_PLYMOD_2' # sequencer play mode 1,2,3
        self.plyctrPvname = 'ECS_PLYCTL_2' # sequencer play control
        self.lengthPvname = 'ECS_LEN_2'    # sequencer length number
#        self.eventcPvname = 'EC_2' # sequencer event code
#        self.beamdlPvname = 'BD_2' # sequencer beam tick
        self.eventcPvname = 'ECS_SEQ_2.A' # sequencer event code
        self.beamdlPvname = 'ECS_SEQ_2.B' # sequencer beam time
        self.tickdlPvname = 'ECS_SEQ_2.C' # sequencer beam tick        
        self.evcodechanged = True
        
        # EVR
        self.evrDlyPvname = 'D' # EVR delay value
        self.C2Pvname     = 'C2' # encoder readings
        
        self.curMode      = None # current mode running in the IMS motor
        # PV instances:
        self.runPv    = None
        self.ims_on   = False
        self.failUDPv = None
        self.failLDPv = None
        self.nshotsPv = None
        self.repeatPv = None
        self.plymodPv = None
        self.lengthPv = None
        self.evrDlyPv = None
        
        # config file related
        self.sSeqPv   = None # Sequencer PV base name
        self.sSeqDesc = None
        self.sPlyPv   = None # Sequencer play mode
        self.sPlyDesc = None
        self.sIOC     = None # IOC server name
        self.sIOCDesc = None
        self.sEvrPv   = None # EVR PV base name
        self.sEvrDesc = None
        self.sPpmPv   = None # IMS motor Picker PV base name 
        self.sPpmDesc = None
        self.sYtrPv   = None # IMS motor Y translation PV base name 
        self.sYtrDesc = None
        self.sXtrPv   = None # IMS motor X translation PV base name 
        self.sXtrDesc = None
        self.sSPP     = None # EDM screen location
        self.sSPPDesc = None
        self.sSEV     = None # EDM screen location
        self.sSEVDesc = None
        self.sEVB     = None # EVR burst mode delay
        self.sEVBDesc = None
        self.sEVS     = None # EVR single shot mode delay
        self.sEVSDesc = None
        # alignment related:
        self.alignDone = False
        self.c2       = None
        self.c1       = None
        self.apr_000  = 655
        self.apr_180  = 8704
        self.alg_000  = 0
        self.alg_180  = 8192
        
        # shell commands (EDM and xterm) 
        self.edm_ppm  = False
        self.edm_evr  = False
        self.srv_open = False
        self.aligned  = False
        
        # define ca thread:
        self.lock = QtCore.QReadWriteLock()
        self.ca   = CAComm(self.lock, self)

        self.readPVListFile()   # read pv list file and associate Pvs.

        # disable encoder
        cmd = '%s:%s' % (self.sPpmPv, 'SET_EE') ; val = 0
        self._caput(cmd, val)
        
        self._linkEPICSPV()   # Connect PVs and create monitors
        
        self.connect(self.ca, QtCore.SIGNAL("Homedone"),   self._onalign)
        self.connect(self.ca, QtCore.SIGNAL("_onOpening"), self._onOpening)
        self.connect(self.ca, QtCore.SIGNAL("_onOpen"),    self._onOpen)
        self.connect(self.ca, QtCore.SIGNAL("_onClosing"), self._onClosing)
        self.connect(self.ca, QtCore.SIGNAL("_onClose"),   self._onClose)
        self.connect(self.ca, QtCore.SIGNAL("_onAuto"),    self._onAuto)

        self.event = QtCore.QObject()
        self.connect(self.event, QtCore.SIGNAL("_statusLDFAIL"), self._statusLDFAIL)
        self.connect(self.event, QtCore.SIGNAL("_statusUDFAIL"), self._statusUDFAIL)
        self.connect(self.event, QtCore.SIGNAL("_statusRUN"),    self._statusRUN)
        self.connect(self.event, QtCore.SIGNAL("_onNshots"),     self._onNshots)
        self.connect(self.event, QtCore.SIGNAL("_onEVRdelay"),   self._onEVRdelay)

        # reset home speed and base speed:
        self._pr_log( 'Setup IMS home speed ---------------------')
        self._caput('%s.%s' % (self.sPpmPv, 'HVEL'), 400)
        self._caput('%s.%s' % (self.sPpmPv, 'HBAS'), 100)

        self._initEVR('Init')
        self._initSequencer()


    def start(self):
        badstatus = ['Open', 'Closed', None]
        if self.sh_status in badstatus:
            return self._pr_err('Invalid Position. Shutter must be in Auto')
            
        mode = self._check_mode()
        self.alignDone = False
        if not mode:
            self.emit(QtCore.SIGNAL("_set_led(QString)"), 'FAIL')
            self.emit(QtCore.SIGNAL("_pstatus(QString)"), 'Invalid Mode')
            return self._pr_err('Invalid Mode: %s' % mode)
        self._pr_log(mode + ' ' + self.modes[mode])
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'align')

        # program EVR
        if not self._initEVR(mode):
            return self._pr_err( 'Could not set EVR')

        self._pr_log( 'Start MCode Program --------------------')
        if not self._ims_set(mode):
            return self._pr_err( 'Could not set IMS motor')

        self._pr_log( 'Setup Sequencer ------------------------')
        if not self._set_sequencer(mode):
            return self._pr_err( 'Could not set Sequencer')
        
        # start Sequencer:
        if self.cB_sequencer.isChecked():
            self._pr_log( 'Starting Sequencer ---------------------')
            self._caput('%s:%s' % (self.sPlyPv, self.plyctrPvname), '1')
            
    def stop(self):
        if not self.running:
            return False
        self._pr_log( 'Stopping Pulse Selector-----------------')
        self._stopims()
        if self.sequencer:
            self._pr_log( 'Stopping Sequencer ---------------------')
            self._caput('%s:%s' % (self.sPlyPv, self.plyctrPvname), '0')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'repeat')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'nshots')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'forever')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'align')

    def align(self):
        if self.running:
            self._stop()
            self._pr_err('Stop the program prior to align blades.')
            return False
        self.pstatus('Aligning', eol=False)
        self.emit(QtCore.SIGNAL("_set_led(QString)"), 'ON')
        self.aligned = False
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'start')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'stop')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'open')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'close')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'auto')
        self.ca.set_align()
        self.ca.start()

    def iocreset(self):
        self._pr_log( 'Restarting IOC -------------------------')
        self._caput('%s:SYSRESET 1' % self.sPpmPv, '1')

    def pstatus(self, msg, eol=True):
        self._pr_log(msg, eol)# + ' ' + '-' * (79 -len(msg)))
        self.emit(QtCore.SIGNAL("_setText(QString, QString)"), 'status', msg)

    def setusesequencer(self, val):
        self.sequencer = val
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'check', 'sequencer')
        self.evcodechanged = True
        self._dumpConfig()

    def setnshots(self, val):
        if self.running:
            return False
        self.nshots = val
        self._caput('%s:%s' % (self.sPlyPv, self.lengthPvname), self.nshots + 1)
        self.evcodechanged = True
        self._dumpConfig()
        return True

    def setrepeat(self, val):
        if self.running:
            return False
        self.repeat = val
        if    int(self.repeat) == 0 or int(self.repeat) == 1:
            playtimes = '0'
        elif  int(self.repeat)   > 1:
            playtimes = '1'
            self._caput('%s:%s' % (self.sPlyPv, self.repeatPvname), self.repeat)
        elif  int(self.repeat) == -1:
            playtimes = '2'
        else:
            return False
        self._caput('%s:%s' % (self.sPlyPv, self.plymodPvname), playtimes)
        self.evcodechanged = True
        self._dumpConfig()
        return True

    def setfreq(self, val):
        if self.running:
            return False
        self.freq = val
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'freq',  self.freq)
        self.evcodechanged = True
        self._dumpConfig()
        return True
    
    def setforever(self, forever=True):
        if forever:
            playtimes = '2'
        else:
            playtimes = '1'
        self._caput('%s:%s' % (self.sPlyPv, self.plymodPvname), playtimes)
        self.forever = forever
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'check', 'forever')
        self.evcodechanged = True
        self._dumpConfig()
        
    def setauto(self):
        if not self.alignDone:
            self.align()
        self.ca.set_auto()
        self.ca.start()
        
    def open(self):
        if self.running:
            self._pr_err('Program is running. Can\'t Open Shutter')
            return False
        self.ca.set_open()
        self.ca.start()
            
    def close(self):
        if self.running:
            self.stop()
        self.ca.set_close()
        self.ca.start()

    def quit(self):
        self._pr_log( 'User ended -----------------------------')
        self.close() # close shutter NOT the application
        self.disconnectEPICSPV()

    def setevrdelay(self, val):
        if self.running:
            return False
        self.evrdelay = val
        self._caput('%s:%s' % (self.sEvrPv, 'D'), self.evrdelay)
        self.evcodechanged = True
        self._dumpConfig()
        return True
    
    def hide(self):
        self.emit(QtCore.SIGNAL("hide()"))

    def show(self):
        self.emit(QtCore.SIGNAL("show()"))

    def setcheckbounds(self, chkbounds=True):
        '''Enable/Disable Out of bounds checking: XPP:TST:MMS:01:SET_EC '''
        self._caput('%s:%s' % (self.sPpmPv, ':SET_EC'), int(chkbounds))
        self.chkbounds = chkbounds
        if chkbounds:
            chkuck = 'check'
        else:
            chkuck = 'uncheck'
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), chkuck, 'chkbounds')
        self._dumpConfig()

    #===========================================================================
    # Non public members
    #===========================================================================
    def _onOpening(self):
        self._dis_pars()
        self.pstatus('Openning shutter', eol=False)

    def _onOpen(self):
        self._guisetstatus('Open')
        self._pr_log(' ...done')
        self.sh_status = 'Open'

    def _onClosing(self):
        self._dis_pars()
        self.pstatus('Closing shutter', eol=False)

    def _onClose(self):
        self._guisetstatus('Close')
        self._pr_log(' ...done')
        self.sh_status = 'Closed'

    def _onAuto(self):
        self._pr_log('Shutter Idle -------------')
        self._guisetstatus('Idle')
        self.sh_status = 'Auto'
    
    def _stopims(self):
        '''Stops the current MCode program'''
        self._pr_log( 'Stop MCode Program --------------------')
        self._caput('%s:RESET_PG' % self.sPpmPv, '1')
        time.sleep(1)
        
    def _check_mode(self):
        if  self.nshots == None or self.freq == None:
            return None
        if  self.nshots == 1 and self.freq == 120:
            return 'Mode 1'
        elif self.freq <= 30:
            return 'Mode 2'
        elif self.nshots > 1 and self.freq == 120:
            return 'Mode 3'
        else:
            return None

    def _initEVR(self, pp_mode='Init'):
        ''' Initialize EVR with correspondent mode values'''
        EVR = {}; EVR['Trg PP']  = ('E', 1) # EVR PV's
        EVR['Pol PP']  = ('P', 1)   ; EVR['Wdt PP']  = ('W', 2000) 
        EVR['Psc PP']  = ('C', 119) ; EVR['Dly PP']  = ('D', 0)
        if pp_mode == 'Init':
            self._pr_log( 'Initialize EVR --------------------')
            for pvval in EVR.values():
                cmd = '%s:%s' % (self.sEvrPv, pvval[0]) ; val = pvval[1]
                self._caput(cmd, val)
        else:
            self._pr_log( 'Program EVR -----------------------')
            if pp_mode == 'Mode 1' or pp_mode == 'Mode 2':
                EVR['Dly PP']  = ('D', int(self.sEVS))
            elif pp_mode == 'Mode 3':
                EVR['Dly PP']  = ('D', int(self.sEVB))
            else:
                return False
            cmd = '%s:%s' % (self.sEvrPv, EVR['Dly PP'][0])
            val = EVR['Dly PP'][1]
            self._caput(cmd, val)
            self.emit(QtCore.SIGNAL("_setsB(QString, QString)"), 'evrdelay', str(val))
        self._pr_log( 40 * '-')
        return True

    def _ims_set(self, pp_mode):
        '''Stop current program, set defaults and start IMS program mode.'''
        ''' This should be modified to work with new Karl MCODE version'''
        self._pr_log('Initialize shutter position -----')
        self._caput('%s:%s' % (self.sPpmPv, 'SE_5'), 1) # what this does???)
        
        if   pp_mode == 'Mode 1':
            pvname = '%s:RUN_MODE1' % self.sPpmPv
            self.curMode = 1
        elif pp_mode == 'Mode 2':
            pvname = '%s:RUN_MODE2' % self.sPpmPv
            self.curMode = 2
        elif pp_mode == 'Mode 3':
            if self.nshots == None:
                return self._pr_err('Number of shots not defined')
            pvname = '%s:RUN_MODE3' % self.sPpmPv#; val = '1'
            self.curMode = 3
        elif pp_mode == 'Mode Open':
            self._stop() # stops the program and the sequencer
            pvname = '%s:S_OPEN' % self.sPpmPv#; val = '1'
        elif pp_mode == 'Mode Close':
            self._stop() # stops the program and the sequencer
            pvname = '%s:S_CLOSE' % self.sPpmPv#; val = '1'            
        else:
            return self._pr_err('!! Bad IMS program mode selected')
        cmd = '%s' % pvname ; val = 1
        self._caput(cmd, val)
        return True

    def _set_sequencer(self, pp_mode):
        ''' Setup the sequencer: 
            self.seqcode1 (shutter trigger)
            self.seqcode2 (Readout)
        '''
        if not self.sequencer:
            self._pr_log('Skipping Sequencer')
            return True
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'repeat')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'nshots')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'forever')
        
        ntimes = self.repeat
        nshots = self.nshots + 1
        fvalue = self.freq
        
        seqdata = list()
        if   pp_mode == 'Mode 1':
            seqcode = self.seqcode1 ; beamtime = 1
            seqdata.append((seqcode, beamtime))
            seqrange = 1
            for n in range(seqrange):
                if n == 0:
                    seqcode = self.seqcode2; beamtime = 2
                else:
                    seqcode = self.seqcode2; beamtime = 1
                seqdata.append((seqcode, beamtime))
        elif pp_mode == 'Mode 2':
            seqcode = self.seqcode1; beamtime = int(120 / fvalue) - 2
            seqdata.append((seqcode, beamtime)) 
            for n in range(nshots):
                seqcode = self.seqcode2; beamtime = 2
                seqdata.append((seqcode, beamtime))
        elif pp_mode == 'Mode 3': # burst mode
            stopat = nshots
            self.sB_repeat.setEnabled(False)
            self.cB_forever.setEnabled(False)
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'repeat')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'forever')

            seqcode = self.seqcode1 ; beamtime = 1
            seqdata.append((seqcode, beamtime))
            seqrange = self.nshots
            for n in range(seqrange):
                if n == 0:
                    seqcode = self.seqcode2; beamtime = 2
                else:
                    seqcode = self.seqcode2; beamtime = 1
                    if self.nshots > 2 and n == seqrange-1:
                        seqdata.append((self.seqcode1, 0))
                        
                seqdata.append((seqcode, beamtime))
        else:
            return self._pr_err('Bad sequencer mode!!')
        
        if pp_mode != 'Mode 3': # burst mode
            stopat = len(seqdata)# - 1
        # print results:
        self._pr_log( 40 * '-')
        self._pr_log( 'N shots     : %02d' % nshots)
        self._pr_log( 'Frequency   : %d'   % fvalue)
        self._pr_log( 'Repetition  : %d'   % ntimes)
        self._pr_log( 'Stop at Seq : %02d' % stopat)
        self._pr_log( 40 * '-')
        self._pr_log( 'Seq %4s    %8s' % ('Code', 'Waittime'))
        for i, idata in enumerate(seqdata):
            self._pr_log('%02d %4s %8s' % (i, str(idata[0]), str(idata[1])))
            
        # reprogram sequencer only if some changes ocurred:
        if self.evcodechanged: 
            self._pr_log( 40 * '-')
            # setup play mode:
            if self.forever:
                self._caput('%s:%s' % (self.sPlyPv, self.plymodPvname), '2')
            elif ntimes > 1:
                self._caput('%s:%s' % (self.sPlyPv, self.plymodPvname), '1')
            else: # repeat once
                self._caput('%s:%s' % (self.sPlyPv, self.plymodPvname), '0')
            # setup n times value: 
            self._caput('%s:%s' % (self.sPlyPv, self.repeatPvname), '%d' % ntimes)
            # setup stop at step:    
            self._caput('%s:%s' % (self.sPlyPv, self.lengthPvname), '%d' % stopat)
            self._pr_log( 40 * '-')
            
            clength = '%d' % len(seqdata)
            evcodes = clength ; betimes = clength ; tktimes = clength  
            
            for idata in enumerate(seqdata):
                evcodes += ' %d ' % idata[1][0]
                betimes += ' %d ' % idata[1][1]
                tktimes += ' %d ' % 0
                
            # Event codes    
            cmd = '%s:%s' % (self.sPlyPv, self.eventcPvname)
            vals = map(int, evcodes) # map( int, cmd[2:])
            vals += [0] * (2048 - len(vals))
            print 'evcodes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
            caput(cmd, tuple(vals))
            
                        
            # Beam time delay
            cmd = '%s:%s' % (self.sPlyPv, self.beamdlPvname)
            vals = map(int, betimes) # map( int, cmd[2:])
            vals += [0] * (2048 - len(vals))
            print 'betimes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
            caput(cmd, tuple(vals))

            # Ticks delay (fiducials)
            cmd = '%s:%s' % (self.sPlyPv, self.tickdlPvname)
            vals = map(int, tktimes) # map( int, cmd[2:])
            vals += [0] * (2048 - len(vals))
            print 'tktimes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
            caput(cmd, tuple(vals))

            self._pr_log( 40*'-')
            self.evcodechanged = False

    def _initSequencer(self):
        ''' Enables or disable GUI sequencer controls'''
        if self.sequencer:
            self._pr_log('Sequencer Control Enabled')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'repeat')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'nshots')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'forever')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'freq')
        else:
            self._pr_log('Sequencer Control Disabled')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'repeat')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'nshots')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'forever')
            self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'disable', 'freq')
        self._dumpConfig()

    def _onalign(self):
        self.emit(QtCore.SIGNAL("_set_led(QString)"), 'OFF')
        self.pstatus(' ...done')
        self.pstatus('Idle')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'start')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'stop')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'open')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'close')
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'enable', 'auto')
        self.alignDone = True
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'check', 'auto')
        self.sh_status = 'Auto'
        self._dumpConfig()

    def _linkEPICSPV(self):
        ''' Connect PVs to monitoring changes: 
               runPv, failUDPv, failLDPv, nshotsPv, evrDlyPv
        '''
        ppPvs = [self.runPv, self.failUDPv, self.failLDPv, 
                 self.nshotsPv, self.evrDlyPv]

        self._connectEPICSPV()
    
        if None in ppPvs:
            self.ims_on = False
            return False
        self._pr_log('Connecting EPICS Monitors -----')
        evtmask = pyca.DBE_VALUE
        # monitor run status
        self.runPv.monitor_cb    = self._runPvCallback
        self.runPv.monitor(evtmask)
        # monitor upper bounds status
        self.failUDPv.monitor_cb = self._failUDPvCallback
        self.failUDPv.monitor(evtmask)
        # monitor lower bounds status                        
        self.failLDPv.monitor_cb = self._failLDPvCallback
        self.failLDPv.monitor(evtmask)
        # monitor number of shots
        self.nshotsPv.monitor_cb = self._nshotsPvCallback
        self.nshotsPv.monitor(evtmask)
        # monitor EVR delay value
        self.evrDlyPv.monitor_cb = self._evrDlyPvCallback
        self.evrDlyPv.monitor(evtmask)
        self.ims_on = True
        pyca.flush_io()
        return True

    #----------------------------------------------------- SE (Run mode) changes
    def _runPvCallback(self, exception=None):
        if exception is None:
            self.event.emit(QtCore.SIGNAL("_statusRUN"))
            
    def _statusRUN(self):
        pvname = '%s:%s' % (self.sPpmPv, self.runPvname)
        se = int(caget(pvname))
        self.running = False
        if se == 0:
            self._guisetstatus('Idle')
        elif se < 4:
            self._initEVR('Mode %d' % se)
            self._guisetstatus('Running %d' % se)
            self.running = True
        elif se == 4:
            self._guisetstatus('Open')
        elif se == 5:
            self._guisetstatus('Close')
        return self.running

    #----------------------------------------------------- Out of bounds changes
    def _failUDPvCallback(self, exception=None):
        if exception is None:
            self.event.emit(QtCore.SIGNAL("_statusUDFAIL"))
            
    def _statusUDFAIL(self):        
        if int(caget('%s:%s' % (self.sPpmPv, self.failUDPvname))):
            self._guisetstatus('Fail UD')
            
    def _failLDPvCallback(self, exception=None):
        if exception is None:
            self.event.emit(QtCore.SIGNAL("_statusLDFAIL"))

    def _statusLDFAIL(self):
        if int(caget('%s:%s' % (self.sPpmPv, self.failLDPvname))):
            self._guisetstatus('Fail LD')            

    #----------------------------------------------- N (Number of shots) changes
    def _nshotsPvCallback(self, exception=None):
        if exception is None:
            self.event.emit(QtCore.SIGNAL("_onNshots"))
            
    def _onNshots(self):
        # TODO: check which mode and correct user nshots according to
        val = str(caget('%s:%s' % (self.sPpmPv, self.nshotsPvname)))
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'nshots',  val)

    #------------------------------------------------------ EVR delay PV changes
    def _evrDlyPvCallback(self, exception=None):
        if exception is None:
            self.event.emit(QtCore.SIGNAL("_onEVRdelay"))
            
    def _onEVRdelay(self):
        val = str(caget('%s:%s' % (self.sEvrPv, self.evrDlyPvname)))
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'evrdelay',val)

    #----------------------------------------------- Sequencer Repeat PV changes
    def _repeatPvCallback(self, exception=None):
        if exception is None:
            self.event.emit(QtCore.SIGNAL("_onRepeat"))
            
    def _onRepeat(self):
        val = str(caget('%s:%s' % (self.sSeqPv, self.repeatPvname)))
        self.emit(QtCore.SIGNAL("_setWidget(QString, QString)"), 'repeat',  val)


    def _connectEPICSPV(self):
        ''' Connect PVs runPv, failUDPv, failLDPv, nshotsPv, evrDlyPv'''
        self._disconnectEPICSPV()
        pycaaction = self._connectPv
        self.runPv    = pycaaction('%s:%s' % (self.sPpmPv, self.runPvname))
        self.failUDPv = pycaaction('%s:%s' % (self.sPpmPv, self.failUDPvname))
        self.failLDPv = pycaaction('%s:%s' % (self.sPpmPv, self.failLDPvname))
        self.nshotsPv = pycaaction('%s:%s' % (self.sPpmPv, self.nshotsPvname))
        self.evrDlyPv = pycaaction('%s:%s' % (self.sEvrPv, self.evrDlyPvname))
        
    def _disconnectEPICSPV(self):
        ''' Disconnect PVs runPv, failUDPv, failLDPv, nshotsPv, evrDlyPv'''
        pycaaction = self._disconnectPv
        self.runPv    = pycaaction('%s:%s' % (self.sPpmPv, self.runPvname))
        self.failUDPv = pycaaction('%s:%s' % (self.sPpmPv, self.failUDPvname))
        self.failLDPv = pycaaction('%s:%s' % (self.sPpmPv, self.failLDPvname))
        self.nshotsPv = pycaaction('%s:%s' % (self.sPpmPv, self.nshotsPvname))
        self.evrDlyPv = pycaaction('%s:%s' % (self.sEvrPv, self.evrDlyPvname))
        self.runPv    = None
        self.failUDPv = None
        self.failLDPv = None
        self.nshotsPv = None
        self.evrDlyPv = None
        
    def _disconnectPv(self, pv):
        if pv != None:
            try:
                pv.disconnect(); pyca.flush_io()
            except:
                pass
        return None

    def _connectPv(self, name, timeout=1.0):
        try:
            pv = Pv(name) ; pv.connect(timeout) ; pv.get(False, timeout)  
            return pv
        except:
            pass

    def _guisetstatus(self, status=''):
        ''' Sets the GUI led indicator and prompt''' 
        if   status == 'Open':
            led = 'GREEN'
        elif status == 'Close':
            led = 'RED'
        elif 'Fail' in status:
            led = 'RED'
        elif status == 'Idle':
            led = 'OFF'
        elif 'Running' in status:
            led = 'RED'
        else:
            led = None
        if led:
            self.emit(QtCore.SIGNAL("_set_led(QString)"), led)
        self.emit(QtCore.SIGNAL("_setText(QString, QString)"), 'status', status)
                
    def _caput(self, cmd, val):
        ''' Issue the CA caput command and print outs'''
        self._pr_log('caput %s %s' % (cmd, val))
        caput(cmd, val)

    def _dumpConfig(self):
        ''' Dump current configuration in a file'''
        f = open(self.cfgdir + self.ppCfgFname, "w")
        f.write("forever   " + str(int(self.forever))      + "\n")
        f.write("repeat    " + str(int(self.repeat))       + "\n")
        f.write("nshots    " + str(int(self.nshots))       + "\n")
        f.write("frequency " + str(int(self.freq))         + "\n")
        f.write("auto      " + str(int(self.auto))         + "\n")
        f.write("open      " + str(int(self.sopen))        + "\n")
        f.write("close     " + str(int(self.sclose))       + "\n")
        f.write("evrdelay  " + str(int(self.evrdelay))     + "\n")
        f.write("sequencer " + str(int(self.sequencer)) + "\n")
        f.write("vm        " + str(int(self.IMS_VM))       + "\n")
        f.write("vi        " + str(int(self.IMS_VI))       + "\n")
        f.write("a         " + str(int(self.IMS_A))        + "\n")
        f.write("d         " + str(int(self.IMS_D))        + "\n")
        f.write("chkbounds " + str(int(self.chkbounds))    + "\n")
        f.close()
        
    def _sheader(self):
        self._pr_log( 40*'-')
        self._pr_log( 'Starting %s Pulse Selector Application' % self.instr.upper())
        self._pr_log( 40*'-')
    
    def _showinfo(self):
        self._pr_log(40 * '-')
        self._pr_log(' %s Pulse Selector Module' % self.instr.upper())
        self._pr_log(40 * '-')
        for k, v in self.ppcfg.iteritems():
            self._pr_log(' %-30s %s' % (k, v))
        self._pr_log(40 * '-')

    def _pr_log(self, msg, eol=True):
        ''' Now just print but maybe could be used to log into a file'''
        if eol:
            print 'PP>', msg
        else:
            print 'PP>', msg,

    def _pr_err(self, msg):
        ''' Now just print but maybe could be used to log into a file'''
        print 'PP> ERROR:', msg
        return False

if __name__ == '__main__':
    pass
'''
    #===========================================================================
    # TO PUT in xxxbeamline.py (pulse picker configuration)
    #===========================================================================
    ppcfg = {}
    ppcfg['Sequencer Pv']               = 'SXR:RXX:IOC:XX:EV'
    ppcfg['Seq play mode Pv']           = 'IOC:IN20:EV01'
    ppcfg['PP Rotation motor Pv']       = 'SXR:SB2:MMS:09'
    ppcfg['PP Y translation Pv']        = 'SXR:SB2:MMS:21'
    ppcfg['PP X translation Pv']        = 'SXR:SB2:MMS:08'
    ppcfg['PP ioc name']                = 'ioc-sxr-trigger-ims'
    ppcfg['PP ioc server name']         = 'ioc-sxr-mot1'
    ppcfg['EVR Pv']                     = 'SXR:R42:EVR:01'
    ppcfg['EVR Burst mode delay']       = '0'
    ppcfg['EVR Single mode delay']      = '5100'
    ppcfg['EVR trigger channel number'] = '2'
    ppcfg['EDM PP motor screen script'] = 'ppm_gui.sh'
    ppcfg['EVR screen script']          = 'evr_gui.sh'
    ppcfg['instr']                      = 'sxr'
    ppcfg['Configuration directory']    = './'
    ppcfg['Current working directory']  = os.getcwd()
    #===========================================================================
    # Main Application
    #===========================================================================
    app   = QtGui.QApplication([''])
    app.setStyle('Cleanlooks')
    app.setPalette(app.style().standardPalette())
    #gui = PPGui(app, cwd, options.instrument, ppLstFname, cfgdir)
    gui = PPGui(ppcfg, app)
    gui.show()
    sys.exit(app.exec_())
'''