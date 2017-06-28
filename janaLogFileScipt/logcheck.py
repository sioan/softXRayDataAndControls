#!/reg/g/pcds/package/python-2.5.2/bin/python
#

import subprocess
import datetime
import glob
import getopt
from optparse import OptionParser
import re
import os
import sys
from pprint import pprint

COMMON_PATH = '/reg/common/package/'

DEVICE = ['NoDevice', 'Evr', 'Acqiris', 'Opal1000', 'TM6740', 'pnCCD', 'Princeton', 'Fccd', 'Ipimb', 'Encoder', 'Cspad', 'AcqTDC', 'Xamps', 'Cspad2x2', 'Fexamp', 'Gsc16ai', 'Phasics', 'Timepix', 'Opal2000', 'Opal4000', 'OceanOptics', 'Opal1600', 'Opal8000', 'Fli', 'Quartz4A150', 'Andor', 'USDUSB', 'OrcaFl40', 'Imp', 'Epix', 'Rayonix', 'EpixSampler', 'Pimax', 'Fccd960', 'Epix10k', 'Epix100a', 'EpixS', 'Gotthard', 'DualAndor', 'Wave8', 'LeCroy', 'ControlsCamera', 'Archon', 'Jungfrau', 'Zyla']
DETECTOR = ['NoDetector', 'AmoIms', 'AmoGasdet', 'AmoETof', 'AmoITof', 'AmoMbes', 'AmoVmi', 'AmoBps', 'Camp', 'EpicsArch', 'BldEb', 'SxrBeamline', 'SxrEndstation', 'XppSb1Ipm', 'XppSb1Pim', 'XppMonPim', 'XppSb2Ipm', 'XppSb3Ipm', 'XppSb3Pim', 'XppSb4Pim', 'XppGon', 'XppLas', 'XppEndstation', 'AmoEndstation', 'CxiEndstation', 'XcsEndstation', 'MecEndstation', 'CxiDg1', 'CxiDg2', 'CxiDg3', 'CxiDg4', 'CxiKb1', 'CxiDs1', 'CxiDs2', 'CxiDsu', 'CxiSc1', 'CxiDsd', 'XcsBeamline', 'CxiSc2', 'MecXuvSpectrometer', 'MecXrtsForw', 'MecXrtsBack', 'MecFdi', 'MecTimeTool', 'MecTargetChamber', 'FeeHxSpectrometer', 'XrayTransportDiagnostic', 'Lamp','MfxEndstation', 'MfxDg1', 'MfxDg2', 'XrtDiag', 'DetLab']
BLD=['EBeam', 'PhaseCavity', 'FEEGasDetEnergy', 'Nh2Sb1Ipm01', 'HxxUm6Imb01', 'HxxUm6Imb02', 'HfxDg2Imb01', 'HfxDg2Imb02', 'XcsDg3Imb03', 'XcsDg3Imb04', 'HfxDg3Imb01', 'HfxDg3Imb02', 'HxxDg1Cam', 'HfxDg2Cam', 'HfxDg3Cam', 'XcsDg3Cam', 'HfxMonCam', 'HfxMonImb01', 'HfxMonImb02', 'HfxMonImb03', 'MecLasEm01', 'MecTctrPip01', 'MecTcTrDio01', 'MecXt2Ipm02', 'MecXt2Ipm03', 'MecHxmIpm01', 'GMD', 'CxiDg1Imb01', 'CxiDg2Imb01', 'CxiDg2Imb02', 'CxiDg4Imb01', 'CxiDg1Pim', 'CxiDg2Pim', 'CxiDg4Pim', 'XppMonPim0', 'XppMonPim1', 'XppSb2Ipm', 'XppSb3Ipm', 'XppSb3Pim', 'XppSb4Pim', 'XppEndstation0', 'XppEndstation1', 'MecXt2Pim02', 'MecXt2Pim03', 'CxiDg3Spec', 'Nh2Sb1Ipm02', 'FeeSpec0', 'SxrSpec0', 'XppSpec0', 'XcsUsrIpm01', 'XcsUsrIpm02', 'XcsUsrIpm03', 'XcsUsrIpm04', 'XcsSb1Ipm01', 'XcsSb1Ipm02', 'XcsSb2Ipm01', 'XcsSb2Ipm02', 'XcsGonIpm01', 'XcsLamIpm01', 'XppAin01', 'XcsAin01', 'AmoAin01', 'MfxBeamMon01', 'EOrbits', 'MfxDg1Pim', 'MfxDg2Pim', 'SxrAin01', 'Hx2BeamMon01']


SUMMARY = {'NoSumm':0,'Brief':1,'Expanded':2, 'Fields':3, 'Full':4, 'csv':5}

runfmt = {'run':'%5.5s',
          'cgui':'%20.20s',
          'begin_full':'%20.20s',
          'begin':'%12.12s' ,
          'end_full':'%20.20s',
          'end':'%12.12s',
          'dur':'%10.10s',
          'evts':'%12.12s',
          'dmg':'%12.12s',
          'dmgpct':'(%6s)',
          'bytes':'%11.11s',
          'evtsz':'%10.10s',
          'evtrt':'%4.4s',
          'datrt':'%15.15s',
          'sources':'%30.30s',
          'maxdmg':'(%10.10s)',
          'srcdmg':'%30.30s',
          'daq':'%20.20s',
          'compress':'%20.20s',
          'ami':'%20.20s',
          'ins':'%8.8s',
          'expname':'%9.9s',
          'expnum':'%6.6s',
          'daqrest':'%3.3s',
          'amirest':'%3.3s'}

