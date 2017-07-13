import os
import sys
import pylab

#myrange = [5,6,16,17,22,26,36,42,45,79,87,91,96]

for i in pylab.arange(21,30):
#for i in myrange:

	#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psnehq -n 32 mpirun --mca btl ^openib python fastHD5.py $1")
	#batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psnehq -n 32 mpirun --mca btl ^openib python fastHD5c.py "+str(i)+" $1")

	batchSubmit = os.system("bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psnehhiprioq -n 32 mpirun --mca btl ^openib python kboPowerPostCleaning.py "+str(i)+" $1")
  


