import numpy as np
import h5py
import psana

from xppmodules.littleData import *
from xppmodules.utilities import *

import time
import argparse

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

##########################################################
# run independent parameters 
##########################################################
#event codes which signify no xray/laser
xfel_off_codes = [ 162 ]
laser_off_codes = [ 91 ]
#aliases for experiment specific PVs go here
epicsPV = ['s1h_w']
#tt calibration parameters (if passing None, init will use values used during recording
ttCalibPars = None #[p0, p1, p2]

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

debug = True
time_ev_sum = 0.
try:
    ds = psana.DataSource(dsname)
except:
    print 'we seem to not have small data, you need to use the idx file based Ldat_standard code....'
    sys.exit()
env=ds.env()            
expname = getExpName(env)
        
ldr = littleDataReader()
ldr.getConfig(env, debug)        
ldr.setEpicsUser(epicsPV)
ldr.setBeamOffCodes([xfel_off_codes, laser_off_codes])
ldr.set_ttCalib(ttCalibPars)
if dirname is None:
    dirname = ldr.getLittleDataHdf5Pars(env)
    dirnameTmp=ldr.dirname.replace('ftc','scratch/tmp_littleDat')
else:
    dirnameTmp=dirname
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
    
    #time here.
    time_ev_stop = MPI.Wtime()
    time_ev_sum += time_ev_stop-time_ev_start
##########################################################
# loop over events done, now gather data from all sub-jobs
##########################################################

print 'sub jobs ended, now combining ',rank,' of ',size,' at ',time.ctime(),' with ',len(ld.gdet.f11),' entries'

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
        ######################################################
        # write user info to hdf5 file
        ######################################################
        writeCfgToOutputFile(f, ldr)
        
        f.close()
        

        
if debug:
    print 'time in littleData event for rank: ', rank,' is ',time_ev_sum

MPI.Finalize()