headerttl = {'run':'Run',
             'cgui':'DAQ start time',
             'begin_full':'Begin',
             'begin':'Begin',
             'end_full':'End',
             'end':'End',
             'dur':'Duration',
             'evts':'Events',
             'dmg':'Damaged',
             'dmgpct':'%',
             'bytes':'Bytes',
             'evtsz':'Evnt size',
             'evtrt':'[Hz]',
             'datrt':'Data rate',
             'sources':'%30.30s',
             'maxdmg':'# events',
             'srcdmg':'Largest contributor',
             'daq':'DAQ release',
             'compress':'Compression status',
             'ami':'AMI release',
             'ins':'Inst',
             'expname':'Exp',
             'expnum':'#',
             'daqrest':'DR',
             'amirest':'AR'}


class PHYSID(object):
    MASK_DEVID  = 0xff
    MASK_DEV    = 0xff00
    MASK_DETID  = 0xff0000
    MASK_DET    = 0xff000000
    SHIFT_DEVID = 0
    SHIFT_DEV   = 8
    SHIFT_DETID = 16
    SHIFT_DET   = 24
    
    def __init__(self, physid=0x0):
        self._physid = physid
        self._detid = (physid & self.MASK_DETID) >> self.SHIFT_DETID
        self._det   = (physid & self.MASK_DET)   >> self.SHIFT_DET
        self._devid = (physid & self.MASK_DEVID) >> self.SHIFT_DEVID
        self._dev   = (physid & self.MASK_DEV)   >> self.SHIFT_DEV

    def detid(self):
        return self._detid
    def det(self):
        return self._det
    def detname(self):
        if (self._det >= len(DETECTOR)):
#            print "\nDETECTOR %d"%self._det
            return 'DET%d'%self._det
        return DETECTOR[self._det]
    def devid(self):
        return self._devid
    def dev(self):
        return self._dev
    def devname(self):
        if (self._det == 0) and (self._dev ==0): return BLD[self._devid]
        if (self._dev >= len(DEVICE)):
#            print "DEVICE %d%self._dev
            return 'DEV%d'%self._dev
        return DEVICE[self._dev]
    def phy(self):
        return int(self._physid)
    def physname(self):
        srcstr =''
        if self.det() == 0 and self.dev() == 0:
            srcstr = "%x"%(self._physid)
        elif self.dev() == 0:
            srcstr = "%s-%d"%(self.detname(), self.detid())
        elif self.det() == 0:
            srcstr = "%s-%d"%(self.devname(), self.devid())
        else:
            srcstr = "%s-%d|%s-%d"%(self.detname(), self.detid(), self.devname(), self.devid())
        return srcstr

def usage():
    print """    
NAME
    daqcheck - Check DAQ logs for given hutch.
               Prints summary of runs for a given experiment by parsing DAQ logfiles.

USAGE
    daqcheck [OPTIONS]

EXAMPLE
    daqcheck -e amo
    daqcheck -e sxr -d 5
    daqcheck -e xpp --beg '2014-03-20' --end '2014-03-22'
    daqcheck -e xcs -s
    daqcheck -e xcs -l run,evts,dmg,dmgpct

OPTIONS
    -h, --help
        Display script usage information

    -e, --expt
        Check logs for EXPT hutch.  If not given, amo is used as default
        EXPT = amo, sxr, xpp, xcs, cxi, mfx, mec, det, or local

    -d, --day
        Check logs DAY days ago.  If no DAY or BEG field given, today's date is used by default.
        
    -b, --beg
        Check logs from given date YYYY/MM/dd to end date (now if no end date given).

    -f, --end
        Check logs from begin date to end (finish) date, YYYY/MM/dd.  Only used if --beg field is given.

    -s, --summ
        Print summary of control log information (no information on contributors or fixups)

    -x, --xsumm
        Print expanded summary of control log information (no info on contributors or fixups)

    -c, --csv
        Print csv summary of all fields listed below

    -r, --err
        Report error conditions from the logfiles: Out of Order errors, transition timeouts, ERESTART.
        
    -l, --list
        Print summary of control log information including the given fields.
        Fields are given as a comma-separated list, no spaces. The list of possible fields is
            run         - Run number
            cgui        - Control GUI start time (DAQ start time), format YYYY-mm-dd HH:MM:SS
            begin_full  - Begin run date and time, format YYYY-mm-dd HH:MM:SS
            begin       - Begin run date and time, format dd_HH:MM:SS
            end         - End run date and time, format dd_HH:MM:SS
            dur         - Duration of run (HH:MM:SS)
            evts        - Total number of events taken
            dmg         - Total number of damaged events
            dmgpct      - Percentage of events damaged
            maxdmg      - Number of damaged events contributed by the largest contributor
            srcdmg      - Contributor with the greatest number of damaged events
            bytes       - Total number of bytes recorded
            evtsz       - Average event size per event
            evtrt       - Average event rate [Hz]
            datrt       - Average data rate
            daq         - DAQ release used to acquire data
            ami         - AMI release used to view data
            ins         - Instrument name (e.g., CXI:0 or CXI:1)
            expname     - Experiment name
            expnum      - Experiment number
            daqrest     - Number of DAQ restarts since last run       
"""

