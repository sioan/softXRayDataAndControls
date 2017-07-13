import h5py
import time
import numpy as np
from matplotlib import pyplot as plt
import argparse
import resource
import sys
import os
import socket
import json
import RegDB.experiment_info
from utilities import rebin
from utilities import hasKey
from utilities import getDelay
from utilities import addToHdf5
from utilities import getBins
from utilities import reduceVar
from littleData import DetObject
from littleData import dropObject
from scipy import ndimage
import LittleDataAna as lda
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

###########################
# set commandline parameters
###########################
time_init = time.time()
memstart=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.
parser = argparse.ArgumentParser()
parser.add_argument("--run", help="run")
parser.add_argument("--exp", help="experiment name")
parser.add_argument("--cube", help="cube file")
parser.add_argument("--raw", help="save cspad array in raw data format",action='store_true')
parser.add_argument("--rebinTo", help="rebin cspad image to X",type=int)
parser.add_argument("--cm", help="apply common mode",type=int)
parser.add_argument("--thresADU", help="apply threshold in ADU",type=float)
parser.add_argument("--thresRms", help="apply threshold in rms from pedestal",type=float)
parser.add_argument("--overflow", help="save overflow bins",action='store_true')
parser.add_argument("--dir", help="output directory")
parser.add_argument("--debug", help="print debug information",action='store_true')
parser.add_argument("--test", help="run only over 5 evts/bin",action='store_true')
args = parser.parse_args()

debug=False
if args.debug:
    debug=True

#check variables
cubeName=''
if not args.cube:
    #cubeName = (raw_input('need cubename as input: '))+'.txt'
    print 'no cube name was given '
    sys.exit()
else:
    cubeName = args.cube
jsonCube = json.load(open(cubeName,'r'))
#print jsonCube

if not args.run:
    print 'we need a run number as input!'
    sys.exit()
else:
    runIn=args.run

if not args.exp:
    expname=RegDB.experiment_info.active_experiment('XPP')[1]
    #dsname='exp='+expname+':run='+runIn+':smd:dir=/reg/d/ffb/xpp/%s/xtc:live'%expname
    dsname='exp='+expname+':run='+runIn+':idx:dir=/reg/d/ffb/xpp/%s/xtc'%expname
else:
    expname=args.exp
    dsname='exp='+expname+':run='+runIn+':idx'

dirname = '/reg/d/psdm/xpp/%s/hdf5/smalldata'%expname
if not os.path.exists(dirname):
    dirname = dirname.replace('hdf5/smalldata','ftc')
mylda = lda.LittleDataAna(expname,int(runIn),dirname=dirname)
if not mylda.fh5:
    print 'no hdf5 file, will quit'; sys.exit()
if not mylda.hasKey(jsonCube[0]) and jsonCube[0] != 'delay':
    print 'bin variable %s not in hdf5 file, please check!'%(jsonCube[0])
    sys.exit()
for cut in jsonCube[3]:
    if not mylda.hasKey(cut[0]) and cut[0] != 'delay' and len(cut)>1:
        print 'variable for cut %s is not in h5 file'%cut[0]

time_readLittleData = time.time()



# first load the reduced data format
f = mylda.fh5
cuts = jsonCube[3]

#if mylda.hasKey('enc/lasDelay'):
#    delay = getDelay(f, use_ttCorr=True, addEnc=True)
#else:
#    delay = getDelay(f, use_ttCorr=True, addEnc=False)
delay = getDelay(f, use_ttCorr=True)

filters=[]
Filter=np.ones_like(delay).astype(bool)
for thiscut in cuts:
    if len(thiscut)==1:
        continue
    if debug and rank==0:
        print 'cut: %g < %s < %g'%(thiscut[1],thiscut[0],thiscut[2])
    if thiscut[0] != 'delay':
        thisPlotvar=f[thiscut[0]].value
    else:
        thisPlotvar = delay
    filters.append(~np.isnan(thisPlotvar))
    if len(thiscut)==3:
        filters.append((thisPlotvar > thiscut[1]) & (thisPlotvar < thiscut[2]))
    else:
        filters.append(thisPlotvar != thiscut[1])
for ft in filters:
    Filter&=ft                
