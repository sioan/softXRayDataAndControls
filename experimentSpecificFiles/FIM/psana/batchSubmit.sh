#!/bin/bash
BATCHPATH=/reg/neh/home/sioan/Desktop/softXRayDataAndControls/experimentSpecificFiles/FIM/psana/
bsub -o $BATCHPATH/%J.log -q psanaq -n 8 mpirun --mca btl ^openib python kbFluorescenceIntensityMonitorWithPnccdRoi.py $1

#bsub -o /reg/neh/home/sioan/Desktop/referenceCodeBits/psana/%J.log -q psanaq -n 32 mpirun --mca btl ^openib python fastHD5.py $1
