#! /bin/env python
import sys, os, errno

# NEEDS ./reg/g/pcds/pyps/las/head/las/lasenv.sh

import pyca
from Pv import Pv
import time
import threading
import termios
import tty, select, curses

#from PyQt4 import QtCore
'''
RELEASE NOTES:
This is the version working at MEC on 10/16/2013
'''
'''
NOTES:
SXR Oscilloscope:
sxr-control:~> rdesktop -g 1280x1024 -a16 scope-sxr-lecroy-825zi-a
/reg/g/pcds/package/epics/3.14-dev/screens/edm/mec/current/mechome
================================================================================
Dan SXR_Python setup:

mkdir pyps
cd pyps
svn co file:///afs/slac/g/pcds/vol2/svn/pcds/package/trunk/sxr

[paiser@pslogin01 sxr 11:43:26] cat sxrenv.sh 
source /reg/g/pcds/setup/pathmunge.sh

PKG_BAS="/reg/common/package/release"
SXR_REL="sxr-0.0.3"
RH5_BLD="x86_64-rhel5-gcc41-opt"
RH6_BLD="x86_64-rhel6-gcc44-opt"
RH5_PTH=$PKG_BAS/$SXR_REL/$RH5_BLD
RH6_PTH=$PKG_BAS/$SXR_REL/$RH6_BLD

if [ "$LSB_FAMILY" == "rhel6" ]; then
  pathmunge       "$RH6_PTH/bin"
  ldpathmunge     "$RH6_PTH/lib"
  pythonpathmunge "$RH6_PTH/python"
elif [ "$LSB_FAMILY" == "rhel5" ]; then
  pathmunge       "$RH5_PTH/bin"
  ldpathmunge     "$RH5_PTH/lib"
  pythonpathmunge "$RH5_PTH/python"
elif [ "$LSB_FAMILY" == "" ]; then
  echo "Cannot determine Linux distribution"
else 
  echo "Linux distribution '$LSB_FAMILY' unsupported by this script"
fi

export EPICS_CA_MAX_ARRAY_BYTES=8000000
[paiser@pslogin01 sxr 11:43:31] nano sxrenv.sh 
[paiser@pslogin01 sxr 11:43:41] ./ps_make -r sxr-paiser-dev


[paiser@pslogin01 sxr 11:43:41] source ../../etc/set_env.sh 

emacs sxr-paiser-dev.rel 
[paiser@pslogin01 package 03:47:31] cp sxr-0.0.3.rel sxr-paiser-dev.rel
================================================================================

The EDM EVR (evr_gui.sh) and PP motor screens shell are located  in:
~/.pp_<instr>/
sxr-control:sxr> ll ~/.pp_sxr/
total 80
-rwxr-xr-x 1 sxropr sxropr  1617 Sep  6 12:53 evr_gui.sh
-rw-r--r-- 1 sxropr sxropr   194 Sep  6 16:43 pp.cfg
-rw-r--r-- 1 sxropr sxropr 57362 Aug 26 10:54 pp_gui.edl
-rwxr-xr-x 1 sxropr sxropr  1638 Sep  6 13:14 ppm_gui.sh

#-------------------------------------------- Examples in XPP/SXR/CXI/MECpython:
ppcfg = {}
ppcfg['Instr']                      = 'sxr'
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
ppcfg['EDM EVR screen script']      = 'evr_gui.sh'
ppcfg['Configuration directory']    = '~/'
ppcfg['Current working directory']  = os.getcwd()
ppcfg['Alignment offset']           = 68.1328 + 11.25
#------------------------------------------------------------------------------
'''
#    #===========================================================================
#    # TO PUT in xxxbeamline.py (pulse picker configuration)
#    #===========================================================================
#    ppcfg = {}
#    ppcfg['Instr']                      = 'sxr'
#    ppcfg['Sequencer Pv']               = 'SXR:RXX:IOC:XX:EV'
#    ppcfg['Seq play mode Pv']           = 'IOC:IN20:EV01'
#    ppcfg['PP Rotation motor Pv']       = 'SXR:SB2:MMS:09'
#    ppcfg['PP Y translation Pv']        = 'SXR:SB2:MMS:21'
#    ppcfg['PP X translation Pv']        = 'SXR:SB2:MMS:08'
#    ppcfg['PP ioc name']                = 'ioc-sxr-trigger-ims'
#    ppcfg['PP ioc server name']         = 'ioc-sxr-mot1'
#    ppcfg['EVR Pv']                     = 'SXR:R42:EVR:01'
#    ppcfg['EVR Burst mode delay']       = '0'
#    ppcfg['EVR Single mode delay']      = '5100'
#    ppcfg['EVR trigger channel number'] = '2'
#    ppcfg['EVR edm screen release']     = 'R3.3.0-2.6.0'
#    ppcfg['PP edm screen release']      = 'R2.3.7'
#    ppcfg['Configuration directory']    = '~/'
#    ppcfg['Current working directory']  = os.getcwd()
#    ppcfg['Alignment offset']           = 68.1328 + 11.25

#class Kutil():
#    ''' Keyboard utilities'''
#    def get_cursor_pos(self):
#        # Save stdin configuration
#        fd = sys.stdin.fileno()
#        settings = termios.tcgetattr(fd)
#    
#        # Set stdin to raw mode
#        tty.setraw(fd)
#    
#        # Request cursor position
#        sys.stdout.write("\033[6n")
#    
#        # Read response one char at a time until 'R'
#        resp = char = ""
#    
#        try:
#            while char != 'R':
#                resp += char
#                char = sys.stdin.read(1)
#        finally:
#            # Restore previous stdin configuration
#            termios.tcsetattr(fd, termios.TCSADRAIN, settings)
#    
#        # Split answer in two and return COL and ROW as tuple
#        return tuple([int(i) for i in resp[2:].split(';')])
#    
#    def getchar(self):
#        ''' Equivale al comando getchar() di C '''
#    
#        fd = sys.stdin.fileno()
#        
#        if os.isatty(fd):
#            
#            old = termios.tcgetattr(fd)
#            new = termios.tcgetattr(fd)
#            new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
#            new[6] [termios.VMIN] = 1
#            new[6] [termios.VTIME] = 0
#            
#            try:
#                termios.tcsetattr(fd, termios.TCSANOW, new)
#                termios.tcsendbreak(fd,0)
#                ch = os.read(fd,7)
#    
#            finally:
#                termios.tcsetattr(fd, termios.TCSAFLUSH, old)
#        else:
#            ch = os.read(fd,7)
#        
#        return(ch)
#    
#    def setup_term(self, fd, when=termios.TCSAFLUSH):
#        mode = termios.tcgetattr(fd)
#        mode[tty.LFLAG] = mode[tty.LFLAG] & ~(termios.ECHO | termios.ICANON)
#        termios.tcsetattr(fd, when, mode)
#    
#    def getch(self,timeout=None):
#        fd = sys.stdin.fileno()
#        old_settings = termios.tcgetattr(fd)
#        try:
#            self.setup_term(fd)
#            try:
#                rw, wl, xl = select.select([fd], [], [], timeout)
#            except select.error:
#                return
#            if rw:
#                return sys.stdin.read(1)
#        finally:
#            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
PP_NOSIMULATE  = 0x0000
PP_NOVERBOSE   = 0x0000
PP_PROMPT      = 0x0001
PP_NOPROMPT    = 0x0002
PP_NOEOL       = 0x0004
PP_NOECHO      = 0x0008
PP_VERBOSE     = 0x0010
PP_SIMULATE    = 0x1000

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
            
class RunPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.name = name
        self.parent = parent
        self.monitor_cb = self.monitor_handler

    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    status = ['Idle', 'One-Shot', 'Flip-Flop', 'Burst Mode', 'Open', 'Closed']
                    se = self.value
                    #print 'se', se
                    self.parent.running = False
                    self.parent.sh_status = status[se]
                    if se > 0 and se < 4:
                        self.parent.running = True
                        self.parent.slitpos = 'Moving'
#                    if se == 0:
#                        self.parent.sh_status = 'Idle'
#                    elif se == 1:
#                        self.parent.sh_status = 'Idle'
#                    elif se == 2:
#                        self.parent.sh_status = 'Idle'
#                    elif se == 3:
#                        self.parent.sh_status = 'Idle'
#                    elif se == 4:
#                        pass
#                        self.parent.sh_status = 'Open'
#                    elif se == 5:
#                        pass
#                        self.parent.sh_status = 'Close'
#                    elif se < 4:
#                        if 
#                        mode = 'Mode %d' % se
#                        #self.parent._initEVR(mode)
#                        self.parent.sh_status = mode
#                        self.parent.running = True
#                    elif se == 4:
#                        pass
#                        self.parent.sh_status = 'Open'
#                    elif se == 5:
#                        pass
#                        self.parent.sh_status = 'Close'
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e
            
class StatusPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.name = name
        self.parent = parent
        self.monitor_cb = self.monitor_handler
        self.sds = {
             0 : 'Waiting for Se mode selection', 
            10 : 'One-Shot Initialization' ,
            11 : 'One-Shot Loop Waiting' ,
            12 : 'One-Shot Complete' ,
            20 : 'Flip-Flop Initialization', 
            21 : 'Flip-Flop Loop Waiting' ,
            22 : 'Flip-Flop Loop Active',
            30 : 'Burst Initialization',
            31 : 'Burst Armed and Waiting', 
            32 : 'Burst Open Pulse Received', 
            33 : 'Burst Close Pulse Received', 
            39 : 'Burst Complete',
            40 : 'Fast Open Initialization', 
            41 : 'Fast Open Complete',
            50 : 'Fast Close Initialization', 
            51 : 'Fast Close Complete',
            80 : 'Hard Reset/Power-Up Initialization',
            81 : 'Soft Reset/Power-Up Initialization', 
            90 : 'Toggle Move Complete',
            91 : 'Move to Positive Closed Position Complete', 
            92 : 'Move to Negative Closed Position Complete', 
            94 : 'Move to Open Position Complete' ,
            95 : 'Close move did not execute because pulse picker is already closed'
            }
        self.sSDs = { 0: 'Idle'      , 1: 'One-Shot', 2: 'Flip-Flop', 
                      3: 'Burst Mode', 4: 'Open'    , 5: 'Close',
                      6: 'Reserved'  , 7: 'Reserved', 8: 'Reset',  9: 'Moving'}
                             
    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    sd = int(self.value)
                    #print 'sd', sd
                    sSD = self.sSDs[sd/10]
                    if   sSD == 'One-Shot':