for thiscut in cuts:
    if len(thiscut)==1:
        fname = '%s_Run%03d.txt'%(cut[0],int(runIn))
        #check that file exists
        if not os.path.isfile(fname):
            if debug and rank==0:
                print 'could not find file with bool array: ',fname,os.path.isfile(fname)
            continue
        #read file
        specialFilter = np.loadtxt(fname).astype(bool)
        if debug and rank==0:
            print 'read special filter from: ',fname
            print len(Filter),len(specialFilter), filters[0].shape
        if len(Filter)==len(specialFilter):
            Filter&=specialFilter

# create the bins for the cube
Bins = getBins(jsonCube[1], f)
#because we have under flow, 0-1, 1-2,....,n-1-n,overflow....except in unique case...
if args.overflow:
    numBin=len(Bins)+1
else:
    if jsonCube[0] == 'delay':
        Filter&=delay>Bins[0]  
        Filter&=delay<Bins[-1] 
    else:
        Filter&=f[jsonCube[0]].value>Bins[0]
        Filter&=f[jsonCube[0]].value<Bins[-1]
    numBin=len(Bins)-1

if jsonCube[0] == 'delay':
    binVar = delay[Filter]
else:
    binVar = f[jsonCube[0]].value[Filter]
    #lxt_ttc scan
    if binVar.mean()<1e-9:
        binVar*=1e12

if rank==0:
    print 'Run %s has %i events of which we select %i (%g percent)'%(runIn, delay.shape[0],binVar.shape[0],float(binVar.shape[0])/delay.shape[0]*100)

if binVar.shape[0] == 0:
    print 'did not select any event, quit now!'
    sys.exit()

#now create event->bin mapping. (len(Bins)-1 bins (using bins as edges) + 0-bin & numBin nim for under/overflow)
if args.overflow:
    binNum = np.digitize(binVar, Bins, right=True)
else:
    binNum = np.digitize(binVar, Bins[1:], right=True)
#now check how many jobs I have for each core. Have NumBins+1 bins including the over & underflow.
bins_per_job = numBin/size + int((numBin%size)/max(1,numBin%size))

nEvts_bin = np.bincount(binNum)

if rank==0:
    print len(nEvts_bin),' nEvts_bin: ',nEvts_bin
    
##################
# define & write data to hdf5 file
##################
if args.dir:
    dirname = args.dir
#fname = dirname+"Cube_%s_Run%s"%(cubeName.replace('.txt','').replace('CubeSetup_',''),runIn)
cubeName = cubeName.replace('.txt','').replace('CubeSetup','')
if args.raw:
    cubeName+="_raw"
if args.thresADU:
    cubeName+="_thresADU"
if args.thresRms:
    cubeName+="_thresRms"
if args.cm:
    cubeName+="_cm%i"%args.cm
if args.rebinTo:
    cubeName+="_binTo%i"%args.rebinTo
if dirname.find('/')<=0:
    dirname+='/'
cubeFileName = dirname+mylda.fname.split('/')[-1].replace('ldat_','Cube_').replace('.h5','%s.h5.inprogress'%cubeName)
if rank==0:
    print 'now write outputfile to : ',cubeFileName
fout = h5py.File(cubeFileName, "w",driver='mpio',comm=MPI.COMM_WORLD)

############
# now we write the hdf5 file "small data"
############

for tVar in jsonCube[2]:
    if isinstance(tVar,list):
        tVar = tVar[0]
    if mylda.hasKey(tVar):
        var_binned1d = None
        if len(f[tVar].shape)==1:
            var_binned = np.bincount(binNum, f[tVar].value[Filter])
        elif len(f[tVar].shape)==2:
            var_binned = np.array([ np.bincount(binNum,f[tVar].value[Filter][:,i]) for i in np.arange(f[tVar].value[Filter].shape[1]) ])
            var_binned1d = np.bincount(binNum, f[tVar].value[Filter].squeeze().mean(axis=1))
        else:
            var_binned1d = np.bincount(binNum, f[tVar].value[Filter].squeeze().mean(axis=1).mean(axis=1))

            var_bin2d = f[tVar].value[Filter].squeeze().mean(axis=1)
            var_binned2d = np.array([ np.bincount(binNum,var_bin2d[:,i]) for i in np.arange(var_bin2d.shape[1]) ])
            addToHdf5(fout, tVar.replace('/','_')+'_2d', var_binned2d.transpose())
            arsz = 1; arShape=();nevtSel = f[tVar].value[Filter].shape[0]
            for sz in f[tVar].value[Filter].shape[1:]:
                if [sz != 1]:
                    arsz*=sz
                    arShape+=(sz,)
            arShapeBin=arShape+(numBin,)
            newAr = f[tVar].value[Filter].reshape(nevtSel, arsz)
            if args.thresADU :
                newAr[newAr<args.thresADU]=0
            var_binned = np.array([ np.bincount(binNum, newAr[:,i]) for i in np.arange(newAr.shape[1]) ])
            var_binned = var_binned.transpose()
            var_binned = np.array([ binDat.reshape(arShape) for binDat in var_binned])
        addToHdf5(fout, tVar.replace('/','_'), var_binned)
        if rank==0:
            print 'adding variable %s to hdf5 cube '%tVar
        if var_binned1d is not None:
            addToHdf5(fout, tVar.replace('/','_')+'_1d', var_binned1d)
