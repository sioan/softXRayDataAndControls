#! /bin/env python
import sys, os
'''
Class to read Pulse Selector configuration file and initialize EVR settings.
'''

class PPConfig():
    def __init__(self, instr=None, EVRchannel=2, ppLstFname='pvlist.lst', parent=None):
        #=======================================================================
        # Instrument and File Name setup
        #=======================================================================
        self.instr      = instr
        self.ppLstFname = ppLstFname
        #=======================================================================
        # EVR setup
        #=======================================================================
        self.EVRchannel = EVRchannel
        self.EVR = {}
        self.readconfig_done = False
        self.sEvrPv         = None
        
        #=======================================================================
        # PV's and other parameters'
        #=======================================================================
        self.sSeqPv  = None; self.sSeqDesc = None
        self.sPlyPv  = None; self.sPlyDesc = None
        self.sEvrPv  = None; self.sEvrDesc = None
        self.sPpmPv  = None; self.sPpmDesc = None
        self.sYtrPv  = None; self.sYtrDesc = None
        self.sXtrPv  = None; self.sXtrDesc = None
        self.sIOC    = None; self.sIOCDesc = None
        self.sSPP    = None; self.sSPPDesc = None
        self.sSEV    = None; self.sSEVDesc = None
        self.sSRV    = None; self.sSRVDesc = None
        self.sEVB    = None; self.sEVBDesc = None
        self.sEVS    = None; self.sEVSDesc = None

    def PPread(self):
        ''' Reads pvlist.lst file, load pvs.
            # ---------------------------------------------------------------
            # Pulse Selector Description File
            # ---------------------------------------------------------------
            # Syntax:
            #   <TYPE>, <PVNAME|IOCNAME|SCRIPT>, <DESC> # some_more_comments
            # Where:
            #   <Type>    : "SEQ" -> Sequencer
            #               "EVR" -> EVR associated to sequencer
            #               "PPM" -> Pulse Selector
            #               "IOC" -> Motor and Pulse Selector Server
            #               "EDM" -> EDM screens
            #   <PVNAME>  : PV base name
            #   <IOCNAME> : Server name associated to Pulse Selector PVs
            #   <DESC>    : User description
            # Notes:
            #   PVNAME or IOCNAME are not case sensitive.
            #   Line can be commented out by starting with '#' character.
            # ---------------------------------------------------------------
        '''
        cfgdir = os.getenv("HOME")
        ppLstFname = cfgdir + '/.pp_%s' % self.instr + "/" + self.ppLstFname
        print '  Using pvlist: %s' % ppLstFname
        try:
            lppListLine = open(ppLstFname,"r").readlines()
            
            for line in lppListLine:
                line = line.lstrip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                if line.startswith("SEQ"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sSeqPv = lsLine[1].strip()
                    sSeqPv = sSeqPv.upper()
                    if len(lsLine) >= 3:
                        sSeqDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sSeqDesc = sSeqPv
                    self.sSeqPv   = sSeqPv
                    self.sSeqDesc = sSeqDesc
                elif line.startswith("PLY"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sPlyPv = lsLine[1].strip()
                    sPlyPv = sPlyPv.upper()
                    if len(lsLine) >= 3:
                        sPlyDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sPlyDesc = sPlyPv
                    self.sPlyPv   = sPlyPv
                    self.sPlyDesc = sPlyDesc
                elif line.startswith("EVR"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sEvrPv = lsLine[1].strip()
                    sEvrPv = sEvrPv.upper()
                    if len(lsLine) >= 3:
                        sEvrDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sEvrDesc = sEvrPv
                    self.sEvrPv   = sEvrPv
                    self.sEvrDesc = sEvrDesc
                elif line.startswith("PPM"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sPpmPv = lsLine[1].strip()
                    sPpmPv = sPpmPv.upper()
                    if len(lsLine) >= 3:
                        sPpmDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sPpmDesc = sPpmPv
                    self.sPpmPv   = sPpmPv
                    self.sPpmDesc = sPpmDesc
                elif line.startswith("YTR"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sYtrPv = lsLine[1].strip()
                    sYtrPv = sYtrPv.upper()
                    if len(lsLine) >= 3:
                        sYtrDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sYtrDesc  = sYtrPv
                    self.sYtrPv   = sYtrPv
                    self.sYtrDesc = sYtrDesc
                elif line.startswith("XTR"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sXtrPv = lsLine[1].strip()
                    sXtrPv = sXtrPv.upper()
                    if len(lsLine) >= 3:
                        sXtrDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sXtrDesc  = sXtrPv
                    self.sXtrPv   = sXtrPv
                    self.sXtrDesc = sXtrDesc
                elif line.startswith("IOC"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sIOC = lsLine[1].strip()
                    sIOC = sIOC.lower()
                    if len(lsLine) >= 3:
                        sIOCDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sIOCDesc = sIOC
                    self.sIOC     = sIOC
                    self.sIOCDesc = sIOCDesc
                elif line.startswith("SPP"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sSPP = lsLine[1].strip()
                    if len(lsLine) >= 3:
                        sSPPDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sSPPDesc = sSPP
                    self.sSPP     = sSPP
                    self.sSPPDesc = sSPPDesc
                elif line.startswith("SEV"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sSEV = lsLine[1].strip()
                    if len(lsLine) >= 3:
                        sSEVDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sSEVDesc = sSEV
                    self.sSEV     = sSEV
                    self.sSEVDesc = sSEVDesc
                elif line.startswith("SRV"):
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sSRV = lsLine[1].strip()
                    if len(lsLine) >= 3:
                        sSRVDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sSRVDesc = sSRV
                    self.sSRV     = sSRV
                    self.sSRVDesc = sSRVDesc
                elif line.startswith("EVB"):
                    # EVR burst mode code and hutch dependent delay (ms)
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sEVB = lsLine[1].strip()
                    if len(lsLine) >= 3:
                        sEVBDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sEVBDesc = sEVB
                    self.sEVB     = sEVB
                    self.sEVBDesc = sEVBDesc
                elif line.startswith("EVS"):
                    # EVR single mode code and hutch dependent shot delay (ms)
                    lsLine = line.split(",")
                    if len(lsLine) < 2:
                        print throw("")
                    sEVS = lsLine[1].strip()
                    if len(lsLine) >= 3:
                        sEVSDesc = lsLine[2].strip().split('#')[0].rstrip()
                    else:
                        sEVSDesc = sEVS
                    self.sEVS     = sEVS
                    self.sEVSDesc = sEVSDesc
                else:
                    continue
        except:
            print '!! Failed to read motor pv list from \"%s\"' % ppLstFname
            return False
#        try:
#            print 40 * '-'
#            print 'SEQ Pv %s' % self.sSeqPv
#            print 'PLY Pv %s' % self.sPlyPv
#            print 'EVR Pv %s' % self.sEvrPv
#            print 'PPM Pv %s' % self.sPpmPv
#            print 'YTR Pv %s' % self.sYtrPv
#            print 'XTR Pv %s' % self.sXtrPv
#            print 'IOC %s'    % self.sIOC
#            print 'SPP %s'    % self.sSPP
#            print 'SEV %s'    % self.sSEV
#            print 'SRV %s'    % self.sSRV
#            print 'EVB %s'    % self.sEVB
#            print 'EVS %s'    % self.sEVS
#            print 40 * '-'
#        except:
#            print 'Not all info treated'
        self.readconfig_done = True
        return True
    
 
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

if __name__ == '__main__':
    cwd = os.getcwd()
    
    cfg = PPConfig('sxr', 2)
    cfg.PPread()
    print cfg.PPEVRinit()
    print cfg.PPEVRdelay('RUN_MODE1')
    print cfg.PPEVRdelay('RUN_MODE2')
    print cfg.PPEVRdelay('RUN_MODE3')
    sys.exit(1)
    