#                        mode = 'Mode 1'
#                        self.parent.sh_status = '%s %s' % (mode, sSD) 
                        
#                        self.parent._initEVR(mode)
                        self.parent.running = True
                    elif sSD == 'Flip-Flop':
#                        mode = 'Mode 2'
#                        self.parent.sh_status = '%s %s' % (mode, sSD)  
#                        self.parent._initEVR(mode)
                        self.parent.running = True
                    elif sSD == 'Burst Mode':
#                        mode = 'Mode 3'
#                        self.parent.sh_status = '%s %s' % (mode, sSD)  
#                        self.parent._initEVR(mode)
                        self.parent.running = True
                    else:
                        #self.parent.sh_status = sSD
                        self.parent.running   = False
                    self.parent.sdstatus = sSD
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e
            
class SlitposPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.parent = parent
        self.monitor_cb = self.monitor_handler
    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    dfd = {-1: 'Closed', 0: 'Open', 1: 'Closed', 99: '?????'}
                    self.parent.slitpos = dfd[self.value] 
                    self.parent.slitposPvchanged = True
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e

class MovingPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.parent = parent
        self.monitor_cb = self.monitor_handler
    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    dmov = {1: 'Moving', 0: 'Idle'}
                    self.parent.moving = dmov[self.value] 
                    self.parent.movingPvchanged = True
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e
            
            
class NshotsPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.parent = parent
        self.monitor_cb = self.monitor_handler
    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    self.parent.nshots = self.value
                    self.parent.nshotsPvchanged = True
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e

class FailUDPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.parent = parent
        self.monitor_cb = self.monitor_handler
    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    if self.value:
                        self.parent.failUD = True
                        self.parent.alarm = 'Fail UD'
                    else:
                        self.parent.failUD = False
                        if not self.parent.failLD:
                            self.parent.alarm = 'None'
                    self.parent.failUDPvchanged = True
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e

class FailLDPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.parent = parent
        self.monitor_cb = self.monitor_handler
    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    if self.value:
                        self.parent.failLD = True
                        self.parent.alarm = 'Fail LD'
                    else:
                        self.parent.failLD = False
                        if not self.parent.failUD:
                            self.parent.alarm = 'None'
                    self.parent.failLDPvchanged = True
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e

class EvrDlyPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.parent = parent
        self.monitor_cb = self.monitor_handler
    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    self.parent.evrdelay = self.value
                    self.parent.evrDlyPvchanged = True
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e

class PlymodPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.parent = parent
        self.monitor_cb = self.monitor_handler
    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    self.parent.plymod = self.value
                    self.parent.plymodPvchanged = True
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e

class LengthPv(Pv):
    def __init__(self, name, parent=None):
        Pv.__init__(self, name)
        self.parent = parent
        self.monitor_cb = self.monitor_handler
    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.status == pyca.NO_ALARM:
                    self.parent.length = self.value
                    self.parent.lengthPvchanged = True
                else:
                    print '%-30s %s %s' % (self.name,
                                           pyca.severity[self.severity],
                                           pyca.alarm[self.status])
            else:
                print '%-30s' % self.name, exception
        except Exception, e:
            print e

def caput(pvname, value, timeout=1.0):
    #pyca.attach_context()
    try:
        pv = Pv(pvname)
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        #print 'caput', repr(pvname), repr(value)
        pv.put(value, timeout)
        pv.disconnect()
        
    except pyca.pyexc, e:
        print 'pyca exception: %s' %(e)
    except pyca.caexc, e:
        print 'channel access exception: %s' %(e)
        
def caget(pvname, timeout=1.0):
    #pyca.attach_context()
    try:
        pv = Pv(pvname)
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        v = pv.value
        pv.disconnect()
        #print 'caget', pvname, v
        return v
    except pyca.pyexc, e:
        print 'pyca exception: %s' %(e)
        return []
    except pyca.caexc, e:
        print 'channel access exception: %s' %(e)
        return []

#===============================================================================
# Pulse Picker class
#===============================================================================
class PPicker():    
    '''Pulse Picker Class'''
    def __init__(self, ppcfg, autostart=False, save=False, load=False, parent=None):
        self.cwd         = ppcfg['Current working directory']
        instr            = ppcfg['Instr']
        self.instr       = instr
        self.ppcfg       = ppcfg
        self.parent      = parent
        self.ppCfgFname  = 'pp.cfg'
        self.setscfgfilename = ppcfg['Current working directory'] +'/.evset%d.cfg'
        self.cfgpath     = os.environ['HOME'] + '/' + '.pp_%s/' % instr
        
        self.running     = False
        self.sh_status   = None
        self.sdstatus    = None
        self.pp_simulate = PP_NOSIMULATE
        self.verbose     = PP_VERBOSE
        self.singleshotmode = True
        
        self._init_pp_events()
        
        self.modes = {}
        self.modes['One-Shot']  = 'Single shot'
        self.modes['Flip-Flop'] = 'Pulse rate reduction'
        self.modes['Burst']     = 'Burst mode'
        
        # GUI related vars:
        self.nshots    = False
        self.freq      = False
        self.forever   = False
        self.repeat    = False
        self.evrdelay  = False
        self.plymod    = False
        self.length    = False
        self.failLD    = False
        self.failUD    = False
        self.slitpos   = False
        self.chkbounds = True
        self.sequencer = False
        #=======================================================================
        # Picker IOC PV names
        #=======================================================================
        self.runPvname     = 'SE_L' # 0, 1, 2 or 3  = not running or mode n. running
        self.statusPVname  = 'SD_L' # Status Indicator
        self.failUDPvname  = 'UD' # 1 = out of bounds
        self.failLDPvname  = 'LD' # 1 = out of bounds
        self.slitposPvname = 'DF' # Df - Slit Open/Closed Status
        self.boundsPvname  = 'SET_EC' # set boundary positions
        self.homePvname    = 'HOME:MOTOR' # align blades
        self.movingPvname  = 'MV' # moving status Pv
        #self.runPvname     = 'SE' # Waiting for Selection, One Shot, Flip Flop, Burst
        #self.nshotsPvname = 'N' # Number of shots to count in IMS motor trg in
        #=======================================================================
        # Sequencer
        #=======================================================================
        self.seqcode1     =  84 # first trigger to start moving 
        self.seqcode2     =  85 # trigger code to DAQ and Picker
        self.seqcode      = list() # self.seqcode.append(..) or self.seqcode.remove(..)
        seqgroup = {'amo': 1, 'sxr': 2, 'xpp': 3, 'sxr':4, 
                    'cxi': 5, 'mec': 6, 'sp1': 7, 'sp2':8 }
        
        # Macros needs for EDM screens
        self.mioc    = instr.upper() + ':IOC:TRIGGER:IMS'
        self.id      = seqgroup[instr.lower()]
        self.ecs_ioc = 'ECS:SYS0'

#        self.repeatPvname = 'ECS_REPCNT_%s' % seqgroup[self.instr]  # repeat n times counter value
#        self.plymodPvname = 'ECS_PLYMOD_%s' % seqgroup[self.instr]  # sequencer play mode 1,2,3
#        self.plyctrPvname = 'PLYCTL' % seqgroup[self.instr]  # sequencer play control
#        self.eventcPvname = 'ECS_SEQ_%d.A'  % seqgroup[self.instr]  # sequencer event code
#        self.beamdlPvname = 'ECS_SEQ_%d.B'  % seqgroup[self.instr]  # sequencer beam time
#        self.tickdlPvname = 'ECS_SEQ_%d.C'  % seqgroup[self.instr]  # sequencer beam tick
#        self.lengthPvname = 'ECS_LEN_%s'    % seqgroup[self.instr]  # sequencer length number

        self.SEQ_PLY = '%s:%d'   % (self.ecs_ioc, self.id)
        self.SEQ_EVC = '%s:ECS:IOC:01' % instr.upper()

        iinstr = seqgroup[instr.lower()]
        self.repeatPvname = 'REPCNT' # repeat n times counter value
        self.plymodPvname = 'PLYMOD' # sequencer play mode 1,2,3
        self.plyctrPvname = 'PLYCTL' # sequencer play control
        self.lengthPvname = 'LEN'    # sequencer length number
        self.eventcPvname = 'EC_%d'  % iinstr  # sequencer event code
        self.beamdlPvname = 'BD_%d'  % iinstr  # sequencer beam time
        self.tickdlPvname = 'FD_%d'  % iinstr  # sequencer beam tick
        self.burstcPvname = 'BC_%d'  % iinstr  # sequencer burst count
        self.eventdPvname = 'EC_%d'  % iinstr  # sequencer event description

        self.evcodechanged = True
        
        #=======================================================================
        # Initialize variables
        #=======================================================================
        self.sIOC     = None ; self.sIOCDesc   = None # IOC server name
        self.sEvrPv   = None ; self.sEvrDesc   = None # EVR PV base name
        self.sPpmPv   = None ; self.sPpmDesc   = None # IMS motor Picker PV base name 
        self.sYtrPv   = None ; self.sYtrDesc   = None # IMS motor Y translation PV base name 
        self.sXtrPv   = None ; self.sXtrDesc   = None # IMS motor X translation PV base name 
        self.sEDMpp   = None ; self.sEDMppDesc = None # EDM screen location
        self.sEDMev   = None ; self.sEDMevDesc = None # EDM screen location
        self.sEVB     = None ; self.sEVBDesc   = None # EVR burst mode delay
        self.sEVS     = None ; self.sEVSDesc   = None # EVR single shot mode delay
        self.sSRV     = None ; self.sSRVDesc   = None # IOC server name
        self.runPv    = None ; self.failUDPv   = None
        self.failLDPv = None ; #self.nshotsPv   = None
        self.failUDPvchanged = True
        self.failLDPvchanged = True
        self.nshotsPvchanged = True
        self.repeatPv = None ; self.repeatPvchanged = True
        self.plymodPv = None ; self.plymodPvchanged = True
        self.lengthPv = None ; self.lengthPvchanged = True
        self.evrDlyPv = None ; self.evrDlyPvchanged = True
        self.slitposPv = None ; self.slitposPvchanged = True
        self.moving = None
        self.movingPv = None ; self.movingPvchanged = True  
                    
        #=======================================================================
        # Load <instr>beamline.py specific configuration
        #=======================================================================
        
        
