import os
import sys
import pylab

myrange = [340]

for i in pylab.arange(21,30):
#for i in myrange:

	#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psnehq -n 32 mpirun --mca btl ^openib python fastHD5.py $1")
	#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psnehq -n 32 mpirun --mca btl ^openib python fastHD5c.py "+str(i)+" $1")
	
	#i is the run number.
	#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psnehhiprioq -n 32 mpirun --mca btl ^openib python turnerSeabergLQ76analysis.py "+str(i)+" $1")

	#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/LQ76/bsubLogs/%J.log -q psnehprioq -n 32 mpirun --mca btl ^openib python turnerSeabergLQ76analysis.py $1")

	#batchSubmit = os.system("bsub -o  /reg/neh/home/sioan/Desktop/upComingExperiments/LQ76/realDataAnalysis/%J.log -q psnehprioq -n 32 mpirun --mca btl ^openib python turnerSeabergLQ76analysis.py "+str(i)+" $1")
	batchSubmit = os.system("bsub -o  /reg/neh/home/sioan/Desktop/upComingExperiments/LQ76/realDataAnalysis/%J.log -q psanaq -n 32 mpirun --mca btl ^openib python turnerSeabergLQ76analysis.py "+str(i)+" $1")
    


