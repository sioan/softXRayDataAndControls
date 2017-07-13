import numpy as np
import h5py
import psana

from xppmodules.littleData import *
from xppmodules.utilities import *

import argparse
import time

##########################################################
#command line input parameter: definitions & reading
##########################################################
parser = argparse.ArgumentParser()
parser.add_argument("--runStart", help="start run",type=int)
parser.add_argument("--runEnd", help="end run",type=int)
parser.add_argument("--exp", help="experiment name")
parser.add_argument("--dir", help="directory for output files (def <exp>/ftc)")
parser.add_argument("--cubeName", help="cube name")
args = parser.parse_args()
if not args.exp:
    expname=RegDB.experiment_info.active_experiment('XPP')[1]
else:
    expname=args.exp
if args.dir:
    dirname=args.dir+'/'
else:
    #dirname = '/reg/d/psdm/xpp/%s/scratch/'%expname
    dirname = '/reg/d/psdm/xpp/%s/ftc/'%expname

h5fileList=[]
for run in range(args.runStart, args.runEnd+1):
    if args.cubeName:
        h5fileList.append('/reg/d/psdm/xpp/%s/ftc/Cube_%s_Run%03d_%s.h5'%(expname,expname,run,args.cubeName))
    else:
        #will need a glob here
        h5fileList.append('/reg/d/psdm/xpp/%s/ftc/Cube_%s_Run%03d_*.h5'%(expname,expname,run))
h5fileList.sort()
print h5fileList

fOutName = '/reg/d/psdm/xpp/%s/scratch/Cube_%s_Run%iTo%i_%s.h5'%(expname,expname,args.runStart,args.runEnd,args.cubeName)
print fOutName
fOut =  h5py.File(fOutName,'w')

firstFile = h5py.File(h5fileList[0],'r')
addFiles=[]
for addFileName in h5fileList[1:]:
    addFile = h5py.File(addFileName,'r')
    if (addFile['cube/bins'].shape == firstFile['cube/bins'].shape):
        if (addFile['cube/bins'].value-firstFile['cube/bins'].value).sum()==0:
            print 'add file: ',addFileName
            addFiles.append(addFile)

for key in firstFile['cube']:
    print key
    data=firstFile['cube'][key].value
    print data.shape
    for addFile in addFiles:
        data += addFile['cube'][key].value
        print 'add', data.shape
    dset = fOut.create_dataset(('cube/'+key), data.shape, dtype=(data.dtype))
    dset[...] = np.array(data)
fOut.close()