##        self.sSeqPv = ppcfg['Sequencer Pv']
        #self.sPlyPv = ppcfg['Seq play mode Pv']
        self.sSRV   = ppcfg['PP ioc server name']
        self.sPpmPv = ppcfg['PP Rotation motor Pv']
        self.sYtrPv = ppcfg['PP Y translation Pv']
        self.sXtrPv = ppcfg['PP X translation Pv']
        self.sEvrPv = ppcfg['EVR Pv']
        self.sEVB   = ppcfg['EVR Burst mode delay']
        self.sEVS   = ppcfg['EVR Single mode delay']
        self.sIOC   = ppcfg['PP ioc name']
        self.sEVRch = ppcfg['EVR trigger channel number']
        self.sEDMpp = '$EPICS_SITE_TOP/modules/pcds_motion/%s' % ppcfg['PP edm screen release']
        self.sEDMev = '$EPICS_SITE_TOP/modules/event/%s'       % ppcfg['EVR edm screen release']
        #=======================================================================

        #=======================================================================
        # Load or Save Event Set
        #=======================================================================
        if save or load:
            evsets = self._getevpresets()
            if save:
                self._saveevpresets(evsets)
            elif load:
                self._loadevpresets(evsets)
            sys.exit()
        #=======================================================================
        # EVR
        #=======================================================================
        ''' Initialize EVR with correspondent mode values'''
        self.EVR = {} # EVR PV's        
        self.EVR['Trg']  = ['%s:CTRL.DG%sE' % (self.sEvrPv, self.sEVRch), 1]
        self.EVR['Pol']  = ['%s:CTRL.DG%sP' % (self.sEvrPv, self.sEVRch), 1]
        self.EVR['Wdt']  = ['%s:CTRL.DG%sW' % (self.sEvrPv, self.sEVRch), 2000]
        self.EVR['Psc']  = ['%s:CTRL.DG%sC' % (self.sEvrPv, self.sEVRch), 119]
        self.EVR['Dly']  = ['%s:CTRL.DG%sD' % (self.sEvrPv, self.sEVRch), 0]
        self.EVR['One-Shot']  = int(self.sEVS)
        self.EVR['Flip-Flop'] = int(self.sEVS)
        self.EVR['Burst']     = int(self.sEVB)

        # disable encoder
        self._pr_log('Disabling IMS close loop###')
        cmd = '%s:%s' % (self.sPpmPv, 'SET_EE') ; val = 0
        self._caput(cmd, val, PP_NOECHO)
        self._pr_log('###done')

        ####self.pvconnect()   # Connect PVs and create monitors

        # reset home speed and base speed:
        self._pr_log('Setting up IMS home speed###')
        self._caput('%s.%s' % (self.sPpmPv, 'HVEL'), 400, PP_NOECHO)
        self._caput('%s.%s' % (self.sPpmPv, 'HBAS'), 100, PP_NOECHO)
        self._pr_log('###done')

        self.stop() 
        self._initEVR('Init')
        if self.sequencer:
            self._pr_log('Sequencer Control Enabled')
        else:
            self._pr_log('Sequencer Control Disabled')        
        if autostart:
            self.autostart()
            self._seqsetup()
    
    def autostart(self):
        print 'NO YET WORKING!!!'
        return False
        '''Starts getting all parameters from pulse picker IOC'''
        if self.running:
            self._pr_err('Program is still running. Can\'t continue!')
            return False
        self._caput('%s:PP_SEQ' % self.sPpmPv, 1, PP_NOECHO) 
        
        self.evrdelay  = int(self._caget('%s:PP_EVRDELAY' % self.sPpmPv, PP_NOECHO))
        #self._readBustpars()
        # freq = [1,2,3,4,5,6,8,10,12,15,20,24,30,40,60,120]
        #self.nshots    = int(self._caget('%s:PP_NSHOTS'   % self.sPpmPv, PP_NOECHO))
        #self.repeat    = int(self._caget('%s:PP_REPEAT'   % self.sPpmPv, PP_NOECHO))
        #self.freq      = freq[int(self._caget('%s:PP_FREQ'     % self.sPpmPv, PP_NOECHO))]
        self.sequencer = bool(int(self._caget('%s:PP_SEQ' % self.sPpmPv, PP_NOECHO)))
        self.info()
        self._set_sequencer(self._check_mode(), PP_NOECHO)
        ###self.start()
        
    def _readBustpars(self):
        # FIXME: place this in monitoring

#        freq = [1,2,3,4,5,6,8,10,12,15,20,24,30,40,60,120] ; em = PP_NOECHO
#        pp_freq = self._caget('%s:PP_FREQ'     % self.sPpmPv, PP_NOECHO)
#        if pp_freq != []:
#            self.freq = freq[int(pp_freq)]
#        pp_repeat = self._caget('%s:PP_REPEAT'   % self.sPpmPv, PP_NOECHO)
#        if pp_repeat != []:
#            self.repeat = int(pp_repeat)
#        self.setnshots(self.nshots)
#        pp_nshots = self._caget('%s:PP_NSHOTS'   % self.sPpmPv, PP_NOECHO)
#        if pp_nshots != []:
#            self.nshots = int(pp_nshots)
#        
        #--------------------------------------------------- Picker Events Setup