def control_log(path,summ,fields):
    daq_restart = 0
    ami_restart = 0
    nerrs = 0
    for fname in glob.iglob(path+'*control_gui.log'):
        daq_restart += 1
        cguitime = datetime.datetime.strptime(fname[(len(path)-10):len(path)+9],"%Y/%m/%d_%H:%M:%S")
        thetime = fname[(len(path)+1):len(path)+9]
        ami_release = ami_version(path, thetime)
        compression = compression_check(path,thetime)
        fruns = []
        f = file(fname,"r")
        lines = f.readlines();
        run = {'dur':''}
        runnumber = '-'
        for iline in range(len(lines)):
            line = lines[iline]
            if ((line.find("MainWindow:")>=0) and (line.find('instrument')>=0) and (line.find('experiment')>=0)):
                expstr = line.split("MainWindow: ")[1].strip().split('instrument')[1].split('experiment')
                instname = expstr[0].replace("'","")
                expstr = expstr[1].strip("'").replace("'","")
                expname = expstr.split('(#')[0].replace("'","")
                expnum = expstr.split(')')[0]
                expnum = int(expnum.split('(#')[1].strip(')'))
            if (line.find("Configured")>=0 or line.find("Unmapped")>=0):
                if run['dur']!='':
                    fruns.append(run)
                    if daq_restart >= 1: daq_restart = 0
                    run = {'dur':''}
                    runnumber = '-'
            if (line.find("Completed allocating")>=0):
                runnumber = line.split()[-1]
            if ((line.find("build") >= 0) and (line.find("as") >= 0) and (line.find("@@@") >=0)):
                full_release=line.split("as ")[1].strip().strip(')')
                if full_release.find("/reg/g/pcds/dist/pds/") != -1:
                    daq_release = full_release.split("/reg/g/pcds/dist/pds/")[1].split('/')[0]
                else:
                    if full_release.find("home1") != -1:
                        daq_release = full_release.replace("/reg/neh/home1/","~")
                    elif full_release.find("home2") != -1:
                        daq_release = full_release.replace("/reg/neh/home2/","~")
                    elif full_release.find("home3") != -1:
                        daq_release = full_release.replace("/reg/neh/home3/","~")
                    elif full_release.find("home4") != -1:
                        daq_release = full_release.replace("/reg/neh/home4/","~")
                    else:
                        daq_release = full_release.replace("/reg/neh/home/","~")
            index = line.find("Duration")
            if (index>=0):
                ended    = line.partition(':Duration:')[0].rstrip()                
                duration = line.partition(' ')[-1].rstrip()
                begintime,endtime= getbeginrun(path, ended, duration)
                begin = begintime.strftime("%Y-%m-%d %H:%M:%S")
                ended_full = endtime.strftime("%Y-%m-%d %H:%M:%S")
                events   = lines[iline+1].rpartition(':')[-1].rstrip()
                damaged  = lines[iline+2].rpartition(':')[-1].rstrip()
                bytes    = lines[iline+3].rpartition(':')[-1].rstrip().lstrip()
                sec = duration.split(':')
                nsec = int(sec[0])*60*60 + int(sec[1])*60 + int(sec[2])
                if int(events)==0:
                    evtsiz = ''
                    evtrate  = ''
                    datarate = 0
                    dmgpct = 0.0
                else:
                    dmgpct = "%3.2f" % (100.0*int(damaged)/int(events)) 
                    evtsiz = humansize(float(int(lines[iline+3].rpartition(':')[-1].rstrip())/int(events)),True)
                    if (nsec != 0):
                        evtrate  = "%3.0f"%(float(float(events)/nsec))
                        datarate = float(float(bytes)/nsec)                     
                    else:
                        evtrate = 0.0
                        datarate = 0.0
                bytes = humansize(float(bytes), True)
                datarate = humansize(datarate, True)+"/s"
                srcs = []
                maxdmg = 0
                srcdmg = ' '
                iline = iline+4
                line = lines[iline]
                while( (len(line)>17 and line[8]=='.' and line[17]==':') or
                       (len(line)>29 and line[2]=='_' and line[20]=='.' and line[29]==':') or
                       (len(line)>29 and line[20]=='.' and line[29]==':') or
                       (len(line)>41 and line[2]=='_' and line[32]=='.' and line[41]==':') or
                       (len(line)>45 and line[41]==':')):
                    if line.count(':') < 2:
                        s = line.rsplit(':')
                        source = s[-2].rstrip()
                        n = s[-1].rstrip()
                        if n.find('/') != -1: n = n.split('/')[0]
                        physidnum = int(source.split('.')[1],16)
#                        print "0x%x"%(physidnum)
#                        print line
                        physid = PHYSID(physidnum)
                        srcstr=source
                        if physid.det() == 0 and physid.dev() == 0:
                            srcstr = source.split('.')[0].strip()
                        elif physid.dev() == 0:
                            srcstr = "%s-%d"%(physid.detname(), physid.detid())
                        elif physid.det() == 0:
                            srcstr = "%s-%d"%(physid.devname(), physid.devid())
                        else:
                            srcstr = "%s-%d|%s-%d"%(physid.detname(), physid.detid(), physid.devname(), physid.devid())
                        srcs.append({'source':source,
                                     'srcstr':srcstr,
                                     'physid':physidnum,
                                     'devid':physid.dev(),
                                     'devname':physid.devname(),
                                     'detid':physid.det(),
                                     'detname':physid.detname(),
                                     'n':n})

                        if (source.find('EBeam Low Curr') == -1):
                            if int(n) > maxdmg:
                                maxdmg = int(n)
#                                print line
#                                print int(source.split('.')[1],16)
                                physid = PHYSID(int(source.split('.')[1],16))
                                srcdmg = physid.physname()
                                if physid.det() == 0 and physid.dev() == 0:
                                    srcdmg = source.split('.')[0].strip()
                        if maxdmg == 0:  srcdmg = ' '
                        
                    iline = iline+1
                    if (iline>=len(lines)):
                        break
                    line = lines[iline]
                run = {'run':runnumber,
                       'cgui':cguitime,
                       'begin_full':begin,
                       'begin':begin[8:].replace(' ','_'),
                       'end_full':ended_full,
                       'end':ended,
                       'dur':duration,
                       'evts':events,
                       'dmg':damaged,
                       'dmgpct':dmgpct,
                       'bytes':bytes,
                       'evtsz':evtsiz,
                       'evtrt':evtrate,
                       'datrt':datarate,
                       'sources':srcs,
                       'maxdmg':maxdmg,
                       'srcdmg':srcdmg,
                       'daq':daq_release,
                       'compress':compression,
                       'ami':ami_release,
                       'ins':instname,
                       'expname':expname,
                       'expnum':expnum,
                       'daqrest':daq_restart,
                       'amirest':ami_restart,
                       'nerr': 0}
                
        if run['dur']!='':
            fruns.append(run)            

        sources = []
        for r in fruns:
            for s in r['sources']:
                if not s['source'] in sources:
                    sources.append(s['source'])