addToHdf5(fout, 'nEntries', nEvts_bin)
if debug:
    print 'nEvts_bin ',nEvts_bin.shape,' -- ',nEvts_bin
    print fout.keys()
addToHdf5(fout, 'bins', np.array(Bins))

############
# now we get the event indices for the big data
############

if len(Bins)>=2:
    Bins = np.append(Bins,2*Bins[-1]-Bins[-2])

detnames = []
for tVar in jsonCube[2]:
    detName = tVar
    if isinstance(tVar,list):
        detName = tVar[0]
    if not mylda.hasKey(detName):
        if rank==0:
            print 'big data detector: ',tVar
        detnames.append(tVar)
if len(detnames) == 0:
    if rank==0:
        print 'writing: ',fout.filename
    comm.Barrier()
    print fout.keys()
    fout.close()
    if rank==0:
        print 'no detector from xtc requested, renaming file now from %s to %s'%(cubeFileName,cubeFileName.replace('.inprogress',''))
        os.rename(cubeFileName, cubeFileName.replace('.inprogress',''))
    sys.exit()

time_readXtc = time.time()
#now get the event time stamps to get the 'big' data from.
evtfid = f['EvtID/fid'].value[Filter]
evttime = f['EvtID/time'].value[Filter]
allfids=[]
for iBin,thisBin in enumerate(Bins):
    thesefids = [ (ifid,itime) for ifid,itime,iiBin in zip(evtfid,evttime,binNum) if (iiBin==iBin)]
    if debug and rank==0:
        print 'bin, nFiducials: ',iBin,len(thesefids)
    allfids.append(thesefids)

if rank==0:
    print 'now looking for source from the xtc file'
import psana
try:
    ds = psana.DataSource(dsname)
except:
    print 'failed to read the data'
    sys.exit()