#        self.pp_events['B']['EC']  = int(self._caget('%s:PP_ECB'  % self.sPpmPv, PP_NOECHO))
#        self.pp_events['B']['BD']  = int(self._caget('%s:PP_BDB'  % self.sPpmPv, PP_NOECHO))
        self.pp_events['A']['DESC'] = self._caget('%s:PP_ECA.DESC'% self.sPpmPv, PP_NOECHO)
        self.pp_events['B']['DESC'] = self._caget('%s:PP_ECB.DESC'% self.sPpmPv, PP_NOECHO)
        self.pp_events['C']['DESC'] = self._caget('%s:PP_ECC.DESC'% self.sPpmPv, PP_NOECHO)
        self.pp_events['D']['DESC'] = self._caget('%s:PP_ECD.DESC'% self.sPpmPv, PP_NOECHO)
        self.pp_events['1']['DESC'] = self._caget('%s:PP_EC1.DESC'% self.sPpmPv, PP_NOECHO)
        self.pp_events['2']['DESC'] = self._caget('%s:PP_EC2.DESC'% self.sPpmPv, PP_NOECHO)
        self.pp_events['3']['DESC'] = self._caget('%s:PP_EC3.DESC'% self.sPpmPv, PP_NOECHO)
        self.pp_events['4']['DESC'] = self._caget('%s:PP_EC4.DESC'% self.sPpmPv, PP_NOECHO)

        self.pp_events['A']['EC'] = int(self._caget('%s:PP_ECA'  % self.sPpmPv, PP_NOECHO))
        self.pp_events['B']['EC'] = int(self._caget('%s:PP_ECB'  % self.sPpmPv, PP_NOECHO))             
        self.pp_events['C']['EC'] = int(self._caget('%s:PP_ECC'  % self.sPpmPv, PP_NOECHO))
        self.pp_events['D']['EC'] = int(self._caget('%s:PP_ECD'  % self.sPpmPv, PP_NOECHO))             
        self.pp_events['1']['EC'] = int(self._caget('%s:PP_EC1'  % self.sPpmPv, PP_NOECHO))
        self.pp_events['2']['EC'] = int(self._caget('%s:PP_EC2'  % self.sPpmPv, PP_NOECHO))             
        self.pp_events['3']['EC'] = int(self._caget('%s:PP_EC3'  % self.sPpmPv, PP_NOECHO))
        self.pp_events['4']['EC'] = int(self._caget('%s:PP_EC4'  % self.sPpmPv, PP_NOECHO))
                         
        self.pp_events['A']['BD'] = int(self._caget('%s:PP_BDA'  % self.sPpmPv, PP_NOECHO))
        self.pp_events['B']['BD'] = int(self._caget('%s:PP_BDB'  % self.sPpmPv, PP_NOECHO))             
        self.pp_events['C']['BD'] = int(self._caget('%s:PP_BDC'  % self.sPpmPv, PP_NOECHO))
        self.pp_events['D']['BD'] = int(self._caget('%s:PP_BDD'  % self.sPpmPv, PP_NOECHO))             
        self.pp_events['1']['BD'] = int(self._caget('%s:PP_BD1'  % self.sPpmPv, PP_NOECHO))
        self.pp_events['2']['BD'] = int(self._caget('%s:PP_BD2'  % self.sPpmPv, PP_NOECHO))             
        self.pp_events['3']['BD'] = int(self._caget('%s:PP_BD3'  % self.sPpmPv, PP_NOECHO))
        self.pp_events['4']['BD'] = int(self._caget('%s:PP_BD4'  % self.sPpmPv, PP_NOECHO))

        self.pp_events['A']['ENA'] = int(self._caget('%s:PP_ENAA' % self.sPpmPv, PP_NOECHO))
        self.pp_events['B']['ENA'] = int(self._caget('%s:PP_ENAB' % self.sPpmPv, PP_NOECHO))
        self.pp_events['C']['ENA'] = int(self._caget('%s:PP_ENAC' % self.sPpmPv, PP_NOECHO))
        self.pp_events['D']['ENA'] = int(self._caget('%s:PP_ENAD' % self.sPpmPv, PP_NOECHO))
        self.pp_events['1']['ENA'] = int(self._caget('%s:PP_ENA1' % self.sPpmPv, PP_NOECHO))
        self.pp_events['2']['ENA'] = int(self._caget('%s:PP_ENA2' % self.sPpmPv, PP_NOECHO))
        self.pp_events['3']['ENA'] = int(self._caget('%s:PP_ENA3' % self.sPpmPv, PP_NOECHO))
        self.pp_events['4']['ENA'] = int(self._caget('%s:PP_ENA4' % self.sPpmPv, PP_NOECHO))

    def _setdevices(self):
        pickermode = self._check_mode()
        if not self._set_sequencer(pickermode, PP_NOECHO):
            return False
        if not self._initEVR(pickermode): # program EVR
            return False
        if self.singleshotmode == True:
            pickermode = 'Flip-Flop'
            # set sequencer to ONCE
            self._caput('%s:%s' % (self.SEQ_PLY, self.plymodPvname), 0, PP_NOECHO)
        if not self._ims_set(pickermode):
            return False
        return True

    def setsingleshot(self):
        self.setusesequencer(True)
        self.setfreq(120)
        self.setnshots(1)
        self.singleshotmode = True
        self.setstopatstep(1)
        if not self._setdevices():
            return False

    def setfreqreduction(self, freq):
        self.singleshotmode = False
        if freq in [1,2,3,4,5,6,8,10,12,15,20,24,30]:
            self.setusesequencer(True)
            self.setfreq(freq)
            self.setnshots(1)
            self.setrepeat(-1)
            if not self._setdevices():
                return False
        else:
            self._pr_err('Frequency %d Hz not allowed. Can\'t reduce frequency' % freq, PP_NOPROMPT)
            return False
        return True

    def setburst(self, nshots, freq=120):
        self.singleshotmode = False
        if freq in [1,2,3,4,5,6,8,10,12,15,20,24,30]:
            self.setusesequencer(True)
            self.setfreq(freq)
            self.setnshots(1)
            self.setrepeat(nshots)
            if not self._setdevices():
                return False
        elif freq == 120:
            self.setfreq(freq)
            self.setusesequencer(True)
            self.setnshots(nshots)
            self.setrepeat(0)
            if not self._setdevices():
                return False
        else:
            self._pr_err('Frequency %d Hz not allowed. Can\'t reduce frequency' % freq, PP_NOPROMPT)
            return False
        return True
        
    def prepare(self):
        ##badstatus = ['Open', None]
        ##if self.sh_status in badstatus:
        ##    return self._pr_err('Invalid Position. Shutter must be in Idle')
            
        mode = self._check_mode()
        if not mode:
            return self._pr_err('Invalid Mode: %s' % mode)
        self._pr_log(self.modes[mode])

        # program EVR
        if not self._initEVR(mode):
            return self._pr_err( 'set EVR FAIL')

        self._pr_log('Start MCode Program###')
        if not self._ims_set(mode):
            return self._pr_err( 'set IMS motor parametes FAIL')
        self._pr_log('###done')
        # send sequences to Sequencer:
        if self.sequencer:
            self._pr_log('Setup Sequencer###')
            if not self._set_sequencer(mode, PP_NOECHO):
                self._pr_log('###failed')
                return self._pr_err( 'set Sequencer FAIL')
            time.sleep(1)
            self._pr_log('###done')
        #self.info()

    def start(self):
        '''Start the Pre programmed sequencer'''
        if self.sequencer:
            self._pr_log('Starting Sequencer###')
            self._caput('%s:%s' % (self.SEQ_PLY, self.plyctrPvname), 1)
            self._pr_log('###done')
            return True
        else:
            self._pr_err('The \'setusesequencer\' is False. Can\'t start sequencer')
            return False
            
    def stop(self):
        self._pr_log('Stopping IMS###')
        '''Stops the current MCode program'''
        self._caput('%s:RESET_PG' % self.sPpmPv, 1, PP_NOECHO)#'1')
        time.sleep(1)
        self._pr_log('###done')
        if self.sequencer:
            self._pr_log('Stopping Sequencer###')
            cmd = '%s:%s' % (self.SEQ_PLY, self.plyctrPvname); val = 0#'0'
            self._caput(cmd, val, PP_NOECHO)
            self._pr_log('###done')
        #self.info()
        return True

    def iocreset(self):
        self._pr_log('Restarting IOC###')
        self._caput('%s:SYSRESET' % self.sPpmPv, '1')
        self._pr_log('###done')
        
    def pstatus(self, msg, eol=True):
        if msg[-3:] == '...': eol = False
        self._pr_log(msg, eol)# + ' ' + '-' * (79 -len(msg)))

    def setusesequencer(self, val):
        if self.running:
            self._pr_err('Program is running. Can\'t change sequencer mode')
            return False
        self.sequencer = val
        self.evcodechanged = True

    def setnshots(self, val):
        if self.running:
            self._pr_err('Program is running. Can\'t change number of shots')
            return False
        self.nshots = val
        # update sequencer (SXR/XPP) compatible mode
        self._caput('%s:%s' % (self.SEQ_PLY, self.lengthPvname), self.nshots + 1, PP_NOECHO)
        # upadte pp_gui with real number of shots
        self._caput('%s:PP_NSHOTS' % self.sPpmPv, self.nshots, PP_NOECHO)
        self.evcodechanged = True
        return True
    
    def setstopatstep(self, val):
        if self.running:
            self._pr_err('Program is running. Can\'t change stop at step')
            return False
        self._caput('%s:%s' % (self.SEQ_PLY, self.lengthPvname), int(val))#, PP_NOECHO)
        return True
    
    def setrepeat(self, val):
        if self.running:
            self._pr_err('Program is running. Can\'t change repeat number')
            return False
        self.repeat = val
        if    int(self.repeat) == 0 or int(self.repeat) == 1:
            playtimes = '0'
        elif  int(self.repeat)   > 1:
            playtimes = '1'
            self._caput('%s:%s' % (self.SEQ_PLY, self.repeatPvname), int(self.repeat), PP_NOECHO)
        elif  int(self.repeat) == -1:
            playtimes = '2'
        else:
            return False
        self._caput('%s:%s' % (self.SEQ_PLY, self.plymodPvname), int(playtimes), PP_NOECHO)
        self.evcodechanged = True
        return True

    def setfreq(self, val):
        if self.running:
            self._pr_err('Program is running. Can\'t change frequency')
            return False
        freq = [1,2,3,4,5,6,8,10,12,15,20,24,30,40,60,120]
        if val not in freq:
            self._pr_err('Frequency value not allowed. Can\'t change frequency')
            return False
        self._caput('%s:PP_FREQ' % self.sPpmPv, freq.index(val), PP_NOECHO)
        self.freq = val
        #self._readBustpars()
        #self._writeBustpars()
        self.evcodechanged = True
        return True
    
    def setforever(self, forever=True):
        if forever:
            playtimes = '2'
        else:
            playtimes = '1'
        self._caput('%s:%s' % (self.SEQ_PLY, self.plymodPvname), int(playtimes))
        if self.instr == 'mec':
            # single shot special mode:
            # set dbeam to 3 (pulse reduction to 30Hz)
            ecbd = "MEC:ECS:IOC:01:BD_6:00"
            self._caput('%s' % (ecbd), 3)
        self.forever = forever
        self.evcodechanged = True

    def open(self):
        if self.running:
            self._pr_err('Program is running. Can\'t Open Shutter')
            return False
        cmd = '%s:S_OPEN' % self.sPpmPv; val = 1
        caput(cmd, val)        
        
    def close(self):
        if self.running:
            self.stop()
        cmd = '%s:S_CLOSE' % self.sPpmPv; val = 1
        caput(cmd, val)        

    def quit(self):
        self._pr_log('User ended')
        self.close() # close shutter NOT the application

    def setevrmode(self, nshots):
        if nshots == 1:
            self.setevrdelay(self.ppcfg['EVR Single mode delay'])
        else:
            self.setevrdelay(self.ppcfg['EVR Burst mode delay'])

    def setevrdelay(self, val):
        if self.running:
            self._pr_log('Warning: Program is running. EVR delay changed')
        self.evrdelay = val
        cmd = self.EVR['Dly'][0] ; val = int(val)
        self._caput(cmd, val, PP_NOECHO)
        self._caput('%s:PP_EVRDELAY' % self.sPpmPv, val, PP_NOECHO)
        self.evrDlyPvchanged = True
        self.evcodechanged = True
        return True
    
    def setcheckbounds(self, chkbounds=True):
        '''Enable/Disable Out of bounds checking: XPP:TST:MMS:01:SET_EC '''
        cmd = '%s:%s' % (self.sPpmPv, self.boundsPvname) ; val = 1
        self._caput(cmd, val)
        self.chkbounds = chkbounds
        if chkbounds:
            self.pstatus('Checking boundaries')
        else:
            self.pstatus('Not checking boundaries')
            
    def home(self):
        cmd = '%s:%s' % (self.sPpmPv, self.homePvname) ; val = 1
        self._caput(cmd, val)
        
        
    def _check_mode(self):
        #self._readBustpars()
        if  self.nshots == None or self.freq == None:
            return None
        if  self.nshots == 1 and self.freq == 120:
            return 'One-Shot'
        elif self.freq <= 30:        
            return 'Flip-Flop'
        elif self.nshots > 1 and self.freq == 120:
            return 'Burst'
        else:
            return None

    def _initEVR(self, pp_mode='Init'):
        if pp_mode == 'Init':
            self._pr_log('Initializing EVR###')
            pars = ['Trg', 'Pol', 'Wdt', 'Psc', 'Dly']
            for par in pars:
                self._caput(self.EVR[par][0], self.EVR[par][1], PP_NOECHO)
        else:
            self._pr_log('Program EVR###')