#        for r in fruns:
#            if fruns.index(r) == 0:
#                print "Control gui time used ", r['run'], r['cgui'], r['end_full']
#                error_check(path, r['cgui'].strftime("%Y-%m-%d %H:%M:%S"), r['end_full'], nerrs)
#            else:
#                print "Begin/End run used ", r['run'],r['begin_full'], r['end_full'] 
#                error_check(path, r['begin_full'], r['end_full'])
#        nerrs = 0
        
        if len(sources)==0:
            continue

        if summ==SUMMARY['Brief']:
            print_summary_header(fname, fruns)
            fields = ['run','begin','end','dur','evtrt','bytes','evts','dmg','dmgpct','srcdmg','maxdmg','daq','ami','expname','expnum']
            print_summary_fields(fruns,fields)
        elif summ==SUMMARY['Expanded']:
            print_summary_header(fname, fruns)
            fields = ['run', 'dur', 'end', 'bytes', 'datrt', 'evtrt', 'evts', 'dmg', 'dmgpct', 'srcdmg', 'maxdmg', 'daq', 'ami', 'ins', 'expname', 'expnum']
            print_summary_fields(fruns,fields)
        elif summ==SUMMARY['Fields']:
            print_summary_header(fname, fruns)            
            print_summary_fields(fruns, fields)
        elif summ==SUMMARY['csv']:
            print_summary_csv(fruns)
        else:
            print_full(fname, fruns, sources)


def print_full(fname,fruns,sources):
    print '\n-----'+fname,
    if len(fruns) != 0:
        print '\n-----%s %s (%s)'%(fruns[0]['ins'],fruns[0]['expname'],fruns[0]['expnum'])
        print '----- DAQ release: %s'%(fruns[0]['daq'])
        print '----- AMI release: %s'%(fruns[0]['ami'])
        print '----- Contributors:'
        if len(fruns[0]['compress']) != 0:
            print '----- Compression status (%s): ' % (fruns[0]['compress'][0]['ts'])
            for det in fruns[0]['compress']:
                print "      %-25s %-25s (on %s):\tCompression %s." % (det['dev'], det['task'],det['node'], det['msg'])

    fmtttl = '\n%29.29s'
    fmtstr = '%29.29s'
    step = 5
        
    for irun in range(0,len(fruns),step):
        print " "
        runs = fruns[irun:irun+step]
        
        print fmtttl%'Run',
        for r in runs:
            print fmtstr%r['run'],
        
        print fmtttl%'Duration',
        for r in runs:
            print fmtstr%r['dur'],
        
        print fmtttl%'Events',
        for r in runs:
            print fmtstr%r['evts'],

        print fmtttl%'Damaged',
        for r in runs:
            print fmtstr%r['dmg'],
        
        print fmtttl%'Bytes',
        for r in runs:
            print fmtstr%r['bytes'],

        print fmtttl%'EvtSz',
        for r in runs:
            print fmtstr%r['evtsz'],

        print
        for src in sources:
            physid = PHYSID(int(src.split('.')[1],16))
            if physid.det() == 0 and physid.dev() == 0:
                srcstr = src.split('.')[0].strip()
            elif physid.dev() == 0:
                srcstr = "%s-%d"%(physid.detname(), physid.detid())
            elif physid.det() == 0:
                srcstr = "%s-%d"%(physid.devname(), physid.devid())
            else:
                srcstr = "%s-%d|%s-%d"%(physid.detname(), physid.detid(), physid.devname(), physid.devid())
            print fmtttl%srcstr,
            for r in runs:
                lfound=False
                for s in r['sources']:
                    if s['source']==src:
                        lfound=True                        
                        print fmtstr%s['n'],
                if not lfound:
                    print fmtstr%'-',
        print " "

def print_summary_header(fname, fruns):
    print '\n-----'+fname,
    if len(fruns) != 0:
        print '\n-----%s %s (%s)'%(fruns[0]['ins'],fruns[0]['expname'],fruns[0]['expnum'])
        print '----- DAQ release: %s'%(fruns[0]['daq'])
        print '----- AMI release: %s'%(fruns[0]['ami'])

        # Get unique list of cameras
        sources = []
        cameras = []
        for src in fruns[0]['sources']:
            sources.append(src['srcstr'])
        for cam in fruns[0]['compress']:
            cameras.append(cam['dev'])

        srclist = set(sources) | set(cameras)
        msg = ''
        for src in srclist:
            if src in cameras:
                cam = fruns[0]['compress'][cameras.index(src)]
                if cam['msg'] == "enabled": msg = 'C'
                else: msg = 'NC'
            else:
                msg = '--'
            print "      (%2s) %-30s" % (msg, src)
        print ''

def print_summary_fields(fruns, fields, sep=' '):
    header = ''
    for field in fields:
        header += runfmt[field]%headerttl[field]+sep
    print header
    
    
    for irun in range(0, len(fruns)):
        r = fruns[irun]
        outstr = ''
        for field in fields:
            outstr += runfmt[field]%r[field]+sep
        print outstr

