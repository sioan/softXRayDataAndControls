import numpy as np
import h5py
import psana

from xppmodules.littleData import *
from xppmodules.utilities import *

import argparse
import time
import socket

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

##########################################################
# functions for run dependant parameters
##########################################################

def getROIs(run, expname):
    ROIs=[]
    if run<3:
        ROIs.append([[1,2], [23,40], [290,300]])
        ROIs.append([[0,1], [90,100], [30,40]])
    elif run<11:
        ROIs.append([[17,18], [70,172], [47,122]])
        ROIs.append([[9,10],[103,155],[49,119]])
    elif run<79:
        ROIs.append([[17,18], [13,177], [21,200]])
        ROIs.append([[9,10], [58,118], [36,92]])
        ROIs.append([[9,10],[103,155],[49,119]])
    elif run<180:
        ROIs.append([[4,5], [6,44], [166,250]])
        ROIs.append([[4,5], [2,41], [137,176]])
    elif run<204:
        ROIs.append([[1,2], [112,166], [209,377]])
        ROIs.append([[16,17], [85,178], [62,150]])
    elif run<217:
        ROIs.append([[2,3], [155,184], [173,191]])
        ROIs.append([[2,3], [3,138], [117,249]])
        ROIs.append([[7,8], [17,50], [287,295]])
        ROIs.append([[12,13], [131,177], [293,315]])
    elif run<228:
        ROIs.append([[30,31], [100,117], [365,384]])
        ROIs.append([[16,17], [14,111], [308,386]])
        ROIs.append([[23,24], [143,173], [43,78]])
    elif run<240:
        ROIs.append([[3,4], [74,97], [167,184]])
        ROIs.append([[16,17], [22,92], [344,385]])
        ROIs.append([[23,24], [2,30], [55,69]])
        #ROIs.append([[16,17], [85,178], [62,150]])
    else:
        ROIs.append([[3,4], [16,68], [165,192]])
        ROIs.append([[16,17], [12,143], [310,387]])
        ROIs.append([[22,23], [86,152], [33,90]])
        ROIs.append([[13,14], [0,28], [291,347]])


 #   else:
 #       ROIs.append()
 #       ROIs.append()
    return ROIs

##########################################################
# run independent parameters 
##########################################################
#event codes which signify no xray/laser
xfel_off_codes = [ 162 ]
laser_off_codes = [ 91 ]
#aliases for experiment specific PVs go here
epicsPV = ['samR','samX','samY']
#tt calibration parameters (if passing None, init will use values used during recording
#ttCalibPars = None #[p0, p1, p2]
ttCalibPars = [ 0.8032, -0.002455, 0.0000006187]
#AIOPars= [[0],['magV']]
dets=[]

##########################################################
#command line input parameter: definitions & reading
##########################################################
maxNevt=1e9
dirname = None
parser = argparse.ArgumentParser()
parser.add_argument("--run", help="run")
parser.add_argument("--exp", help="experiment name")
parser.add_argument("--nevt", help="number of events", type=int)
parser.add_argument("--dir", help="directory for output files (def <exp>/ftc)")
parser.add_argument("--offline", help="run offline (def for current exp from ffb)")
args = parser.parse_args()
if not args.run:
    run=raw_input("Run Number:\n")
else:
    run=args.run
if not args.exp:
    expname=RegDB.experiment_info.active_experiment('XPP')[1]
    dsname='exp='+expname+':run='+run+':smd:dir=/reg/d/ffb/xpp/%s/xtc:live'%expname
else:
    expname=args.exp
    dsname='exp='+expname+':run='+run+':smd'
if args.offline:
    dsname='exp='+expname+':run='+run+':smd'
if args.nevt:
    maxNevt=args.nevt
if args.dir:
    dirname=args.dir+'/'

try:
    ds = psana.DataSource(dsname)
except:
    print 'we seem to not have small data, you need to use the idx file based Ldat_standard code....'
    sys.exit()
env=ds.env()            
expname = getExpName(env)
time_ev_sum = 0.
debug = True
        