#            if pp_mode == 'One-Shot' or pp_mode == 'Flip-Flop':
#                self.EVR['Dly'][1] = int(self.sEVS)
#            elif pp_mode == 'Burst':
#                self.EVR['Dly'][1] = int(self.sEVB)
#            else:
#                return False
#            cmd = self.EVR['Dly'][0] ; val = self.EVR['Dly'][1]
            cmd = self.EVR['Dly'][0] ; val = self.EVR[pp_mode]
            self._caput(cmd, val, PP_NOECHO)
            self._caput('%s:PP_EVRDELAY' % self.sPpmPv, val, PP_NOECHO)
            self.evrDlyPvchanged = True
        self._pr_log('###done')
        return True

    def _ims_set(self, pp_mode):
        '''Stop current program, set defaults and start IMS program mode.'''
        self._pr_log('Initialize shutter position###')
        self.close() # close the shutter
        self._pr_log('###done')

        if   pp_mode == 'One-Shot':            
            pvname = '%s:RUN_ONESHOT' % self.sPpmPv
        elif pp_mode == 'Flip-Flop':
            pvname = '%s:RUN_FLIPFLOP' % self.sPpmPv
        elif pp_mode == 'Burst':
            if self.nshots == None:
                return self._pr_err('Number of shots not defined', PP_NOPROMPT)
            pvname = '%s:RUN_BURSTMODE' % self.sPpmPv#; val = '1'
        else:
            return self._pr_err('Bad IMS program mode selected', PP_NOPROMPT)
        self._caput(pvname, 1, PP_NOECHO)
        return True

    def _set_sequencer(self, pp_mode, em=PP_NOECHO):
        '''
        if PP_NSHOTS == -1 => continuous mode
        
        '''
        
        ''' Setup the sequencer: 
            self.seqcode1 (shutter trigger)
            self.seqcode2 (Readout)
    # event:
    #   83: start princeton exposure
    #   84: open/close shutter trigger
    #   85: DAQ readout 

    # nshots == 1
    # seq:
    #      event code   beam delay   fiducial delay(360Hz)
    #      83           1            0
    #      84           0            0
    #      85           1            0

    # nshots == 2 (old motor, which doesn't need close trigger)
    # seq:
    #      event code   beam delay   fiducial delay(360Hz)
    #      83           1            0
    #      84           0            0
    #      85           2            0
    #      85           1            0

    # nshots == 3 or more
    # seq:
    #      event code   beam delay   fiducial delay(360Hz)
    #      83           1            0
    #      84           0            0
    #      85           2            0
    #      85           1            0  *
    #      84           0            0  * fired at the same time
    #      85           1            0

    # nshots == 4 or more
    # seq:
    #      event code   beam delay   fiducial delay(360Hz)
    #      83           1            0
    #      84           0            0
    #      85           2            0
    #      85           1            0  
    #      85           1            0  *
    #      84           0            0  * fired at the same time
    #      85           1            0            
    
    for nshots>1 => 85(nshots
  0                                   1                                       2
  1   2   3   4   5   6   7   8   9   0   1   2   3   4   5   6   7   8   9   0
  |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
  
  
  PC
        
        
pypsepics.put('ECS:SYS0:%d:SEQ.C', tuple([0]*2048))
pypsepics.put('ECS:SYS0:%d:SEQ.C', tuple([1]*2))

XPP: Picker EC 94
     DAQ     EC 95



#!/bin/bash
cd /reg/neh/home1/paiser/svn-working/ioc/common/xip_pp/current
edm -eolc -m MOTOR=XPP:SB2:MMS:29 pp_screens/pp_burst.edl


edm -x -eolc -m MOTOR=XPP:SB2:MMS:29 -m ECS_IOC=ECS:SYS0 -m ID=3 -m MIOC=XPP:IOC:TRIGGER:IMS pp_screens/pp_burst.edl &

#!/bin/bash

# Change to directory containing the script
homepath=`dirname $0`
cd /reg/neh/home1/paiser/svn-working/ioc/common/xip_pp/current
# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export PCDS_EDMS=/reg/g/pcds/package/epics/3.14/screens/edm
export EDMDATAFILES=.:${PCDS_EDMS}/common/NewportXPS8/current
export EPICS_CA_MAX_ARRAY_BYTES=8000000

# Launch edm with picker screen
edm -x -eolc -m MOTOR=XPP:SB2:MMS:29 -m ECS_IOC=ECS:SYS0 -m ID=3 -m MIOC=XPP:IOC:TRIGGER:IMS pp_screens/pp_burst.edl &

cd $homepath
~             


        '''
        
        if not self.sequencer:
            self._pr_log('Skipping Sequencer')
            return True
        if self.verbose == PP_VERBOSE:        
            self._pr_log(' Setup Sequencer...')
        fd = 0; bc = 0 # set fiducial and burst count to 0
        #=======================================================================
        # Reads nshots, repeat and freq
        #=======================================================================
        
        self._readBustpars()
        ntimes = self.repeat
        nshots = self.nshots + 1
        
        #print 'pp_mode now is', pp_mode
        
        seqdata = list()
        evs = ['A', 'B', 'C', 'D', '1', '2', '3', '4']
        
        
        
        #=======================================================================
        # Single Shot [Trigger => Close->Open->Close]
        #=======================================================================
        if   pp_mode == 'One-Shot':
            '''
            set fixed dealy 3
            168   3
           (176)  1
           
            '''
            
            #self.pp_events['A']['BC']
            for ev in evs:
                if self.pp_events[ev]['ENA']:
                    seqdata.append((int(self.pp_events[ev]['EC']), 
                                    int(self.pp_events[ev]['BD']), 0, 0,
                                        self.pp_events[ev]['DESC']))
                else:
                    seqdata.append((0,0,0,0,''))

        #=======================================================================
        # Flip-Flop (Freq Reduction)<SEQcount> + [Trigger => Close->Open->Close]
        #=======================================================================
        elif pp_mode == 'Flip-Flop': # or Pulse Reduction Mode
            #===================================================================
            # Startup:
            #===================================================================
            '''
            dictRateToSyncMarker = {0.5:0, 1:1, 5:2, 10:3, 30:4, 60:5, 120:6}
            #dictRateToSyncMarker = {0.5:0, 1:1, 5:2, 10:3, 30:4, 60:5, 120:6}
            accel_beam_rate = self._caget('EVNT:SYS0:1:LCLSBEAMRATE', PP_NOECHO)
            
            # set_sync_marker 
            cmd = '%s:%s' % (self.SEQ_PLY, 'SYNCMARKER')
            self._caput(cmd, dictRateToSyncMarker[accel_beam_rate], PP_NOECHO)
            176 fs las (sp - short pulse) sp las
            182 ns las (lp - long pulse)  lp las
            168 picker 
            check beamrate against the user frequency
            
            Due the bug of sequencer we need to workaround:
            -> first the device, after the picker
            
            176   0
            168   (120/freq)-1
            
            
            
            
             '''
            BEAMRATE = 120
            
            nskip = int(BEAMRATE / self.freq) - 1 # number of pulses to skip
            for ev in evs:
                if self.pp_events[ev]['ENA']:
                    #nskip -= 1
                    if self.pp_events[ev]['DESC'] == 'Picker':
                        seqdata.append((int(self.pp_events[ev]['EC']), 
                                            nskip, 0, 0,
                                            self.pp_events[ev]['DESC']))
                    else:    
                        seqdata.append((int(self.pp_events[ev]['EC']), 
                                            0, 0, 0,
                                            self.pp_events[ev]['DESC']))
                else:
                    seqdata.append((0,0,0,0,''))
        #=======================================================================
        # Burst [Trigger => Close->Open] + <SEQcount> + [Trigger =>Open->Close]
        #=======================================================================
        elif pp_mode == 'Burst':
            #===================================================================
            # Startup burst:
            #===================================================================
            daq_ec = 0
            for ev in evs:
                if self.pp_events[ev]['ENA']:
                    if self.pp_events[ev]['DESC'] == 'Picker':
                        desc = 'Waiting ' + self.pp_events[ev]['DESC'] + ' Open'
                        seqdata.append((int(self.pp_events[ev]['EC']), 1, 0, 0, desc))
                    if self.pp_events[ev]['DESC'] == 'DAQ':
                        daq_ec = (int(self.pp_events[ev]['EC']))
            for n in range(self.nshots-1):
                if n == 0: bd = 2
                else:      bd = 1
                seqdata.append((daq_ec, bd, 0, 0, 'Getting shot'))
            #===================================================================
            # Finish burst:
            #===================================================================
            for ev in evs:
                if self.pp_events[ev]['ENA']:
                    if self.pp_events[ev]['DESC'] == 'Picker':
                        desc = 'Getting shot + ' + self.pp_events[ev]['DESC'] + ' Close'
                        seqdata.append((int(self.pp_events[ev]['EC']), 0, 0, 0, desc))
        else:
            return self._pr_err('Bad sequencer mode!!')
        
        if pp_mode != 'Burst':
            stopat = len(seqdata) - 1
        else:
            stopat = self.nshots

        #print 'seqdata', len(seqdata), 'items'
        # print results:
        self._pr_log(' ' + 40 * '-')
        self._pr_log('Mode###')
        self._pr_log('###%s' % pp_mode)
        self._pr_log('N shots###')
        self._pr_log('###%d' % (int(self.nshots)))
        self._pr_log('Frequency###')
        self._pr_log('###%d'   % self.freq)
        self._pr_log('Repetition###')
        self._pr_log('###%d'   % ntimes)
        self._pr_log('Stop at Step###')
        self._pr_log('###%d' % stopat)
        self._pr_log(' ' + 40 * '-')
        self._pr_log(' %-4s   %-4s %-4s %-4s %-4s  %s' % ('Seq', 'EV', 'BD', 'FD', 'BC', 'Device/Function'))
        for i, idata in enumerate(seqdata):
            self._pr_log(' %-04d   %-4s  %-4s %-4s %-4s %s' % (i, str(idata[0]), str(idata[1]), 
                            str(idata[2]), str(idata[3]), str(idata[4])))
        self._pr_log(' ' + 40 * '-')
        
        
        if self.pp_simulate == PP_SIMULATE:
            self._pr_log('Simulation Mode###')
            self._pr_log('###True')
            return False

        # reprogram sequencer only if some changes ocurred:
        if self.evcodechanged:
            # this need to be tested
             
            if em != PP_NOECHO: self._pr_log(' ' + 40 * '-')
            # setup play mode:
            if self.forever:
                self._caput('%s:%s' % (self.SEQ_PLY, self.plymodPvname), 2, PP_NOECHO)
            elif ntimes > 1:
                self._caput('%s:%s' % (self.SEQ_PLY, self.plymodPvname), 1, PP_NOECHO)
            else: # repeat once
                self._caput('%s:%s' % (self.SEQ_PLY, self.plymodPvname), 0, PP_NOECHO)
            # setup n times value: 
            self._caput('%s:%s' % (self.SEQ_PLY, self.repeatPvname), ntimes, PP_NOECHO)
            # setup stop at step:    
            self._caput('%s:%s' % (self.SEQ_PLY, self.lengthPvname), stopat, PP_NOECHO)
            if em != PP_NOECHO: self._pr_log(' ' + 40 * '-')
            
            
            ###clength = '%d' % len(seqdata)
            ###evcodes = clength ; betimes = clength
            ###tktimes = clength ; burstct = clength
            #descrip = clength 
            
            evcodes = '' ; betimes = ''
            tktimes = '' ; burstct = ''
            descrip = ''
            
            #for idata in enumerate(seqdata):
            for idata in seqdata:
                evcodes += ' %d ' % idata[0]
                betimes += ' %d ' % idata[1]
                tktimes += ' %d ' % idata[2]
                burstct += ' %d ' % idata[3]
                descrip += ';%s;' % idata[4]
                 
            
            
            # Event codes    
            cmd = '%s:%s' % (self.SEQ_PLY, 'SEQ.A')
            vals = map(int, evcodes.split())
            #vals = map(int, evcodes) # map( int, cmd[2:])
            vals += [0] * (2048 - len(vals))
            #print 'evcodes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
            self._caput(cmd, tuple(vals))
            
                        
            # Beam time delay
            cmd = '%s:%s' % (self.SEQ_PLY, 'SEQ.B')
            vals = map(int, betimes.split())
            #vals = map(int, betimes) # map( int, cmd[2:])
            vals += [0] * (2048 - len(vals))
            #print 'betimes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
            self._caput(cmd, tuple(vals))

            # Ticks delay (fiducials)
            cmd = '%s:%s' % (self.SEQ_PLY, 'SEQ.C')
            vals = map(int, tktimes.split())
            #vals = map(int, tktimes) # map( int, cmd[2:])
            vals += [0] * (2048 - len(vals))
            #print 'tktimes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
            self._caput(cmd, tuple(vals))
            
            # Burst count
            cmd = '%s:%s' % (self.SEQ_PLY, 'SEQ.C')
            vals = map(int, burstct.split())
            #vals = map(int, burstct) # map( int, cmd[2:])
            vals += [0] * (2048 - len(vals))
            #print 'tktimes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
            self._caput(cmd, tuple(vals))
            