run = ds.runs().next()
#adjust better to possible list of detectors. as in make this inner loop....
#detName = 'DetInfo(XppGon.0:Cspad.0)'
for detName in detnames:
    print 'detname ',detName
    ROI = None
    if isinstance(detName,list):
        ROI = detName[1]
        detName = detName[0]
    if rank==0:
        print 'now looking for detector: ',detName
    #define detector object & get raw data shape from pedestal
    common_mode = 0
    if args.cm:
        common_mode = args.cm
    try:
        det = psana.Detector(detName)
        if rank==0:
            print 'success with detname',detName
        det = DetObject(detName, ds.env(), run=int(runIn), common_mode=common_mode)
    except:
        print 'could not create detector object %s for '%detName
        sys.exit()

    if det.rms is not None:
        if args.raw:
            addToHdf5(fout, detName+'_ped', det.ped)
            addToHdf5(fout, detName+'_rms', det.rms)
            if det.x is not None:
                addToHdf5(fout, detName+'_x', det.x)
                addToHdf5(fout, detName+'_y', det.y)
        else:
            addToHdf5(fout, detName+'_ped', det.det.image(int(runIn),det.ped))
            addToHdf5(fout, detName+'_rms', det.det.image(int(runIn),det.rms))

    detShape = det.ped.shape
    if rank==0:
        print 'got the pedestals now: shape is', detShape
    lS = list(detShape);lS.insert(0,bins_per_job);csShape=tuple(lS)
    cspad_arrayBin=np.zeros(csShape)

    binID=np.ones(bins_per_job,dtype=int); binID*=-1
    time_startLoop = time.time()

    if rank==0:
        print 'start loop over bins '
    for ib,bins in enumerate(allfids):
        if not (ib>=(bins_per_job*rank) and ib < bins_per_job*(rank+1)):
            continue
        print 'bin: %d has %d events'%(ib, len(bins))
        binID[ib%bins_per_job]=ib
        if debug:
            print rank,ib,binID.shape,'------',binID
        for ievt,evtts in enumerate(bins):
            evtt = psana.EventTime(int(evtts[1][0]<<32|evtts[1][1]),int(evtts[0]))
            evt = run.event(evtt)
            det.evt = dropObject()
            det.getData(evt)
            try:
                data = det.evt.dat
            except:
                print 'could not get data from event'
                continue
            if data is None:
                if debug:
                    print 'no ',detName,' in event'
                continue
            if args.thresADU :
                data[data<args.thresADU]=0
            if args.thresRms :
                data[data<(args.thresRms*det.rms)]=0
            cspad_arrayBin[ib%bins_per_job] += data
            #print 'datamean bint ',ib%bins_per_job, cspad_arrayBin[ib%bins_per_job].mean()
            if args.test and ievt>5+ib:
                print 'test setup, only get 5 evnts'
                print 'bin mean: ',cspad_arrayBin[ib%bins_per_job].mean()
                break
        print 'bin: %d finished %d events, running on host %s'%(ib, len(bins),socket.gethostname())
    time_endLoop = time.time()

    if rank==0:
        print 'now at the of the loop', cspad_arrayBin[0].shape
    if not args.raw and ROI is None:
        cspadImageArray=[]
        for thisArray,thisBin in zip(cspad_arrayBin,binID):            
            if thisBin>=0: 
                print thisBin,thisArray.shape, thisArray.mean()
            img = det.det.image(int(runIn),thisArray)
            print img.mean()
            if args.rebinTo:
                factor = float(int(img.shape[0]/args.rebinTo)+1)
                bigImg = ndimage.zoom(img, [args.rebinTo*factor/img.shape[0],args.rebinTo*factor/img.shape[1]])
                img = rebin(bigImg, [args.rebinTo, args.rebinTo])
            cspadImageArray.append(img)
            #print 'image shape: ',thisArray.shape,cspadImageArray[-1].shape
        cspadOutput = np.array(cspadImageArray)
    else:
        if ROI is not None:
            print 'use ROI: ',ROI
            cspad_arrayBin = reduceVar(cspad_arrayBin, ROI)
        cspadOutput = np.array(cspad_arrayBin)

    time_calcoutArray = time.time()

    ############
    # now we write the cube
    ############
    arShape=(numBin,)
    for i in range(0,len(cspadOutput[0].shape)):
        arShape+=(cspadOutput[0].shape[i],)
    if rank==0:
        print 'print array shape before saving: ',arShape
    cubeData = fout.create_dataset('%s'%detName,arShape)
    for islice,slice in enumerate(cspadOutput):
        print islice, slice.sum()
        if slice.sum()>0:
            cubeData[rank*bins_per_job+islice,:] = slice
            print cubeData[rank*bins_per_job+islice,:].mean(), cubeData[rank*bins_per_job+islice,:].std()
    print fout['%s'%detName][0].mean()
    print fout['%s'%detName][-1].mean()

comm.Barrier()
fout.close()
if rank==0:
    #cubeFileName = dirname+mylda.fname.split('/')[-1].replace('.h5','_w%s.h5.inprogress'%cubeName)
    print 'renaming file now from %s to %s'%(cubeFileName,cubeFileName.replace('.inprogress',''))
    os.rename(cubeFileName, cubeFileName.replace('.inprogress',''))

############
#finish up now (print all times,...):
############
time_end = time.time()
print 'time in rank %i of %i on node %s: total %f, to read Xtc %f, evtLoop %f, make image %f, write file %f'%(rank,size,socket.gethostname(),time_end-time_init,time_readXtc-time_init,time_endLoop-time_startLoop,time_calcoutArray-time_endLoop,time_end-time_calcoutArray)
memend=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.
print 'memory in rank %i of %i: start %f, end %f '%(rank,size,memstart,memend)

MPI.Finalize()
