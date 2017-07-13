# importing generic python modules
import numpy as np
import h5py
import psana
import time
import argparse
import socket

# importing xpp specific modules
from littleData import *
from utilities import *

# setting up MPI 
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

########################################################## 
##
## User Input start --> 
##
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
##
## <-- User Input end
##
########################################################## 

##########################################################
#command line input parameter: definitions & reading
##########################################################
maxNevt=1e9
chunkSize=-1
dirname = None
parser = argparse.ArgumentParser()
parser.add_argument("--run", help="run")
parser.add_argument("--exp", help="expeariment name")
parser.add_argument("--nevt", help="number of events", type=int)
parser.add_argument("--dir", help="directory for output files (def <exp>/hdf5/smalldata)")
parser.add_argument("--offline", help="run offline (def for current exp from ffb)")
parser.add_argument("--chunks", help="use Chunks of size", type=int)
args = parser.parse_args()
if not args.run:
    run=raw_input("Run Number:\n")
else:
    run=args.run
if not args.exp:
    hutches=['amo','sxr','xpp','xcs','mfx','cxi','mec']
    hostname=socket.gethostname()
    hutch=None
    for thisHutch in hutches:
        if hostname.find(thisHutch)>=0:
            hutch=thisHutch.upper()
    if hutch is None:
        #then check current path
        path=os.getcwd()
        for thisHutch in hutches:
            if path.find(thisHutch)>=0:
                hutch=thisHutch.upper()
    if hutch is None:
        print 'cannot figure out which experiment to use, please specify -e <expname> on commandline'
        sys.exit()
    expname=RegDB.experiment_info.active_experiment(hutch)[1]
    dsname='exp='+expname+':run='+run+':smd:dir=/reg/d/ffb/%s/%s/xtc:live'%(hutch.lower(),expname)
else:
    expname=args.exp
    dsname='exp='+expname+':run='+run+':smd'
if args.offline:
    dsname='exp='+expname+':run='+run+':smd'
if args.ffb:
    dsname='exp=%s:run='+run+':smd:dir=/reg/d/ffb/%s/%s/xtc'%(expname,expname[0:3],expname)
if args.chunks:
    chunkSize=args.chunks
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
    dirnameTmp=ldr.dirname.replace('hdf5/smalldata','scratch/tmp_littleDat')
else:
    dirnameTmp=dirname
#littleData serves to make cube!
ldr.setReqDet('cspad')

N_RESIZE=100
currIdx=-1
currSize=N_RESIZE

if chunkSize<0:
    ld = littleData()
else:
    fname = dirname+'ldat_%s_Run%03d.h5.inprogress'%(expname,int(run))
    f = h5py.File(fname, "w",driver='mpio',comm=comm)

EVRdet = psana.Detector('evr0',ds.env())
for eventNr, evt in enumerate(ds.events()):
    printMsg(eventNr, evt.run())
    time_ev_start = MPI.Wtime()

    if eventNr >= maxNevt:
        break

    #check for EVR and pass if not EVR not there
    if EVRdet.eventCodes(evt) is None:
        continue

    allDets = True
    aliases = [ k.alias() for k in evt.keys() ]
    for detn in ldr.reqDet:
        if not detn in aliases:
            allDets = False
    if not allDets:
        continue

    #check event & quit here before counting event for hdf5 file writing
    currIdx+=1    
    if chunkSize>=0:
        if currIdx >= currSize:
            comm.Barrier()
            resizeHdf5File_mpi(f, numResize=currSize+N_RESIZE)
            currSize+=N_RESIZE

        #now only process this ranks events - unless it's the first event:
        if currIdx%size != rank and currIdx>0:
            continue

        ld = littleData()
    else:
        if eventNr%size != rank:
            continue

    ##########################################################
    # extract generic data for the little hdf5 file from event
    ##########################################################
    ldr.extractValues(evt, env, ld)
    
    #only for mpiWriting
    if chunkSize>=0:
        if currIdx>0:
            ld.writeToOutputFile_mpi(f, currIdx)
        if currIdx==0:
            if rank==0:
                print 'DEBUG: chunksize:',chunkSize
            ld.setupHdf5File_mpi(f, currSize=N_RESIZE, chunkSize=chunkSize)
            if rank==currIdx:
                ld.writeToOutputFile_mpi(f, currIdx)

    #time here.
    time_ev_stop = MPI.Wtime()
    time_ev_sum += time_ev_stop-time_ev_start
##########################################################
# loop over events done, now gather data from all sub-jobs
##########################################################

print 'sub jobs ended, now combining ',rank,' of ',size,' at ',time.ctime(),' with ',len(ld.gdet.f11),' entries'

#for mpiWriting
#set final size of dataset
if chunkSize>=0:
    comm.Barrier()
    resizeHdf5File_mpi(f, numResize=currIdx+1)

#mpiGathering
elif chunkSize==-1:
    ldGather = gatherLittleData(ld)
            
    if rank==0:
        print 'We are using mpiGathering for debugging reasons'
        fname = dirname+'ldat_%s_Run%03d.h5'%(expname,evt.run())
        f = h5py.File(fname, "w")
        print 'write file: ',(fname)
        ldGather.writeToOutputFile(f,debug=True)        
#use old way that mis-uses memory somewhat, but at least works....
else:
    if rank==0:
        print 'We are using the old way to writing the separate files and combine, eventhough inefficienct as it works.'
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

if chunkSize>=0 or rank==0:
    ######################################################
    # write user info to hdf5 file
    ######################################################
    writeCfgToOutputFile(f, ldr)
                
print 'End LittleDataProduction: ',socket.gethostname(),' done at',time.strftime('%X'),' time in littleData event for rank: ', rank,' is ',time_ev_sum

if chunkSize>=0:
    comm.Barrier()
    f.close()
    if rank==0:
        fname = dirname+'ldat_%s_Run%03d.h5.inprogress'%(expname,int(run))
        fnameFinal = dirname+'ldat_%s_Run%03d.h5'%(expname,int(run))    
        os.rename(fname, fnameFinal)

MPI.Finalize()