#            # Description (NOT WORKING)
#            cmd = '%s:%s' % (self.SEQ_PLY, 'SEQ.E')
#            vals = map(int, burstct.split())
#            #vals = map(int, burstct) # map( int, cmd[2:])
#            vals += [0] * (2048 - len(vals))
#            print 'tktimes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
#            self._caput(cmd, tuple(vals))

#            # Event codes    
#            ###cmd = '%s:%s' % (self.SEQ_EVC, self.eventcPvname)
#            vals = map(int, evcodes.split()) # map( int, cmd[2:])
#            vals += [0] * (2048 - len(vals))
#            #FIXME: temporaty solution until fix the array problem
#            maxval = len(seqdata)
#            for i in range(maxval):                
#                cmd = '%s:%s:%02d' % (self.SEQ_EVC, self.eventcPvname, i)
#                self._caput(cmd, vals[i], PP_NOECHO)
#            ####print 'evcodes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
#            ###self._caput(cmd, tuple(vals),'ARRAY')
#                        
#                        
#            
#            # Beam time delay
#            ###cmd = '%s:%s' % (self.SEQ_EVC, self.beamdlPvname)
#            vals = map(int, betimes.split()) # map( int, cmd[2:])
#            vals += [0] * (2048 - len(vals))
#            #FIXME: temporaty solution until fix the array problem
#            for i in range(maxval):
#                cmd = '%s:%s:%02d' % (self.SEQ_EVC, self.beamdlPvname, i)
#                self._caput(cmd, vals[i], PP_NOECHO)
#            ####print 'betimes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
#            ###self._caput(cmd, tuple(vals),'ARRAY')
#
#            # Ticks delay (fiducials)
#            ###cmd = '%s:%s' % (self.SEQ_EVC, self.tickdlPvname)
#            vals = map(int, tktimes.split()) # map( int, cmd[2:])
#            vals += [0] * (2048 - len(vals))
#            #FIXME: temporaty solution until fix the array problem
#            for i in range(maxval):
#                cmd = '%s:%s:%02d' % (self.SEQ_EVC, self.tickdlPvname, i)
#                self._caput(cmd, vals[i], PP_NOECHO)
#            ####print 'tktimes\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
#            ###self._caput(cmd, tuple(vals),'ARRAY')
#
#            # Burst count
#            ###cmd = '%s:%s' % (self.SEQ_EVC, self.burstcPvname)
#            vals = map(int, burstct.split()) # map( int, cmd[2:])
#            vals += [0] * (2048 - len(vals))
#            #FIXME: temporaty solution until fix the array problem
#            for i in range(maxval):
#                cmd = '%s:%s:%02d' % (self.SEQ_EVC, self.burstcPvname, i)
#                self._caput(cmd, vals[i], PP_NOECHO)
#            ####print 'burstct\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
#            ###self._caput(cmd, tuple(vals),'ARRAY')
#
##            # Description
##            cmd = '%s:%s.DESC' % (self.SEQ_EVC, self.eventcPvname)
##            vals = map(str, descrip) # map( int, cmd[2:])
##            vals += [''] * (2048 - len(vals))
##            print 'descrip\n', cmd, tuple(vals)[:15] # print limited data for debug purposes
##            ##caput(cmd, tuple(vals)'ARRAY')

            if em != PP_NOECHO: self._pr_log(' ' + 40 * '-')
            self.evcodechanged = False
            self._pr_log('Setup Sequencer###'); self._pr_log('###done')
            return True
        return self._pr_log('done')

    def pvconnect(self):
        ''' Connect PVs to monitoring changes: 
               runPv, failUDPv, failLDPv, evrDlyPv
        '''
        self._pr_log('Connecting EPICS Monitors -----')
        evtmask = pyca.DBE_VALUE
        
        self.runPv = RunPv('%s:%s' % (self.sPpmPv, self.runPvname), self)
        self.runPv.connect(5)
        self.runPv.monitor(evtmask)

        self.statusPV = StatusPv('%s:%s' % (self.sPpmPv, self.statusPVname), self)
        self.statusPV.connect(5)
        self.statusPV.monitor(evtmask)
                
        self.failUDPv = FailUDPv('%s:%s' % (self.sPpmPv, self.failUDPvname), self)
        self.failUDPv.connect(5)
        self.failUDPv.monitor(evtmask)

        self.failLDPv = FailLDPv('%s:%s' % (self.sPpmPv, self.failLDPvname), self)
        self.failLDPv.connect(5)
        self.failLDPv.monitor(evtmask)

        self.evrDlyPv = EvrDlyPv(self.EVR['Dly'][0], self)
        self.evrDlyPv.connect(5)
        self.evrDlyPv.monitor(evtmask)

        self.plymodPv = PlymodPv('%s:%s' % (self.SEQ_PLY, self.plymodPvname), self)
        self.plymodPv.connect(5)
        self.plymodPv.monitor(evtmask)

        self.lengthPv = LengthPv('%s:%s' % (self.SEQ_PLY, self.lengthPvname), self)
        self.lengthPv.connect(5)
        self.lengthPv.monitor(evtmask)
        
        self.slitposPv = SlitposPv('%s:%s' % (self.sPpmPv, self.slitposPvname), self)
        self.slitposPv.connect(5)
        self.slitposPv.monitor(evtmask)

        self.movingPv = MovingPv('%s:%s' % (self.sPpmPv, self.movingPvname), self)
        self.movingPv.connect(5)
        self.movingPv.monitor(evtmask)

        return True

    def _caput(self, cmd, val, mode=True):
        ''' Issue the CA caput command and print outs'''
        if mode == 'ARRAY':
            'It needs to be fixed!!! Why doesn\'t work anymore??'
            caput(cmd, val, mode) 
            return False
        if mode != PP_NOECHO:            
            if type(val) == type(tuple()):
                self._pr_log('caput (partial) %s %s' % (cmd, val[:15]))
            else:
                self._pr_log('caput %s %s' % (cmd, val))
        caput(cmd, val)

    def _caget(self, qry, echo=True):
        ''' Issue the CA caget command and print outs'''
        val = str(caget(qry))
        if echo != PP_NOECHO:
            self._pr_log('caget %s' % qry)
            self._pr_log('%s %s' % (qry, val))
        return val

    def _pr_log(self, msg, mode=PP_PROMPT):
        ''' Now just print but maybe could be used to log into a file'''
        if self.verbose != PP_VERBOSE:
            return False
        
        if '###' in msg[-3:]:
            print ' ' +  msg[:-3] + '.' * (31-len(msg[:-3])),
        elif '###' in msg[:3]:
            print msg[3:]
        else:
            print msg
        
        prompt = 'PP>'

        return False
    
    
    
        if mode & PP_PROMPT:
            print prompt,
        if mode & PP_NOEOL:
            print msg,
        else:
            print msg

        return True

    def _pr_err(self, msg, mode=PP_PROMPT):
        ''' Now just print but maybe could be used to log into a file'''
        prompt = 'PP>'
        #print ' PP> ERROR:', msg
        if mode & PP_PROMPT:
            print prompt,
        print ' ERROR:', msg
        return False

    def edmshow(self):
        #=======================================================================
        # Motor screens
        #=======================================================================
        self._pr_log('Open motor screens')
        ppmotors = [self.sPpmPv, self.sYtrPv, self.sXtrPv]
        for mot in ppmotors:
            cmd = '%s/launch-motor.sh %s' % (self.sEDMpp, mot) 
            os.popen(cmd, "r")
                    
        
        # FIXME: remove next line for final release  
        alexd = '/reg/neh/home3/alexd/ioc/common/xip_pp/current/pyscripts/src'
        cmd = 'cd %s ; edm -x -eolc -m MOTOR=%s pp_gui.edl &' % (alexd, self.sPpmPv)
        
        #=======================================================================
        # Burst screen
        #=======================================================================
        # FIXME: Uncomment for final release
        cwd = os.getcwd() # save working directory
        #ppedmloc = self.ppcfg['PP edm gui screen location']
        #cmd = 'cd %s ; edm -x -eolc -m MOTOR=%s motionScreens/pp_gui.edl &' % (ppedmloc, self.sPpmPv)
        ppedmloc = '/reg/neh/home1/paiser/svn-working/ioc/common/xip_pp/current'
        #FIXME add macros for sequencer 
        #macros = (ppedmloc, self.sPpmPv, self.id, self.ecs_ioc, self.mioc)
        pp_launch_script =  'pp_screens/pp_launch_%s.sh' % self.instr.lower()  
        #cmd = 'cd %s ; edm -x -m MOTOR=%s -m ID=%s -m ECS_IOC=%s -m MIOC=%s pp_screens/pp_burst.edl &' % macros
        cmd = 'cd %s ; %s' % (ppedmloc, pp_launch_script)
        ### --------------------------------------------------------------------
        os.popen(cmd, "r") # execute evr script
        os.chdir(cwd) # restore working directory
        #=======================================================================
        # EVR screens
        #=======================================================================
        self._pr_log('Open EVR screens')
        cwd = os.getcwd() # save working directory
        cmd = 'cd %s ; edm -x -eolc -m EVR=%s evrScreens/evr.edl &' % (self.sEDMev, self.sEvrPv)
        os.popen(cmd, "r") # execute evr script
        os.chdir(cwd) # restore working directory

    def iocterm(self):
        cmd1 = 'xterm -e ssh %s &' % self.sSRV
        os.popen(cmd1, "r")
        self._pr_log('Open xterm in IOC server')

    def monitor(self):
        #!/bin/bash
        cmd1  = 'source /reg/neh/home1/dflath/sxr_python/setup_env.sh\n'
        #
        #cd ~/sxrpython_files
        #PS1=""
        #PROMPT_COMMAND=""
        #echo -ne "\033]0;"SXRpython v5"\007"
        #PAGER=more ipython --nobanner  -i -c "%run '/reg/neh/home1/dflath/sxr_python/sxr_python'"
        
        cmd1 += 'xterm -e python ./ppmonitor.py &'
        os.popen(cmd1, "r")
        self._pr_log('Open Picker monitor xterm')

    def status(self):
        if self.sequencer: seq = 'Yes'
        else:                    seq = 'No'
        print  '\n Pulse Picker Current configuration:'
        self._pr_log('EVR delay###')    ; self._pr_log('###' + str(self.evrdelay))
        self._pr_log('Num of shots###') ; self._pr_log('###' + str(self.nshots))
        self._pr_log('Num repeat###')   ; self._pr_log('###' + str(self.repeat))
        self._pr_log('Frequency (Hz)###')    ; self._pr_log('###' + str(self.freq))
        self._pr_log('Sequencer Controlled###') ; self._pr_log('###' + seq) 
        print ''
        self._pr_log('Status###') ; self._pr_log('###' + str(self.sh_status))
