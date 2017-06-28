import os
import sys
import pylab

nEvents = 72000
myRuns = [122,123]

for i in myRuns:
	for j in pylab.arange(1000,nEvents,1000):
#for i in myrange:

		#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psnehq -n 32 mpirun --mca btl ^openib python fastHD5.py $1")
		#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psnehq -n 32 mpirun --mca btl ^openib python fastHD5c.py "+str(i)+" $1")
	
		#i is the run number.
		#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psnehhiprioq -n 32 mpirun --mca btl ^openib python turnerSeabergLQ76analysis.py "+str(i)+" $1")

		#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/LQ76/bsubLogs/%J.log -q psnehprioq -n 32 mpirun --mca btl ^openib python turnerSeabergLQ76analysis.py $1")

		#batchSubmit = os.system("bsub -o  /reg/neh/home/sioan/Desktop/upComingExperiments/LQ76/realDataAnalysis/logs/%J.log -q psnehprioq -n 32 mpirun --mca btl ^openib python turnerSeabergLQ76analysis.py "+str(i)+" $1")
		batchSubmit = os.system("bsub -o  /reg/neh/home/sioan/Desktop/upComingExperiments/LQ76/realDataAnalysis/logs/%J.log -q psanaq -n 32 mpirun --mca btl ^openib python turnerSeabergLQ76analysis.py "+str(i)+" "+str(j)+" $1")
	    

		batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/experimentSpecificFiles/FIM/psana/%J.log -q psnehhiprioq -n 32 mpirun --mca btl ^openib python kbFluorescenceIntensityMonitorWithPnccdRoi.py $1")