def print_summary(fruns,fields,summ):
    if summ==SUMMARY['Brief']:
        print_summary_header(fname, fruns)
        fields = ['run','begin','end','dur','evts','dmg','bytes','evtrt','srcdmg','maxdmg','daq','ami','ins','expname','expnum']
        print_summary_fields(fruns,fields)
    elif summ==SUMMARY['Expanded']:
        print_summary_header(fname, fruns)
        fields = ['run', 'dur', 'end', 'bytes', 'datrt', 'evtrt', 'evts', 'dmg', 'dmgpct', 'srcdmg', 'maxdmg', 'daq', 'ami', 'ins', 'expname', 'expnum']
        print_summary_fields(fruns,fields)
    elif summ==SUMMARY['Fields']:
        print_summary_header(fname, fruns)            
        print_summary_fields(fruns, fields)
    elif summ==SUMMARY['csv']:
        print_summary(fruns,fields,sep=',')
    else:
        print_full(fname, fruns, sources)

           

def print_summary_csv(fruns,sep=','):
    header = ''
    fields = runfmt.keys()
    for field in fields:
        if field == 'sources' or field == 'compress':
            continue
        else:
            header += runfmt[field]%headerttl[field]+sep
    print header
    
    for irun in range(0, len(fruns)):
        r = fruns[irun]
        outstr = ''
        for field in fields:
            if field == 'sources' or field == 'compress':
                continue
            else:
                outstr += runfmt[field]%r[field]+sep
        print outstr

def getbeginrun(path, end, duration):
    global last_endrun
    begin= ''
    year, month, day = path.split('logfiles/')[1].split('_')[0].split('/')

    if end.find('_') >= 0:
        day = end.split('_')[0]
        ehours,eminutes,eseconds = end.split('_')[1].split(':')
        hours, minutes, seconds = duration.split(':')
        endtime = datetime.datetime(int(year),int(month),int(day),int(ehours), int(eminutes), int(eseconds))
        diff = datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
        begintime = endtime - diff
    else:
        begintime = datetime.date(int(year), int(month), int(day))
        endtime = last_endrun
    return begintime, endtime

def print_run_configuration(fname, fruns, sources):
    print "Printing run configuration"
    print '\n-----'+fname
    print '\n-----%s %s (%s)'%(fruns[0]['ins'],fruns[0]['expname'],fruns[0]['expnum'])
    print '----- DAQ release: %s'%(fruns[0]['daq'])
    print '----- AMI release: %s'%(fruns[0]['ami'])
    if len(fruns) != 0:
        if len(fruns[0]['compress']) != 0:
            print '----- Compression status (%s): ' % (fruns[0]['compress'][0]['ts'])
            for det in fruns[0]['compress']:
                print "      %-30s %-15s (on %s):\tCompression %s." % (det['dev'],det['task'],det['node'], det['msg'])
    
    # DAQ and AMI releases
    # Instrument, experiment name
    # last DAQ restart
    # Compression status
    # Mapping of alias to detector name to task to node, etc.
    # AMI restarts
    # EVR settings, groups, what's reading out on what event code and so on

def get_evr_configuration(fname,fruns, sources):
    for fname in glob.iglob(path+'*control_gui.log'):
        thetime = fname[(len(path)+1):len(path)+9]
        
def fixup_check(path):
    flist = glob.glob(path+'*.log')
    if len(flist)==0:
        return
    args = ["grep","fixup"]+flist
    pfn = subprocess.Popen(args=args,stdout=subprocess.PIPE)
    odate = pfn.communicate()[0].split('\n')
    laststr = None
    lastcnt = 1
    fmtstr='%29.29s'
    lttl = False
    for l in odate:
        if (l[:6]=='/reg/g'):
            thedate = l[29:39]
            thetime = l[40:48]
            thehost = l[49:].partition(':')[0]
            thename = l[49:].split(':')[1].split('.')[0]
            thisstr = fmtstr%thetime+fmtstr%thehost+fmtstr%thename
            if (thisstr==laststr):
                lastcnt = lastcnt+1
            else:
                if (laststr!=None):
                    if not lttl:
                        lttl=True
                        print '\n'+fmtstr%'Time'+fmtstr%'Node'+fmtstr%'Name'+fmtstr%'Fixups'
                    print laststr+fmtstr%lastcnt
                laststr=thisstr
                lastcnt=1
    if (laststr!=None):
        if not lttl:
            lttl=True
            print '\n'+fmtstr%'Time'+fmtstr%'Node'+fmtstr%'File'+fmtstr%'Fixups'
        print laststr+fmtstr%lastcnt

def error_check(path, begstr, endstr, nerrs=0):
    nerror = 0
    error_mask = 0x0
    beg = datetime.datetime.strptime(begstr,"%Y-%m-%d %H:%M:%S")
    end = datetime.datetime.strptime(endstr,"%Y-%m-%d %H:%M:%S")
    
    nerrors = signal_count(path, beg, end)
    print begstr, endstr, nerrors
    
def signal_count(path, beg, end):
    # Ignores vmon
    sigabort = 6
    sigsegv = 11
    signals = {sigabort:0, sigsegv:0}

    flist = glob.glob(path+'*.log')
    if len(flist)==0:
        return signals
    
    for signum in signals:
        args = ["grep","signal"]+flist
        pfn = subprocess.Popen(args=args,stdout=subprocess.PIPE)
        odate = pfn.communicate()[0].split('\n')
        for l in odate:
            if ((l.find('sigChild') >= 0) and l[:6]=='/reg/g' and l.find('signal %d'%signum)>=0):
                thedate = l[29:39]
                thetime = l[40:48]
                thisdate = datetime.datetime.strptime(thedate+' '+thetime,"%Y/%m/%d %H:%M:%S")
                if (thisdate >= beg) and (thisdate <= end):
                    signals[signum] = signals[signum] + 1

    return signals

    
    