#        if not self.sh_status == 'Idle' or :
#            slitpos = self.slitpos
#        else:
#            slitpos = 'Moving'
#            
#        print ' Blades position ...............', slitpos

    def help(self):
        self.verbose = PP_VERBOSE
        print '\n Picker commands\n'
        self._pr_log('Show EDM screens###')        ; self._pr_log('###pp.edmshow()')
        self._pr_log('Open IOC terminal###')       ; self._pr_log('###pp.iocterm()')
        self._pr_log('Reset IOC###')               ; self._pr_log('###pp.iocreset()')
        self._pr_log('Set number of shots###')     ; self._pr_log('###pp.setnshots(<n>)')
        self._pr_log('Set frequency###')           ; self._pr_log('###pp.setfreq(<n>)')
        self._pr_log('Set repeat number###')       ; self._pr_log('###pp.setrepeat(<-1|n>')
        self._pr_log('Set forever###')             ; self._pr_log('###pp.setforever(<True | False>)')
        self._pr_log('Force using sequencer###')   ; self._pr_log('###pp.setusesequencer(<True | False>)')
        self._pr_log('Set EVR delay###')           ; self._pr_log('###pp.setevrdelay(<n>)')
        self._pr_log('Set EVR mode###')            ; self._pr_log('###pp.setevrmode(<nshots>)')
        self._pr_log('Home blades###')             ; self._pr_log('###pp.home()')
        self._pr_log('Open blades###')             ; self._pr_log('###pp.open()')
        self._pr_log('Close blades###')            ; self._pr_log('###pp.close()')
        self._pr_log('Prepare acquisition###')     ; self._pr_log('###pp.prepare()')
        self._pr_log('Start acquisition###')       ; self._pr_log('###pp.start()')
        self._pr_log('Stop acquisition###')        ; self._pr_log('###pp.stop()')
        self._pr_log('Show status###')             ; self._pr_log('###pp.status()')
        self._pr_log('')
        self._pr_log('Set single shot###')         ; self._pr_log('###pp.setsingleshot()')
        self._pr_log('Set frequency reduction###') ; self._pr_log('###pp.setfreqreduction(<Freq>)')
        self._pr_log('Set burst###')               ; self._pr_log('###pp.setburst(<Nshots> | <Nshots>, <Freq>)')
        self._pr_log('This help screen###')        ; self._pr_log('###pp.help()')
        self.verbose = PP_NOVERBOSE

    def _seqsetup(self):
        ''' pp_events['A']['ENA']
            pp_events['A']['EC']
            pp_events['A']['BD']
            pp_events['A']['DESC']
        '''
        dev_event_devices = ['A', 'B', 'C', 'D', '1', '2', '3', '4']
        dev_event_sequence = list()
        self.pp_events = {}
        # load events from UI:
        for ev in dev_event_devices:
            self.pp_events[ev] = {}
            pv = '%s:PP_ENA%s' % (self.sPpmPv, ev)
            self.pp_events[ev]['ENA'] = int(self._caget(pv, PP_NOECHO))
            pv = '%s:PP_EC%s' % (self.sPpmPv, ev)
            self.pp_events[ev]['EC']   = int(self._caget(pv, PP_NOECHO))
            pv = '%s:PP_BD%s' % (self.sPpmPv, ev)
            self.pp_events[ev]['BD']  = int(self._caget(pv, PP_NOECHO))
            pv = '%s:PP_EC%s.DESC' % (self.sPpmPv, ev)
            self.pp_events[ev]['DESC']  = self._caget(pv, PP_NOECHO)
                        
        for ev in dev_event_devices:
            if self.pp_events[ev]['ENA']:
                evcode, tbeam = (self.pp_events[ev]['EC'], self.pp_events[ev]['BD'])
                dev_event_sequence.append((evcode, tbeam))

        for i, idata in enumerate(dev_event_sequence):
            self._pr_log('%02d %4s %8s' % (i, str(idata[0]), str(idata[1])))
            print '%02d %4s %8s' % (i, str(idata[0]), str(idata[1]))

        return dev_event_sequence
    
    def _init_pp_events(self):
        dev_event_devices = ['A', 'B', 'C', 'D', '1', '2', '3', '4']
        self.pp_events = {}
        for ev in dev_event_devices:
            self.pp_events[ev] = {}
            self.pp_events[ev]['ENA']  = '0'
            self.pp_events[ev]['EC']   = '0'
            self.pp_events[ev]['BD']   = '0'
            self.pp_events[ev]['DESC'] = ''

    def _read_pp_events_set(self, setn):
        dev_event_devices = ['A', 'B', 'C', 'D', '1', '2', '3', '4']
        self.pp_events = {}
        for ev in dev_event_devices:
            self.pp_events[ev] = {}
            self.pp_events[ev]['ENA']  = '0'
            self.pp_events[ev]['EC']   = '0'
            self.pp_events[ev]['BD']   = '0'
            self.pp_events[ev]['DESC'] = ''

        
    def _getevpresets(self):
        preset1 = int(self._caget('%s:PP_PRESET1' % self.sPpmPv, PP_NOECHO))
        preset2 = int(self._caget('%s:PP_PRESET2' % self.sPpmPv, PP_NOECHO))
        preset3 = int(self._caget('%s:PP_PRESET3' % self.sPpmPv, PP_NOECHO))
        preset4 = int(self._caget('%s:PP_PRESET4' % self.sPpmPv, PP_NOECHO))
        preset5 = int(self._caget('%s:PP_PRESET5' % self.sPpmPv, PP_NOECHO))
        return [preset1, preset2, preset3, preset4, preset5]
    
    def _saveevpresets(self, evsets):
        ''' evsets = [1,0,0,0,0] => means saves set 1
            evsets = [0,0,1,0,0] => means saves set 3
            self.setscfgfilename = '~/.evset%d.cfg'            
        '''
        if sum(evsets) > 1:
            self._pr_err('Cannot save multiple sets. Aborting save!', PP_NOPROMPT)
            return False
        for setn, evset in enumerate(evsets):
            if evset:
                fname = self.setscfgfilename % (setn + 1)
                f = open(fname, "w")
                self._pr_log(' Event Set n.%d' % (setn + 1) + '###')
                for k in ['A','B','C', 'D', '1', '2', '3', '4']:
                    pv = '%s:PP_EC%s.DESC' % (self.sPpmPv, k)
                    f.write("ECDESC%s   " % k + ''.join(self._caget(pv, PP_NOECHO))  + "\n")
                    pv = '%s:PP_EC%s'      % (self.sPpmPv, k) 
                    f.write("EC%s       " % k  + str(self._caget(pv, PP_NOECHO))  + "\n")
                    pv = '%s:PP_BD%s'      % (self.sPpmPv, k)
                    f.write("BD%s       " % k  + str(self._caget(pv, PP_NOECHO))  + "\n")
                    pv = '%s:PP_ENA%s'     % (self.sPpmPv, k)
                    f.write("ENA%s      " % k  + str(self._caget(pv, PP_NOECHO))  + "\n")
                f.close()
                self._pr_log('###saved')
                print '  File:', fname
                #pv = '%s:PP_PRESET%d' % (self.sPpmPv, setn)
                #self._caput(pv , 0, PP_NOECHO)
                
        
    def _loadevpresets(self, evsets):
        ''' evsets = [1,0,0,0,0] => means loads set 1
            evsets = [0,0,1,0,0] => means loads set 3
        '''
        self.cfg = cfginfo()
        for setn, evset in enumerate(evsets):
            if evset:
                fname = self.setscfgfilename % (setn + 1)
                #print 'fname', fname
                if self.cfg.read(fname):
                    self._pr_log(' Event Set n.%d' % (setn + 1) + '###')
                    val = self.cfg.ECDESCA; pv = '%s:PP_ECA.DESC' % self.sPpmPv
                    if type(val) == list:
                        val = ' '.join(self.cfg.ECDESCA)
                    #if self.pp_events['A']['DESC'] != val:
                    self._caput(pv , str(val), PP_NOECHO)
                    val = self.cfg.ECA; pv = '%s:PP_ECA'          % self.sPpmPv
                    #if self.pp_events['A']['EC'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.BDA; pv = '%s:PP_BDA'          % self.sPpmPv
                    #if self.pp_events['A']['BD'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.ENAA; pv = '%s:PP_ENAA'        % self.sPpmPv
                    #if self.pp_events['A']['ENA'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    #===========================================================
                    # Picker (User Cannot Change)
                    #===========================================================
                    #val = self.cfg.ECDESCB; pv = '%s:PP_ECB.DESC' % self.sPpmPv
                    #if type(val) == list:
                    #    val = ' '.join(self.cfg.ECDESCB)
                    #if self.pp_events['B']['DESC'] != val:
                    #    self._caput(pv , str(val), PP_NOECHO)
                    pv = '%s:PP_ECB.DESC' % self.sPpmPv
                    self._caput(pv , 'Picker', PP_NOECHO)
                    val = self.cfg.ECB; pv = '%s:PP_ECB'          % self.sPpmPv
                    #if self.pp_events['B']['EC'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.BDB; pv = '%s:PP_BDB'          % self.sPpmPv
                    #if self.pp_events['B']['BD'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.ENAB; pv = '%s:PP_ENAB'        % self.sPpmPv
                    #if self.pp_events['B']['ENA'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    #===========================================================
                    val = self.cfg.ECDESCC; pv = '%s:PP_ECC.DESC' % self.sPpmPv
                    if type(val) == list:
                        val = ' '.join(self.cfg.ECDESCC)
                    #if self.pp_events['C']['DESC'] != val:
                    self._caput(pv , str(val), PP_NOECHO)
                    val = self.cfg.ECC; pv = '%s:PP_ECC'          % self.sPpmPv
                    #if self.pp_events['C']['EC'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.BDC; pv = '%s:PP_BDC'          % self.sPpmPv
                    #if self.pp_events['C']['BD'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.ENAC; pv = '%s:PP_ENAC'        % self.sPpmPv
                    #if self.pp_events['C']['ENA'] != val:
                    self._caput(pv , int(val), PP_NOECHO)

                    val = self.cfg.ECDESCD; pv = '%s:PP_ECD.DESC' % self.sPpmPv
                    if type(val) == list:
                        val = ' '.join(self.cfg.ECDESCD)
                    #if self.pp_events['D']['DESC'] != val:
                    self._caput(pv , str(val), PP_NOECHO)
                    val = self.cfg.ECD; pv = '%s:PP_ECD'          % self.sPpmPv
                    #if self.pp_events['D']['EC'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.BDD; pv = '%s:PP_BDD'          % self.sPpmPv
                    #if self.pp_events['D']['BD'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.ENAD; pv = '%s:PP_ENAD'        % self.sPpmPv
                    #if self.pp_events['D']['ENA'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                
                    val = self.cfg.ECDESC1; pv = '%s:PP_EC1.DESC' % self.sPpmPv
                    if type(val) == list:
                        val = ' '.join(self.cfg.ECDESC1)
                    #if self.pp_events['1']['DESC'] != val:
                    self._caput(pv , str(val), PP_NOECHO)
                    val = self.cfg.EC1; pv = '%s:PP_EC1'          % self.sPpmPv
                    #if self.pp_events['1']['EC'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.BD1; pv = '%s:PP_BD1'          % self.sPpmPv
                    #if self.pp_events['1']['BD'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.ENA1; pv = '%s:PP_ENA1'        % self.sPpmPv
                    #if self.pp_events['1']['ENA'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                
                    val = self.cfg.ECDESC2; pv = '%s:PP_EC2.DESC' % self.sPpmPv
                    if type(val) == list:
                        val = ' '.join(self.cfg.ECDESC2)
                    #if self.pp_events['2']['DESC'] != val:
                    self._caput(pv , str(val), PP_NOECHO)
                    val = self.cfg.EC2; pv = '%s:PP_EC2'          % self.sPpmPv
                    #if self.pp_events['2']['EC'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.BD2; pv = '%s:PP_BD2'          % self.sPpmPv
                    #if self.pp_events['2']['BD'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.ENA2; pv = '%s:PP_ENA2'        % self.sPpmPv
                    #if self.pp_events['2']['ENA'] != val:
                    self._caput(pv , int(val), PP_NOECHO)

                    val = self.cfg.ECDESC3; pv = '%s:PP_EC3.DESC' % self.sPpmPv
                    if type(val) == list:
                        val = ' '.join(self.cfg.ECDESC3)                    
                    #if self.pp_events['3']['DESC'] != val:
                    self._caput(pv , str(val), PP_NOECHO)
                    val = self.cfg.EC3; pv = '%s:PP_EC3'          % self.sPpmPv
                    #if self.pp_events['3']['EC'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.BD3; pv = '%s:PP_BD3'          % self.sPpmPv
                    #if self.pp_events['3']['BD'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.ENA3; pv = '%s:PP_ENA3'        % self.sPpmPv
                    #if self.pp_events['3']['ENA'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                
                    val = self.cfg.ECDESC4; pv = '%s:PP_EC4.DESC' % self.sPpmPv
                    if type(val) == list:
                        val = ' '.join(self.cfg.ECDESC4)
                    #if self.pp_events['4']['DESC'] != val:
                    self._caput(pv , str(val), PP_NOECHO)
                    val = self.cfg.EC4; pv = '%s:PP_EC4'          % self.sPpmPv
                    #if self.pp_events['4']['EC'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.BD4; pv = '%s:PP_BD4'          % self.sPpmPv
                    #if self.pp_events['4']['BD'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    val = self.cfg.ENA4; pv = '%s:PP_ENA4'        % self.sPpmPv
                    #if self.pp_events['4']['ENA'] != val:
                    self._caput(pv , int(val), PP_NOECHO)
                    
                    self._pr_log('###loaded')
                else:
                    pass
                self.cfg = None
                
                #pv = '%s:PP_PRESET%d' % (self.sPpmPv, setn)
                #self._caput(pv , 0, PP_NOECHO)

