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
runInput = args.run
ds = psana.DataSource('exp=XPP/xppf0814:run=%d:idx'%runInput)

totalStart = MPI.Wtime()

for run in ds.runs():
    times = run.times()
    mylength = len(times)/size
    #restrict length for debugging
    mylength = min(mylength,10)
    mytimes= times[rank*mylength:(rank+1)*mylength]
    befLoopTime = MPI.Wtime()
    for i in range(mylength):
        evt = run.event(mytimes[i])
        print 'print fid: ',evt.get(psana.EventId).fiducials()
        #if (mylength-i)<3:
        #    print 'acccess event! rank: ',rank, ' evt#  ',i
        if evt is None:
            print '*** event fetch failed'
            continue
    #print 'now end run',rank
    endrunTime = MPI.Wtime()
    run.end()
    #print 'and done!', rank

#totalStart = MPI.Wtime()
#filteredTime = MPI.Wtime()
#befLoopTime = MPI.Wtime()
#endrunTime = MPI.Wtime()
print "rank", rank," start to begin ", str(befLoopTime-totalStart)," in loop ", str(endrunTime-befLoopTime)
#print 'end of job!'