def signal_check(path, signum, signame):
    nerr = 0
    flist = glob.glob(path+'*.log')
    if len(flist)==0:
        return
    args = ["grep","signal"]+flist
    pfn = subprocess.Popen(args=args,stdout=subprocess.PIPE)
    odate = pfn.communicate()[0].split('\n')
    laststr = None
    lastcnt = 1
    fmtstr='%29.29s'
    lttl = False
    for l in odate:
        if (l[:6]=='/reg/g' and l.find('signal %d'%signum)>=0):
            thedate = l[29:39]
            thetime = l[40:48]
            thehost = l[49:].partition(':')[0]
            thename = l[49:].split(':')[1].split('.')[0]
            thisstr = fmtstr%thetime+fmtstr%thehost+fmtstr%thename
            if (thisstr==laststr):
                lastcnt = lastcnt+1
            else:
                if (laststr!=None):
                    if not lttl:
                        lttl=True
                        print '\n'+fmtstr%'Time'+fmtstr%'Node'+fmtstr%'Name'+fmtstr%signame
                    print laststr+fmtstr%lastcnt
                laststr=thisstr
                lastcnt=1
    if (laststr!=None):
        if not lttl:
            lttl=True
            print '\n'+fmtstr%'Time'+fmtstr%'Node'+fmtstr%'Name'+fmtstr%signame
        print laststr+fmtstr%lastcnt


def hutch_loop(expt, date_path, summ, fields, errs):
    hutches = ['amo','sxr','xpp','xcs','cxi','mec','cxi_0','cxi_1','cxi_shared', 'mfx', 'det']
    for hutch in hutches:
        if expt=='all' or expt==hutch.lower():
            base_path = '/reg/g/pcds/pds/'+hutch+'/logfiles/'
            path = base_path+date_path
            if len(glob.glob(path+'*control_gui.log')) == 0:
                latest = [glob.glob(base_path+'*/*/*control_gui.log')[-1]]
                if len(latest) != 0:
                    args = ["egrep","@@@ Received a sigChild"]+latest
                    p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
                    out = p.communicate()[0]
                    if (len(out) == 0):
                        # The DAQ is still running and this is the latest control_gui file
                        date_fields = latest[0].split('logfiles/')[1].split('_')[0].split('/')
                        year, month, day = (date_fields[-3],date_fields[-2],date_fields[-1])
                        date_path = datetime.date(int(year), int(month), int(day)).strftime("%Y/%m/%d")
                        path =base_path+date_path
                    else:
                        return
            print '=== %s ==='%hutch.upper()
            control_log(path,summ,fields)
            if errs:
                fixup_check(path)
                signal_check(path,6,'SIGABORT')
                signal_check(path,11,'SIGSEGV')
                transition_check(path)
                outoforder_check(path)
                stat_check(path)
                pgpproblem_check(path)
    if expt=='local':
        path = os.getenv('HOME')+'/'+date_path
        if len(glob.glob(path+'*control_gui.log')) == 0: return
        print '=== LOCAL ==='
        print path
        control_log(path,summ,fields)
        if errs:
            fixup_check(path)
            signal_check(path,6,'SIGABORT')
            signal_check(path,11,'SIGSEGV')
            transition_check(path)
            outoforder_check(path)
            stat_check(path)
            pgpproblem_check(path)
            
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + datetime.timedelta(n)