#===============================================================================
# For tests purposes only
#===============================================================================
    
def pressforcommand(msg, callback=None, arg=None):
    
    if arg == None:
        prompt = ' ' + msg + ' ' + '.' * (65-len(msg)) + ' [y/N] '
    else:
        prompt = ' ' + msg + ' ' + '.' * (65-len(msg)) + ' [%s] ' % arg
    vv = raw_input(prompt)
    
    if vv == '.':
        sys.exit(0)
    elif vv == '': # get the default value
        vv = str(arg)
    else:
        pass
    
    vv = vv.capitalize()
    
    if arg !=  None:
        if vv.isdigit():
            vv = int(vv)
        elif 'False' in vv: 
            vv = False
        elif 'True'  in vv: 
            vv = True
        return callback(vv)
    else:
        if vv == 'Y':
            return callback()
    return False

def xxxbeamline_read(instr):
    ppcfg = {}
    instr = instr.lower()
    if os.getcwd().split('/')[-1] != instr:
        return False
    f = open('%sbeamline.py' % instr, 'r')
    lines = f.readlines()
    for line in lines:
        if 'ppcfg' in line:
            if '= {}' in line:
                continue
            if '[' in line:
                kv = line.split('=')
                key = kv[0].replace('ppcfg[\'','').replace('\']','').rstrip()
                val = kv[1].replace('\'','').split('#')[0].strip().replace('\n','')
                ppcfg[key] = str(val)
                
    f.close()
    ppcfg['Current working directory']  = os.getcwd()
    
    return ppcfg

if __name__ == '__main__':
    
#    if len(sys.argv) > 1:
#        for i in range(len(sys.argv)):
#            print i, sys.argv[i]
#    sys.exit(1)
#    
    
    
    ppcfg = xxxbeamline_read('mec')
    
    for i, (k,v) in enumerate(ppcfg.iteritems()):
        print '%02d, %-40s %-30s' % (i+1, repr(k), repr(v))
    
    #===========================================================================
    # Last saved settings location: 
    # XPP: /reg/neh/operator/xppopr/.pp_xpp
    # SXR: /reg/neh/operator/sxropr/.pp_sxr
    # CXI: /reg/neh/operator/cxiopr/.pp_cxi
    # MEC: /reg/neh/operator/mecopr/.pp_mec
    #===========================================================================

    #===========================================================================
    # Main Application
    #===========================================================================
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--save':
            PPicker(ppcfg, save=True)
        elif sys.argv[1] == '--load':
            PPicker(ppcfg, load=True)
        sys.exit(0)
    autostart = True
    pp = PPicker(ppcfg, autostart=autostart)
    
    
    sys.exit(1)
    #===========================================================================
    # Dummy test
    #===========================================================================
    print 'Dummy test'
    pp.monitor()
    sys.exit(1)
    #===========================================================================
    # End Dummy test
    #===========================================================================
    
    
    print '\n Testing Picker commands (Press \'.\' to quit, Enter to default)\n'
    
    pressforcommand('Show EDM screens',          pp.edmshow)
    pressforcommand('Open IOC terminal',         pp.iocterminal)
    pressforcommand('Stop picker',               pp.stop)    
    pressforcommand('Reset IOC',                 pp.iocreset)
    pressforcommand('Set number of shots',       pp.setnshots, 1)
    pressforcommand('Set frequency',             pp.setfreq, 120)
    pressforcommand('Set repeat number to 1',    pp.setrepeat, 1)
    pressforcommand('Set forever',               pp.setforever, True)
    pressforcommand('Set forever',               pp.setforever, False)    
    pressforcommand('Show volatil user message', pp.pstatus, 'This is a user message')
    pressforcommand('Force using sequencer',     pp.setusesequencer, True)
    pressforcommand('Force using sequencer',     pp.setusesequencer, False)
    pressforcommand('Set EVR delay',             pp.setevrdelay, 5300)
    pressforcommand('Set EVR delay',             pp.setevrdelay, 0)
    pressforcommand('Start picker',              pp.start)
    pressforcommand('Open blades',               pp.open)
    pressforcommand('Close blades',              pp.close)
    pressforcommand('Checking boundaries',       pp.setcheckbounds, True)
    pressforcommand('Checking boundaries',       pp.setcheckbounds, False)
    pressforcommand('Align blades',              pp.align)
    pressforcommand('Quit Picker APP',           pp.quit)
    sys.exit(0)
