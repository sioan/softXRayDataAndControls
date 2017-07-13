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
    if run == 23:
        sigROI = [[1,2],[77,173],[125,148]]
        sigROI2 = [[0,1],[87,176],[172,193]]
    elif run == 26:
        sigROI = [[1,2], [28,174], [118,155]]
        sigROI2 = [[0,1], [70,173], [177,192]]
    elif run in list(range(28,38+1)):
        sigROI = [[1,2], [3,183], [111,147]]
        sigROI2 = [[1,2], [12,181], [232,263]]
    elif run in [39]:
        sigROI = [[1,2], [0,183], [107,152]]
        sigROI2 = [[1,2], [0,183], [221,272]]
    elif run in [47,48]:
        sigROI = [[1,2], [81,183], [92,157]]
        sigROI2 = [[1,2], [90,184], [219,279]]
    elif run == 53:
        sigROI = [[1,2], [37,183], [113,150]]
        sigROI2 = [[1,2], [27,182], [233,272]]
    elif run == 56:
        sigROI = [[1,2], [43,180], [116,146]]
        sigROI2 = [[1,2], [29,181], [234,272]]
    elif run in [57,58]:
        sigROI = [[1,2], [51,176], [116,144]]
        sigROI2 = [[1,2], [35,174], [239,266]]
    elif run == 59:
        sigROI = [[1,2], [50,178], [113,146]]
        sigROI2 = [[1,2], [46,177], [238,270]]
#    elif run in [75,76,78]: # larger ROI for diffuse scattering
#        sigROI = [[1,2], [4,183], [4,162]]
#        sigROI2 = [[1,2], [6,183], [227,382]]
    elif run > 59 and run < 84:
        sigROI = [[1,2], [37,176], [113,144]]
        sigROI2 = [[1,2], [27,180], [234,272]]
    elif run > 85 and run < 179:
        sigROI = [[1,2], [50,180], [110,145]]
        sigROI2 = [[1,2], [25,180], [235,275]]
    elif run in [183,184]:
        sigROI = [[1,2], [30,150], [105,150]]
        sigROI2 = [[1,2], [40,160], [235,275]]
    elif run > 184 and run < 201:
        sigROI = [[1,2], [40,135], [115,145]]
        sigROI2 = [[1,2], [40,140], [235,265]]
        #larger ROIs
        #sigROI = [[1,2], [5,155], [90,180]]
        #sigROI2 = [[1,2], [5,160], [210,285]]
    elif run > 201 and run < 225:
        sigROI = [[1,2], [65,180], [110,150]]
        sigROI2 = [[1,2], [65,180], [230,270]]
    elif run > 225 and run < 228:
        sigROI = [[1,2], [70,180], [105,150]]
        sigROI2 = [[1,2], [55,180], [230,270]]
    elif run > 228 and run < 243:
        sigROI = [[1,2], [5,180], [100,150]]
        sigROI2 = [[1,2], [11,180], [225,275]]
    elif run > 242 and run < 277:
        sigROI = [[1,2], [35,180], [100,155]]
        sigROI2 = [[1,2], [5,180], [220,285]]
    elif run > 276 and run < 283:
        sigROI = [[1,2], [45,140], [120,145]]
        sigROI2 = [[1,2], [70,170], [230,265]]
    elif run > 282 and run < 284:
        sigROI = [[1,2], [45,140], [120,145]]
        sigROI2 = [[1,2], [70,170], [230,265]]
    elif run > 283 and run < 288:
        sigROI = [[1,2], [55,180], [105,155]]
        sigROI2 = [[1,2], [35,180], [220,275]]
    elif run > 287:
        sigROI = [[1,2], [10,175], [105,150]]
        sigROI2 = [[1,2], [5,160], [230,275]]
    else:
        return None, None

    assert (len(sigROI) == 3 and len(sigROI[0]) == 2 and
            len(sigROI[1]) == 2 and len(sigROI[2]) == 2
            ), "sigROI not in good format"
    assert (len(sigROI2) == 3 and len(sigROI2[0]) == 2 and
            len(sigROI2[1]) == 2 and len(sigROI2[2]) == 2
            ), "sigROI2 not in good format"

    return sigROI, sigROI2

##########################################################
# run independent parameters 
##########################################################
#event codes which signify no xray/laser
xfel_off_codes = [ 162 ]
laser_off_codes = [ 91 ]
#aliases for experiment specific PVs go here
epicsPV = ['sam_r','sam_x','sam_y','sam_z','mag_h', 'MagnetCmd']
#tt calibration parameters (if passing None, init will use values used during recording
#ttCalibPars = None #[p0, p1, p2]
ttCalibPars = [ 0.8032, -0.002455, 0.0000006187]
AIOPars= [[0],['magV']]

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
ldr.set_AIO(AIOPars)

ROIs =  getROIs(int(run), expname=expname)
dets=[]
have_cs140_0 = checkDet(env, 'cs140_0')
if have_cs140_0:
    cs140_0 = DetObject('cs140_0' ,env, int(run), name='Up')
    cs140_0.addROI('ROI',ROIs[0],writeArea=True, rms=cs140_0.rms)
    cs140_0.ROI.addProj('_x', axis=0)
    cs140_0.ROI.addProj('_y', axis=1)
    cs140_0.ROI.addProj('_xthres', axis=0, singlePhoton=False, cutADU=25.)
    cs140_0.ROI.addProj('_ythres', axis=1, singlePhoton=False, cutADU=25.)
    dets.append(cs140_0)

have_cs140_1 = checkDet(env, 'cs140_1')
if have_cs140_1:
    cs140_1 = DetObject('cs140_1' ,env, int(run), name='Down')
    cs140_1.addROI('ROI',ROIs[1], writeArea=True, rms=cs140_1.rms)
    cs140_1.ROI.addProj('_x', axis=0)
    cs140_1.ROI.addProj('_y', axis=1)
    cs140_1.ROI.addProj('_ythres', axis=1, singlePhoton=False, cutADU=25.)
    cs140_1.ROI.addProj('_xthres', axis=0, singlePhoton=False, cutADU=25.)
    dets.append(cs140_1)


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