ldr = littleDataReader()
ldr.getConfig(env, debug)        
if dirname is None:
    dirname=ldr.dirname
    dirnameTmp=ldr.dirname.replace('ftc','scratch/tmp_littleDat')
else:
    dirnameTmp=dirname
ldr.setEpicsUser(epicsPV)
ldr.setBeamOffCodes([xfel_off_codes, laser_off_codes])
ldr.set_ttCalib(ttCalibPars)

ROIs = getROIs(int(run), expname=expname)
dets=[]
have_cspad = checkDet(env, 'cspad')
if have_cspad:
    cspad = DetObject('cspad' ,env, int(run), name='cspad')
    cspad.addROI('roi0',ROIs[0], writeArea=True, rms=cspad.rms)
    cspad.addROI('roi1',ROIs[1], writeArea=True, rms=cspad.rms)
    cspad.addROI('roi2',ROIs[2], writeArea=True, rms=cspad.rms)
    if len(ROIs)>3:
        cspad.addROI('roi3',ROIs[3], writeArea=True, rms=cspad.rms)
    if len(ROIs)>4:
        cspad.addROI('roi4',ROIs[4], rms=cspad.rms)
    dets.append(cspad)

ld = littleData()

for eventNr, evt in enumerate(ds.events()):
    printMsg(eventNr, evt.run())
    time_ev_start = MPI.Wtime()

    #now only process this ranks events:
    if eventNr%size != rank:
        continue

    ##########################################################
    # extract generic data for the little hdf5 file from event
    ##########################################################
    ldr.extractValues(evt, env, ld)
                            
    ##########################################################
    # add user data - cspad
    ##########################################################
    if have_cspad:
        cspad.evt = dropObject()
        #pedestal subtracted data, common mode if desired
        try:
            ##no common mode
            #cspad.evt.dat = cspad.det.raw_data(evt)-cspad.det.pedestals(evt)        
            #with common mode (good unless our you have photons on whole ASCIs and care about relative ASIC treatment)
            cspad.evt.dat = cspad.det.calib(evt,cmpars=(1,25,40,100))
        except:
            cspad.evt.dat = None
        cspad.processROIs()

    ##########################################################
    # now add the userData to littleData
    # adds fields xxx like det.evt.write_xxx
    ##########################################################
    for det in dets:
        ldr.userDataToLittleData(det, det._name, ld)
        
    #time here.
    time_ev_stop = MPI.Wtime()
    time_ev_sum += time_ev_stop-time_ev_start

##########################################################
# loop over events done, now gather data from all sub-jobs
##########################################################

print 'sub jobs ended, now writing ',rank,' of ',size,' at ',time.ctime(),' with ',len(ld.gdet.f11),' entries'

fname = dirnameTmp+'ldat_%s_Run%i_r%03d.h5'%(expname,evt.run(),rank)
f = h5py.File(fname, "w")
ld.writeToOutputFile(f)        
f.close()

thisRunDone=1
allRunsDone=0
if (size > 1 ):
    allRunsDone = comm.reduce( thisRunDone)
    h5fileList = comm.gather(fname, root=0)
            
if rank==0:
    print 'size ',size, ' rank ',rank,' # of runs done: ',allRunsDone
    if allRunsDone == size and size >=2:
        print 'I will merge this now!'
        h5fileList.sort()
        print '1:',h5fileList
        files=[ h5py.File(locfname) for locfname in h5fileList ]

        fname = dirname+'ldat_%s_Run%03d.h5'%(expname,evt.run())
        f = h5py.File(fname, "w")
        print 'write file: ',(dirname+fname)
        Mergeh5(files, f)
        #write merged into
        #ld.writeToOutputFile(f)        

        ######################################################
        # write user info to hdf5 file
        ######################################################
        writeCfgToOutputFile(f, ldr)
        
        ######################################################
        # writing configuration data for user data
        ######################################################
        for det in dets:
            writeUserCfgToOutputFile(f, det, h5ds='UserDataCfg/')
        f.close()

print 'End Ldat 1: ',socket.gethostname(),'done at',time.strftime('%X')
print 'End Ldat 2: time in littleData event for rank: ', rank,' is ',time_ev_sum



