#mpirun -n 2 python mpioffline.py 30
import psana
import sys
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

psana.setConfigFile('xppmodules/src/xpp_cspadMovie.cfg')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("run", help="run number", type=int)
args = parser.parse_args()
run = args.run
ds = psana.DataSource('exp=XPP/xppi0714:run=%d:idx'%run)
#ds = psana.DataSource('exp=XPP/xppf3414:run=%d:idx'%run)

totalStart = MPI.Wtime()

from xppmodules import littleData
from xppmodules import utilities
lds = utilities.getLittleDataFromRun(ds.env().experiment(), run)

#read the data arrays
ipm3sum = lds.ndarray('ipm3.sum')
xStat =  lds.ndarray('lightStatus.xray')
lStat =  lds.ndarray('lightStatus.laser')
crlVal = lds.ndarray('step.ctrlVal')
ttCorr = lds.ndarray('tt.TTSPEC_FLTPOS_PS')
ttVal = crlVal + ttCorr
ids = littleData.getFromObj(lds,'eventID.eventID')
print 'ipm3sum shape: ',ipm3sum.shape
print 'lStat shape ',lStat.shape, ' --- ',lStat.shape[0]
#NEED TO TEST ALSO & MAKE ldat with this first!
ids = [ psana.EventTime( (littleData.getFromObj(lds,'EvtID.time')[i][0]<<32)|(littleData.getFromObj(lds,'EvtID.time')[i][1]),littleData.getFromObj(lds,'EvtID.fid')[i]) for i in range(0,lStat.shape[0]) ]

#for actual data
fids = [ ID for ID,ipm3,xray,laser,tt in zip(ids, ipm3sum, xStat,lStat, ttVal) if (ipm3>1. and ipm3 < 9. and xray>0 and laser>0) and tt < 10. and tt > -2.]
#for my test run
fids = [ ID for ID,ipm3,xray,laser,tt in zip(ids, ipm3sum, xStat,lStat, ttVal) if (ipm3>0. and ipm3 < 9. and xray>0 and laser>0) and tt < 10. and tt > -2.]
fids = ids

filteredTime = MPI.Wtime()

print 'split the selected ',len(fids),' events from ',ipm3sum.shape,' total into ',size,' chunks'
mylength = len(fids)/size
mylength = min(10, mylength)
for run in ds.runs():
    #times = run.times()
    mytimes= fids[rank*mylength:(rank+1)*mylength]
    befLoopTime = MPI.Wtime()
    for i in range(mylength):
        evt = run.event(mytimes[i])
        if evt is None:
            print '*** event fetch failed'
            continue
    #print 'end of run!'
    endrunTime = MPI.Wtime()
    run.end()

#totalStart = MPI.Wtime()
#filteredTime = MPI.Wtime()
#befLoopTime = MPI.Wtime()
#endrunTime = MPI.Wtime()
print "rank", rank," start to filter ", str(filteredTime-totalStart)," in loop ", str(endrunTime-befLoopTime)
#print 'end of job!'
