import numpy as np
import argparse

import sys
p = ["./xppmodules/src"]
for pi in p:
    if not (pi in sys.path): sys.path.append(pi)

import littleData
import utilities

###
#import cPickle
#f = open('/reg/d/psdm/xpp/xppi0813/ftc/ldat_xppi0813_Run66_rank000.pkl')
#lds = cPickle.load(f)
###

parser = argparse.ArgumentParser()
parser.add_argument("--run", help="run number", type=int)
parser.add_argument("--expname", help="expname")
args = parser.parse_args()
if args.expname:
    expname = args.expname
else:
    expname = raw_input('Enter the experiment name: ')
if args.run:
    run = args.run
else:
    run = int(raw_input('Enter a run number: '))
    
lds = utilities.getLittleDataFromFile(expname, run)

ipm2sum = lds.ndarray('ipm2.sum')
ipm3sum = lds.ndarray('ipm3.sum')
gdetf22 = lds.ndarray('gdet.f22')
print 'ipm2sum ',ipm2sum.shape
print 'ipm3sum ',ipm3sum.shape
print 'gdetf22 ',gdetf22.shape

if gdetf22.shape != ipm2sum.shape:
    print 'array not same size!!! fix this'
    exit
    

ids = littleData.getFromObj(lds,'eventID.eventID')
fids = [ ID.fiducial() for ID,gdet22this in zip(ids, gdetf22) if (not np.isnan(gdet22this) and gdet22this>2.) ]
ipm2sum_filter = np.where(gdetf22>2.,ipm2sum,None)
#print [ ID.fiducial() for ID,thisipm2 in zip(ids, ipm2sum_filter) if thisipm2 ]

vmin=0.25; vmax=0.5; nbin=5
ibin = [ int((thisipm-vmin)*nbin/(vmax-vmin)) for thisipm in ipm2sum if not np.isnan(thisipm) ]
Ar=[]
for i in range(0,nbin):
    Ar.append( [ thisfid for thisfid,thisibin in zip(fids, ibin) if thisibin == i ])

import matplotlib.pyplot as plt
#plotting examples
ipm2sum_mean = np.nanmean(ipm2sum)
ipm2sum_med = np.median(ipm2sum)

plt.subplot(2,2,1)
plt.title('IPM3 vs gdet22')
plt.plot(ipm3sum, gdetf22, 'b.')

plt.subplot(2,2,2)
plt.title('IPM2 vs IPM3')
plt.plot(ipm2sum, ipm3sum, 'ro', np.where(ipm2sum>0.1,ipm2sum,None), np.where(ipm2sum>0.1,(ipm2sum-ipm3sum)/ipm2sum*10+ipm2sum_med,None), 'b.')
    
#make this a histogram
plt.subplot(2,2,3)
plt.title('ipm3')
plt.hist(np.where(ipm3sum>0.01,ipm3sum,None),bins=np.linspace(0.,10.,num=500))

plt.subplot(2,2,4)
ids = littleData.getFromObj(lds,'eventID.eventID')
fids = [ ID.fiducial() for ID in ids ]
stepNum = lds.ndarray('step.relNum')
crlVal = lds.ndarray('step.ctrlVal')
ttCorr = lds.ndarray('tt.TTSPEC_FLTPOS_PS')
ttVal = crlVal + ttCorr
plt.title('ipm3 vs time delay')
plt.plot(ttVal,ipm3sum,'bo')

plt.show()
