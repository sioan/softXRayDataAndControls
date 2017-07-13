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
maxNevt=1e9
parser = argparse.ArgumentParser()
parser.add_argument("--run", help="run")
parser.add_argument("--exp", help="experiment name")
parser.add_argument("--dir", help="directory for output files (def <exp>/ftc)")
args = parser.parse_args()
if not args.run:
    run=raw_input("Run Number:\n")
else:
    run=args.run
if not args.exp:
    expname=RegDB.experiment_info.active_experiment('XPP')[1]
else:
    expname=args.exp
if args.dir:
    dirname=args.dir+'/'
else:
    dirname = '/reg/d/psdm/xpp/%s/scratch/'%expname
    #dirname = '/reg/d/psdm/xpp/%s/ftc/'%expname

import glob
#h5fileList = glob.glob('/reg/d/psdm/xpp/%s/scratch/tmp_littleDat/ldat_%s_Run%s_r07?.h5'%(expname,expname,run))
h5fileList = glob.glob('/reg/neh/operator/xppopr/experiments/%s/littleData/ldat_%s_Run%s_r*.h5'%(expname,expname,run))
print 'I will merge this now!'
h5fileList.sort()
print h5fileList
#73,75 are broken.
h5fileList=h5fileList[:4]
print '1:',h5fileList
files=[ h5py.File(locfname) for locfname in h5fileList ]

fname = dirname+'ldat_%s_Run%s_simpleMerge.h5'%(expname,run)
f = h5py.File(fname, "w")
print 'write file: ',(fname)
Mergeh5(files, f)
#write merged into
#ld.writeToOutputFile(f)        


print 'merged data only....production to be fixed'

