#! /bin/env python
import sys, os, errno
from PyQt4 import QtGui, QtCore, uic
from options import Options
import pyca
from Pv import Pv
import time
import threading
from pp import PPicker


MOTION_SCREENS_PATH = '/reg/neh/home1/paiser/working/ioc/common/xip_pp/current/pyscripts/src'
PP_SIOC_STARTUP = '/reg/d/iocCommon/sioc/ioc-sxr-trigger-ims/startup.cmd'
EPICS_BASE = '/reg/g/pcds/package/epics/3.14/modules/pcds_motion/R2.3.4'
EVR_SCREENS_PATH = './'

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
form_class, base_class = uic.loadUiType('ui/pp_base.ui')
class PPGui(QtGui.QWidget, form_class):    
    '''Pulse Picker Graphical User Interface'''
    def __init__(self, ppcfg, app, parent=None):
        super(PPGui, self).__init__(parent)
        self.setupUi(self)
            
        self.tB_expert.setArrowType(QtCore.Qt.DownArrow)
        self.l_led.fileName    = None
        self.l_led.oldfileName = None
        self.edmppmlockfile    = '/tmp/edmppm.lock'
        self.edmevrlockfile    = '/tmp/demevr.lock'
        self.tlhioclockfile    = '/tmp/tlhioc.lock'

        self._set_led('OFF')
        self.msgbuffer = ''

        # initial geometry:
        self.fr_expert.hide()
        self.minheight = self.sizeHint().height()
        #Load layout settings.
        self.settings = QtCore.QSettings("pp_base", "Paiser")
        if self.settings.contains("Geometry"):
            self.restoreGeometry(self.settings.value("Geometry").toByteArray())
            if self.height() > self.minheight:
                self.fr_expert.show()
                self.tB_expert.setArrowType(QtCore.Qt.UpArrow)  # contract
        self.setMaximumSize(16777215,16777215)
        self.setMinimumSize(0,0)
        self.blink = True
        self.blinker = False
        self._initActions()
        # Load the Pulse Picker Class
        self.pp = PPicker(ppcfg, app, self)
        self.getConfig()        # retrieves settings saved since last time
        self.repaint()
        
    def _initActions(self):
        qsig   = QtCore.SIGNAL
        sig0   = qsig("clicked()")
        sig2   = qsig("valueChanged(int)")