SUFFIXES = {1024: ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            1000: ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']}

def humansize(size, a_kilobyte_is_1024_bytes=True):
    '''Convert a file size to human-readable form.

    Arguments:
       size -- size in bytes
       a_kilobyte_is_1024_bytes -- if True (default), use multiples of 1024
                                if False, use multiples of 1000

    Returns: string repressenting file size

    '''
    if size < 0:
        raise ValueError('number must be non-negative')

    multiple = 1024 if a_kilobyte_is_1024_bytes else 1000
    for suffix in SUFFIXES[multiple]:
        size /= multiple
        if size < multiple:
            return '%8.1f %s'%(size, suffix)

    raise ValueError('number too large')

def pid2task(path,pid):
    flist=glob.glob(path+'*.log')
    tasks = []
    task = {'pid':0}
    args = ["grep","PID"]+flist
    p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
    output = p.communicate()[0].split('\n')
    for line in output:
        if line.find('@@@ The PID of new child')>=0:
            line = line.split("@@@ The PID of new child")[1]
            thedate = line.split('logfiles/')[1].split('_')[0]
            thetime = line.split('_')[1]
            thenode = line.split('_')[2].split(':')[0]
            thename = line.split('_')[2].split(':')[1].split('.')[0]
            thepid = line.split('is: ')[1].strip()
            task={'date':thedate, 'time':thetime, 'node':thenode,'name':thename,'pid':thepid}
            tasks.append(task)              
            if pid == thepid:
                return task
    return 0



def transition_check(path):
    print_header = True
    fmtstr="%29.29s"
    longfmtstr="%29.29s"
    for fname in glob.iglob(path+'*control_gui.log'):
        logtime=fname.split(path)[1].split('_')[1]
        fruns = []
        f = file(fname,"r")
        lines = f.readlines();
        
        for iline in range(len(lines)):
            line = lines[iline]
            if (line.find("Completed allocating")>=0):
                runnumber = line.split()[-1]
            index = line.find("Timeout waiting for transition")
            if (index>=0):
                try:
                    trans_time = line.partition(': Timeout')[0].rstrip().split('_')[1][:-9]
                    transition = line.split(' to complete.')[0].strip().split('transition ')[1]
                    nodes = lines[iline+1].rpartition(':')[-1].rstrip()
                    segment, pid = lines[iline+2].split(':')[1:]
                    segment = segment.strip()
                    pid = pid.strip()
                    task = pid2task(path+'_'+logtime, pid)
                
                    if print_header:
                        print '\n'+fmtstr%'Time'+longfmtstr%'Transition Timeout'+longfmtstr%'Task'+fmtstr%'PID'+longfmtstr%'Node'
                        print_header = False

                    print fmtstr%trans_time+longfmtstr%transition+longfmtstr%task['name']+fmtstr%task['pid']+longfmtstr%task['node']
                except:
                    pass

def stat_check(path):
    print_header = True
    flist = glob.glob(path+"*event*.log")
    args = ["grep", "Cannot"]+flist
    p = subprocess.Popen(args=args, stdout=subprocess.PIPE)
    output = p.communicate()[0].split('\n')
    for line in output:
        if (len(line) != 0) and (line.find("stat") != -1) and (line.find("file") != -1):
            if print_header:
                print "\nStat errors:"
                print_header = False
            print line
    print ""
    

def outoforder_check(path):
    noo = 0
    print_header = True
    flist = glob.glob(path+"*.log")
    args = ["grep","--binary-files=text", "order"]+flist
    p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
    output = p.communicate()[0].split('\n')
    for line in output:
        if (len(line) != 0) and (line.find("response") == -1) and (line.find("vmonrecorder") == -1):
            if print_header:
                print "\nOut of Order errors:"
                print_header = False
            print line
            noo+=1
    print ""
    return noo

def node2name(flist,node):
    name = "Unknown node: %s" % node
    try:
        hutch = flist[0].split("reg/g/pcds/pds/")[1].split("/logfiles")[0]
    except:
        print("Unexpected error in node2name:", sys.exc_info()[0])
        return name
    
    if (hutch.find('cxi') != -1):
        exp = "cxi"
    else:
        exp = hutch
    flist=glob.glob('/reg/g/pcds/dist/pds/'+exp+'/scripts/'+hutch+'.cnf')
    if (len(flist) != 0):
        args = ["grep",node]+flist
        p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
        output = p.communicate()[0]
        if len(output) != 0: output = output.split('\n')
        for line in output:
            if ((len(line) != 0) and (line.find(node) != -1)):
                name = line.split('=')[0].strip()
    return name


def ami_version(path, thetime):
    rv = ''
    flist = glob.glob(path+"_"+thetime+"*ami*.log")
    if len(flist) != 0:
        cmd = ["""grep '@@@    (as ' | grep     """]
        args = ["grep", "@@@    (as "]+flist
        p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
        output = p.communicate()[0].split('\n')
        for line in output:
            if (len(line) != 0) and (line.find("online_ami") != -1):
                release = line.split("as ")[1].strip().strip(')')
                if release.find("/reg/g/pcds/dist/pds/") != -1:
                    rv = release.split("/reg/g/pcds/dist/pds/")[1].split('/')[0]
                else:
                    rv = release
    return rv

def compression_check(path,thetime):
    retval = []
    ccdretval = []
    srcid = ''
    detid = ''
    devid = ''
    devname = ''
    device = ''

    flist = glob.glob(path+"_"+thetime+"*.log")

    if len(flist) != 0:
        args = ["egrep", "Compression|Parsing "]+flist 
        p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
        output  = p.communicate()[0].split('\n')
        for line in output:
            if (len(line) != 0) and (line.find("Parsing ") != -1):
                device = line.split('Parsing ')[1].strip().replace('/','-',1).replace('/','|',1).replace('/','-').replace('EndStation','Endstation')
            if (len(line) != 0) and (line.find("Compression") != -1):
                timestamp = line.split('/logfiles/')[1].replace('_',' ',1).split('_')[0]
                if (line.find('cxi_') != -1):
                    node = line.split('_')[3].split(':')[0]
                else:
                    node = line.split('_')[2].split(':')[0]
                task = line.split(':')[3].split('.')[0]
                msg = line.split('.log:')[1].split('Compression is')[1].strip().strip('.')
                retval.append({'node':node2name(flist,node),'task':task,'ts':timestamp,'msg':msg, 'dev':device})
                
        args = ["egrep","-l","entering cspad task main loop"]+flist
        p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
        output,err = p.communicate()
        ccdlist = output.split('\n')
        for file in ccdlist:
            if file.find('.log') != -1:
                args = ["egrep", "Detector:|Device:|pgpcard device name|@@@ The PID of new child"]+[file]
                p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
                output, err = p.communicate()
                if len(output) != 0:
                    output = output.split('\n')
                    for line in output:
                        if (line.find("Detector: ") != -1):
                            detid = line.split("Detector: ")[1].strip()
                        if (line.find("Device: ") != -1):
                            devname = line.split("Device: ")[1].strip()[:5]
                        if (line.find("/dev/pgpcard_") != -1):
                            devid = line.split("/dev/pgpcard_")[1].split('_')[0].strip()
                        if line.find("@@@ The PID of new child") != -1:
                            fname = line.split('\"')[1]
                            node = fname.split('_')[2].split(':')[0]
                            task = fname.split(':')[3].split('.')[0]
                    device = "%s|%s-%s"%(detid, devname, devid)
                    ccdretval.append({'node':node2name([file],node),'task':task,'dev':device})
        for camera in retval:
            for ccd in ccdretval:
                if (camera['node'] == ccd['node']) and (camera['task'] == ccd['task']):
                    camera['dev'] = ccd['dev']
    return retval


def pgpproblem_check(path):
    print_header=True
    flist = glob.glob(path+"*cspad*.log")
    flist += glob.glob(path+"*Pnccd*.log")
    if len(flist) != 0:
        args = ["grep", "--binary-file=text","ERESTART"]+flist
        p    = subprocess.Popen(args=args,stdout=subprocess.PIPE)
        output = p.communicate()[0].split('\n')
        for line in output:
            if (len(line) != 0) and (line.find("ERESTART") != -1):
                if print_header:
                    print "PGP problems:\n"
                    print_header = False
                    print line
            
def get_current_pdsdata():
    dirlist = []
    releases = []
    dirlist = glob.glob(COMMON_PATH + 'pdsdata/*')
#    dirlist.sort(key=lambda x: os.path.getmtime(x))
    for dir in dirlist:
        if re.search('(?:(\d+)\.)?(?:(\d+)\.)?(\*|\d+)', dir):
            releases.append(dir)
    latest_file = max(releases, key=os.path.getmtime)
    pdsdata = latest_file.strip(COMMON_PATH+'pdsdata/')
    return pdsdata

def read_bldinfo(pdsdata):
    bld = []
    f = open('/reg/common/package/pdsdata/'+pdsdata+'/i386-linux-opt/pdsdata/xtc/BldInfo.hh', 'r')
    lines = f.readlines()
    
    found_bld_enum = False
    
    for iline in range(len(lines)):
        line = lines[iline]
        if line.find("enum")>=0 and line.find("Type")>=0:
            found_bld_enum = True
        if found_bld_enum:
            while line.find('}') == -1:
                if line.find('=')>=0:
                    bldname = line.split('=')[0].strip()
                    if bldname.find('enum Type') >=0:
                        bldname = bldname.split('{')[1].strip()
                    bldid = line.split('=')[1]
                    if bldid.find(',')>=0: bldid = bldid.split(',')[0]
                    if bldname.find("NumberOf") == -1:
                        bld.append(bldname)
                        if (len(bld)-1) != int(bldid):
                            print "ERROR: detid %d does not match index of det array (%d)"%(int(bldid), len(bld)-1)
                iline = iline+1
                if iline>=len(lines):
                    break
                line = lines[iline]
                found_bld_enum = False
    return bld

def read_detinfo(pdsdata):
    det = []
    dev = []
    f = open('/reg/common/package/pdsdata/'+pdsdata+'/i386-linux-opt/pdsdata/xtc/DetInfo.hh', 'r')
    lines = f.readlines()
    
    found_det_enum = False
    found_dev_enum = False
    
    for iline in range(len(lines)):
        line = lines[iline]
        if line.find("enum")>=0 and line.find("Detector")>=0:
            found_det_enum = True
        if found_det_enum:
            while line.find('}') == -1:
                if line.find('=')>=0:
                    detname = line.split('=')[0].strip()
                    detid = line.split('=')[1]
                    if detid.find(',')>=0: detid = detid.split(',')[0]
                    if detname.find("NumDetector") == -1:
                        det.append(detname)
                        if (len(det)-1) != int(detid):
                            print "ERROR: detid %d does not match index of det array (%d)"%(int(detid), len(det)-1)
                iline = iline+1
                if iline>=len(lines):
                    break
                line = lines[iline]
                found_det_enum = False
  
        if line.find("enum")>=0 and line.find("Device")>=0:
            found_dev_enum = True
        if found_dev_enum:
            while line.find('}') == -1:
                if line.find('=')>=0:
                    devname = line.split('=')[0].strip()
                    devid = line.split('=')[1]
                    if devid.find(',')>=0: devid = devid.split(',')[0]
                    if devname.find("NumDevice") == -1:
                        dev.append(devname)
                        if (len(dev)-1) != int(devid):
                            print "ERROR: devid %d does not match index of dev array (%d)"%(int(devid), len(dev)-1)
                iline = iline+1
                if iline>=len(lines):
                    break
                line = lines[iline]
                found_dev_enum = False


    return (dev,det)
    
if __name__ == "__main__":    
    summary = SUMMARY['NoSumm']
    expt = 'amo'
    fields = []
    beg_date = None
    end_date = None
    day = 0
    report_errs = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],'e:d:b:f:l:rsxch',
                                   ['expt=',
                                    'day=',
                                    'beg=',
                                    'end=',
                                    'list=',
                                    'err',
                                    'summ',
                                    'xsumm',
                                    'csv',
                                    'help'])
    except getopt.GetoptError,e:
        print e
        print 'try "logcheck.py --help" for usage information'
        sys.exit()

    for o, a in opts:
        if o in ( '-h', '--help' ):
            usage()
            sys.exit()
        if o in ( '-e', '--expt' ):
            expt = a.lower()
        if o in ( '-d', '--day' ):
            day = int(a)
        if o in ( '-b', '--beg' ):
            beg_date = a
        if o in ( '-f', '--end' ):
            end_date = a
        if o in ( '-s', '--summ' ):
            summary = SUMMARY['Brief']
        if o in ( '-x', '--xsumm' ):
            summary = SUMMARY['Expanded']
        if o in ( '-c', '--csv' ):
            summary = SUMMARY['csv']
        if o in ( '-l', '--list' ):
            summary = SUMMARY['Fields']
            varstr = ''.join(a)
            fields = varstr.split(',')
            for field in fields:
                if field not in runfmt:
                    print "Invalid field: %s\nTry --help option and remember comma-separated, no spaces."%field
                    sys.exit()
        if o in ( '-r', '--err' ):
            report_errs = True

    pdsdata = get_current_pdsdata()
    DEVICE, DETECTOR = read_detinfo(pdsdata)
    BLD = read_bldinfo(pdsdata)

    thisdate = datetime.date.today() - datetime.timedelta(int(day))
    date_path = thisdate.strftime('%Y/%m/%d')

    global last_endrun
    last_endrun = thisdate
        
    if beg_date!= None:
        year,month,day=beg_date.replace('-','/').strip().split('/')
        beg_date = datetime.date(int(year), int(month), int(day))
        last_endrun = datetime.datetime(int(year), int(month), int(day))

        if end_date != None:
            end_year, end_month, end_day = end_date.replace('-','/').strip().split('/')
            end_date = datetime.date(int(end_year),int(end_month),int(end_day))
        else:
            end_date = datetime.date.today()
    
        for single_date in daterange(beg_date,end_date):
            date_path = single_date.strftime("%Y/%m/%d")
            hutch_loop(expt, date_path, summary, fields, report_errs)
    else:
        hutch_loop(expt, date_path, summary, fields, report_errs)
        

