import numpy as np
import h5py
import psana

from xppmodules.littleData import *
from xppmodules.utilities import *

import argparse
import time

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

##########################################################
# functions for run dependant parameters
##########################################################

def getROIs(run, expname):
    if expname == 'xpph4915':
    ##harlang, run 17 (cs140_0)
        if run==17:
            sigROI = [[1,2], [23,40], [0,388]]
            sigROI2 = [[0,1], [90,100], [30,170]]
        elif run>=256:
            sigROI = [[1,2], [24,39], [0,388]]
            sigROI2 = [[0,1], [90,100], [30,170]]
        return sigROI, sigROI2
    elif run<=314:
        sigROI = [[1,2], [85,120], [0,388]]
        sigROI2 = [[1,2], [0,184], [30,315]]
    else:
        sigROI = [[1,2], [83,112], [0,388]]
        sigROI2 = [[1,2], [0,184], [30,315]]
    return sigROI, sigROI2

##########################################################
# run independent parameters 
##########################################################
#event codes which signify no xray/laser
xfel_off_codes = [ 162 ]
laser_off_codes = [ 91 ]
#aliases for experiment specific PVs go here
epicsPV = ['alio_position07']
#tt calibration parameters (if passing None, init will use values used during recording
#ttCalibPars = None #[p0, p1, p2]
ttCalibPars = [ 0.8032, -0.002455, 0.0000006187]

##########################################################
#command line input parameter: definitions & reading
##########################################################
maxNevt=1e9
dirname = None
parser = argparse.ArgumentParser()
parser.add_argument("--run", help="run")
parser.add_argument("--exp", help="expeariment name")
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
        
ROIs =  getROIs(int(run), expname=expname)
dets=[]
have_cs140_0 = checkDet(env, 'cs140_0')
if have_cs140_0:
    cs140_0 = DetObject('cs140_0' ,env, int(run), name='vonHamos')
    cs140_0.addROI('ROI',ROIs[0], writeArea=True, rms=cs140_0.rms)
    cs140_0.ROI.addProj('', axis=0)
    cs140_0.ROI.addProj('_thres', axis=0, singlePhoton=False, cutADU=25.)
    cs140_0.ROI.addProj('_ythres', axis=1, singlePhoton=False, cutADU=25.)
    #cs140_0.ROI.addProj('_thres', axis=0, singlePhoton=False, cutRms=3.5)
    dets.append(cs140_0)

have_cs140_1 = checkDet(env, 'cs140_1')
if have_cs140_1:
    cs140_1 = DetObject('cs140_1' ,env, int(run), name='Rowland')
    cs140_1.addROI('ROI',ROIs[1], rms=cs140_1.rms)
    cs140_1.ROI.addProj('_x', axis=0)
    cs140_1.ROI.addProj('_y', axis=1)
    cs140_1.ROI.addProj('_ythres', axis=1, singlePhoton=False, cutADU=25.)
    cs140_1.ROI.addProj('_xthres', axis=0, singlePhoton=False, cutADU=25.)
    dets.append(cs140_1)

haveCsPad = checkDet(env, 'cspad')
if haveCsPad:
    cspad = DetObject('cspad' ,env, int(run), name='cspad')
    dets.append(cspad)
    #setup for the azimuthal integration/averaging
    cspad.azav_eBeam=8.
    cspad.azav_center=[88938,93184.4]#xpph4915, run 256 from FitCircle, select threshold
    cspad.azav_dis_to_sam=60.
    try:
        cspad.addAzAv()
    except:
        print 'no cspad in run %s of experiment %s'%(run, expname)

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
    # add user data - cs140_0
    ##########################################################
    if have_cs140_0:
        cs140_0.evt = dropObject()
        #pedestal subtracted data, common mode if desired
        try:
            cs140_0.evt.dat = cs140_0.det.raw_data(evt)-cs140_0.det.pedestals(evt)        
            cs140_0.det.common_mode_apply(evt, cs140_0.evt.dat)
        except:
            cs140_0.evt.dat = None
        cs140_0.processROIs()
    ##########################################################
    # add user data - cs140_1
    ##########################################################
    if have_cs140_1:
        cs140_1.evt = dropObject()
        try:
            cs140_1.evt.dat = cs140_1.det.raw_data(evt)-cs140_1.det.pedestals(evt)        
            cs140_1.det.common_mode_apply(evt, cs140_1.evt.dat)
        except:
            cs140_1.evt.dat = None
        cs140_1.processROIs()
            
    ##########################################################
    # add user data - cspad
    ##########################################################
    if haveCsPad:
        cspad.evt = dropObject()
        try:
            cspad.evt.dat = cspad.det.raw_data(evt)-cspad.det.pedestals(evt)        
            #cspad.det.common_mode_apply(evt, cspad.evt.dat) #suggest no common mode if strong signal
            cspad.evt.write_azav = cspad.azav.doAzimuthalAveraging(cspad.evt.dat)
        except:
            cspad.evt.dat = None
            nanShp = [ shpi-1 for shpi in cspad.azav.qbins.shape ]
            nanAr = np.empty(nanShp)
            nanAr[:]=np.nan
            cspad.evt.write_azav = nanAr
        ########################################
        # calculate azimuthal average
        ########################################

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
        
if debug:
    print 'time in littleData event for rank: ', rank,' is ',time_ev_sum