#        sig3   = qsig("currentIndexChanged(int)")
#        sig4   = qsig("par_upd(int, QVariant, QVariant)")
#        sig5   = qsig("returnPressed()")
#        sig6   = qsig("onUpdateRate(int, float, float)")
#        sig7   = qsig("stateChanged()")
#        sig8   = qsig("setCameraCombo(int)")
#        sig9   = qsig("topLevelChanged(bool)")
#        sig10  = qsig("insertMarker(int, int, int)")
        
        # vars stored in config file:
        self.connect(self.cB_forever,  sig0, self._forever)
        self.connect(self.sB_repeat,   sig2, self._repeat)
        self.connect(self.sB_nshots,   sig2, self._nshots)
        self.connect(self.sB_freq,     sig2, self._freq)
        self.connect(self.rB_auto,     sig0, self._auto)
        self.connect(self.rB_open,     sig0, self._open)
        self.connect(self.rB_close,    sig0, self._close)
        self.connect(self.pB_iocres,   sig0, self._iocres)
        self.connect(self.sB_evrdelay, sig2, self._evrdelay)
        # only actions (user zone):
        self.connect(self.pB_start,    sig0, self._start)
        self.connect(self.pB_stop,     sig0, self._stop)
        self.connect(self.tB_expert,   sig0, self._expert)

        # only action (expert zone):
        self.connect(self.rB_align,    sig0, self._align)
        self.connect(self.cB_chkbounds,sig0, self._imscheckbounds)
        self.connect(self.pB_clear,    sig0, self.pT_log.clear)
        self.connect(self.cB_sequencer,sig0, self._initSequencer)
        self.connect(self.pB_quit,     sig0, self._quit)
        #TODO from here
        self.connect(self.pB_edmppm,   sig0, self._edmppm)
        self.connect(self.pB_edmevr,   sig0, self._edmevr)
        self.connect(self.pB_iocppm,   sig0, self._tlhioc)
        
        self.lblinkTimer = QtCore.QTimer()        
        self.connect(self.lblinkTimer, QtCore.SIGNAL("timeout()"), self._ledblink)
        
        #-------------------------------------------- Non graphical connections:
        self.connect(self.pp, QtCore.SIGNAL("_set_led(QString)"), self._set_led)
        self.connect(self.pp, QtCore.SIGNAL("_setText(QString, QString))"), self._setText)
        self.connect(self.pp, QtCore.SIGNAL("_setWidget(QString, QString))"), self._setWidget)
        self.connect(self.pp, QtCore.SIGNAL("_pr_log(QString, QString)"), self._pr_log)
        self.connect(self.pp, QtCore.SIGNAL("_pr_err(QString, QString)"), self._pr_err)
        
        # Timer connections:
        self.lblinkTimer.start(500)
        self.l_status.setText('')
        
    def _setText(self, widget, msg):
        if widget == 'status':
            self.l_status.setText(msg)
        
    def _setWidget(self, action, name):
        '''Sets GUI widget values and status'''
        enadis = {'enable': True, 'disable': False}
        chknck = {'check' : True, 'uncheck': False}
        sbname = ('evrdelay', 'repeat', 'freq', 'nshots')
        
        if action in enadis.keys():
            if   name == 'align':
                widget = self.rB_align.setEnabled    ; val = enadis[action] 
            elif name == 'auto':
                widget = self.rB_auto.setEnabled     ; val = enadis[action]
            elif name == 'open':
                widget = self.rB_open.setEnabled     ; val = enadis[action]
            elif name == 'close':
                widget = self.rB_close.setEnabled    ; val = enadis[action]
            elif name == 'forever':
                widget = self.cB_forever.setEnabled  ; val = enadis[action]
            elif name == 'evrdelay':
                widget = self.sB_evrdelay.setEnabled ; val = enadis[action] 
            elif name == 'repeat':
                widget = self.sB_repeat.setEnabled   ; val = enadis[action]
            elif name == 'freq':
                widget = self.sB_freq.setEnabled     ; val = enadis[action]
            elif name == 'start':
                widget = self.pB_start.setEnabled    ; val = enadis[action]
            elif name == 'stop':
                widget = self.pB_stop.setEnabled     ; val = enadis[action]
            else:
                return False
        elif action in chknck.keys() or action in sbname:
            if   name == 'align':
                widget = self.rB_align.setChecked     ; val = chknck[action]
            elif name == 'auto':
                widget = self.rB_auto.setChecked      ; val = chknck[action]
            elif name == 'open':
                widget = self.rB_open.setChecked      ; val = chknck[action]
            elif name == 'close':
                widget = self.rB_close.setChecked     ; val = chknck[action]
            elif name == 'forever':
                widget = self.cB_forever.setChecked   ; val = chknck[action]
            elif name == 'chkbounds':
                widget = self.cB_chkbounds.setChecked ; val = chknck[action]
            else:
                try:
                    val = int(name)
                    if action == 'evrdelay':
                        widget = self.sB_evrdelay.setValue
                    elif action == 'repeat':
                        widget = self.sB_repeat.setValue
                    elif action == 'freq':
                        widget = self.sB_freq.setValue
                    elif action == 'nshots':
                        widget = self.sB_nshots.setValue
                except:
                    return False
        else:
            return False
        widget(val)

    def _set_led(self, status):
        if   status.upper() == 'RED':
            pixmap = 'ui/ledred16x16.png'
        elif status.upper() == 'GREEN':
            pixmap = 'ui/ledgreen16x16.png'
        elif status.upper() == 'OFF':
            pixmap = 'ui/ledoff16x16.png'
        elif status.upper() == 'ON':
            pixmap = 'ui/ledgreen16x16.png'
        elif status.upper() == 'FAIL':
            pixmap = 'ui/ledred16x16.png'
        else:
            return False
        if self.l_led.fileName:
            self.l_led.oldfileName = self.l_led.fileName
        self.l_led.setPixmap(QtGui.QPixmap(pixmap))
        self.l_led.fileName = pixmap
        return True
        
    def closeEvent(self, event):
        """Save MainWindow layout settings."""
        self.settings.setValue("Geometry", QtCore.QVariant(self.saveGeometry()))
        self._quit()
        #self.settings.setValue("windowState", QtCore.QVariant(self.fr_expert.saveState()))      
        #self.settings.setValue('size', self.size())
        #event.accept()

    def _start(self):
        self.pp.start()

    def _stop(self):
        self.pp.stop()
        
    def _quit(self):
        self._remotelockfiles()
        self.close()

    def _initSequencer(self):
        sequencer = self.cB_sequencer.isChecked()
        if self.pp.sequencer == sequencer:
            return False
        self.pp._initSequencer()

    def _forever(self):
        forever = self.cB_forever.isChecked()
        if self.pp.forever == forever:
            return False
        self.pp.setforever(forever)

    def _repeat(self):
        repeat = self.sB_repeat.value()
        if self.pp.repeat == repeat:
            return False
        self.pp.setrepeat(repeat)

    def _nshots(self):
        nshots = self.sB_nshots.value()
        if self.pp.nshots == nshots:
            return False
        self.pp.setnshots(nshots)

    def _freq(self):
        freq = self.sB_freq.value()
        if self.pp.freq == freq:
            return False
        self.pp.setfreq(freq)

    def _auto(self):
        self.pp.setauto()
        self._ena_pars()
        
    def _open(self):
        self.pp.open()

    def _close(self):
        self.pp.close()

    def _iocres(self):
        self.pp.iocreset()
        
    def _evrdelay(self):
        evrdelay = self.sB_evrdelay.value()
        if self.pp.evrdelay == evrdelay:
            return False
        self.pp.setevrdelay(evrdelay)

    def _expert(self):
        if self.sizeHint().height() > self.minheight:
            self.tB_expert.setArrowType(QtCore.Qt.DownArrow)  # contract
            self.fr_expert.hide()
        else:
            if self.showDialog('Access'): # expand with password
                self.tB_expert.setArrowType(QtCore.Qt.UpArrow)
                self.fr_expert.show()
            
        self.setFixedSize(self.sizeHint())
        self.setMaximumSize(16777215,16777215)
        self.setMinimumSize(0,0)

    def _align(self):
        self.pp.align()

    def _imscheckbounds(self):
        ''' Enable/Disable picker position check'''
        chkbounds = self.cB_chkbounds.isChecked()
        if self.pp.chkbounds == chkbounds:
            return False
        self.pp.setcheckbounds(self.cB_chkbounds.isChecked())

    def _edmppm(self):
        
        if not self._createlockfile():
            
            print '   Another instance of this script is running.'
            print '   Close it before starting a new one or',
            print 'remove the file %slock' % self.edmppmlockfile
            sys.exit(-1)
        self._createlockfile(self.edmppmlockfile)
        if self.edm_ppm:
            self._pr_err('Motor screens already open')
            #return False
        # Open Pulse Selector EDM screens
        cmd1 = '%s/%s %s %s %s' % (MOTION_SCREENS_PATH, self.sSPP, self.sPpmPv, self.sYtrPv, self.sXtrPv)
        os.popen(cmd1, "r")
        self.edm_ppm = True
        self._pr_log('Open motor screens')
        return self.edm_ppm

    def _edmevr(self):
        
        if not self._createlockfile():
            print '   Another instance of this script is running.'
            print '   Close it before starting a new one or',
            print 'remove the file %slock' % self.edmevrlockfile
            sys.exit(-1)
        self._createlockfile(self.edmevrlockfile)
        if self.edm_evr:
            self._pr_err('EVR screens already open')
            #return False
        # Open Pulse Selector EDM screen
        cmd1 = '%s/%s %s &' % (EVR_SCREENS_PATH, self.sSEV, self.sEvrPv)
        os.popen(cmd1, "r")
        self.edm_evr = True
        self._pr_log('Open EVR screens')
        return self.edm_evr

    def _tlhioc(self):

        if not self._createlockfile():
            print '   Another instance of this script is running.'
            print '   Close it before starting a new one or',
            print 'remove the file %slock' % self.tlhioclockfile
            sys.exit(-1)        
        self._createlockfile(self.tlhioclockfile)    
        if self.srv_open:
            self._pr_err('IOC server xterm already open')
            #return False
        # TODO way to find the port to telnet
        cmd1 = 'xterm -e ssh %s &' % self.sSRV
        os.popen(cmd1, "r")
        self.srv_open = True
        self._pr_log('Open xterm in IOC server')
        return self.srv_open

    def _createlockfile(self, lockfilename):
        if not os.path.isfile(lockfilename):
            open(lockfilename + '.' + 'lock', "w").close()
            return True
        return False
    
    def _remotelockfile(self, lockfilename):
        try:
            os.remove(lockfilename)
        except OSError, e:
            if e.errno != errno.ENOENT:
                raise

    def _remotelockfiles(self):
        if self.edmppmlockfile:
            self._remotelockfile(self.edmppmlockfile)
        if self.edmevrlockfile:            
            self._remotelockfile(self.edmevrlockfile)
        if self.tlhioclockfile:
            self._remotelockfile(self.tlhioclockfile)


    def _ledblink(self):
        if self.blinker:
            if self.blink:
                if   'ledgreen' in self.l_led.oldfileName:
                    self._set_led('ON')
                elif 'ledred' in self.l_led.oldfileName:
                    self._set_led('FAIL')
                self.blink = False
            else:
                self._set_led('OFF')
                self.blink = True

    def _ena_pars(self):
        self._set_pars(True)
        
    def _dis_pars(self):
        self._set_pars(False)

    def _set_pars(self, status):
        self.gB_ppsel.setEnabled(status)

    def _pr_log(self, msg, eol=True):
        
        if eol:
            self.pT_log.append(self.msgbuffer + msg)
            self.msg = ''
        else:
            self.msgbuffer += msg

    def _pr_err(self, msg, eol=True):
        # save setttings    
        fw = self.pT_log.fontWeight()
        tc = self.pT_log.textColor()
        cf = self.pT_log.currentCharFormat()
        self.pT_log.setTextColor(QtGui.QColor('red'))
        self._pr_log(msg, eol)
        # restore settings
        self.pT_log.setFontWeight(fw)
        self.pT_log.setTextColor(tc)
        self.pT_log.setCurrentCharFormat(cf)

    def getConfig(self):
        if self.pp.ppCfgFname == None:
            return
        self.cfg = cfginfo()
        if self.cfg.read(self.pp.cfgdir + self.pp.ppCfgFname):
            if self.sB_repeat.value() != int(self.cfg.repeat):
                self.sB_repeat.setValue(int(self.cfg.repeat))
            if self.sB_nshots.value() != int(self.cfg.nshots):
                self.sB_nshots.setValue(int(self.cfg.nshots))
            if self.sB_freq.value() != int(self.cfg.frequency):
                self.sB_freq.setValue(int(self.cfg.frequency))
            if self.sB_evrdelay.value() != int(self.cfg.evrdelay):
                self.sB_evrdelay.setValue(int(self.cfg.evrdelay))
            if self.cB_forever.isChecked() != int(self.cfg.forever):
                self.cB_forever.setChecked(int(self.cfg.forever))
            if self.cB_sequencer.isChecked() != int(self.cfg.sequencer):
                self.cB_sequencer.setChecked(int(self.cfg.sequencer))
            if self.cB_chkbounds.isChecked() != int(self.cfg.chkbounds):
                self.cB_chkbounds.setChecked(int(self.cfg.chkbounds))
            if self.rB_auto.isChecked() != int(self.cfg.auto):
                self.rB_auto.setChecked(int(self.cfg.auto))
                self.gB_ppsel.setEnabled(True)
            if self.rB_open.isChecked() != int(self.cfg.open):
                self.rB_open.setChecked(int(self.cfg.open))
                self.gB_ppsel.setEnabled(False)
            if self.rB_close.isChecked() != int(self.cfg.close):
                self.rB_close.setChecked(int(self.cfg.close))
                self.gB_ppsel.setEnabled(False)
            if self.IMS_VM != self.cfg.vm:
                self.IMS_VM = self.cfg.vm
            if self.IMS_VI != self.cfg.vi:
                self.IMS_VI = self.cfg.vi
            if self.IMS_A != self.cfg.a:
                self.IMS_A = self.cfg.a
            if self.IMS_D != self.cfg.d:
                self.IMS_D = self.cfg.d
        else:
            pass
        self.cfg = None


    def showDialog(self, dlg_type):
        return True
        if dlg_type == 'Access':
            text, ok = QtGui.QInputDialog.getText(self, 'Security Access', 'Password')
            if ok:
                if text == 'swordfish':
                    return True
        else:
            return False
        return False
            
                        
if __name__ == '__main__':
    cwd = os.getcwd()
    
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
    '''
    #===========================================================================
    # Main Application
    #===========================================================================
    ppcfg = sys.argv[1]
    print 'ppcfg', ppcfg
    
    app   = QtGui.QApplication([''])
    app.setStyle('Cleanlooks')
    app.setPalette(app.style().standardPalette())
    #gui = PPGui(app, cwd, options.instrument, ppLstFname, cfgdir)
    gui = PPGui(ppcfg, app)
    gui.show()
    sys.exit(app.exec_())
