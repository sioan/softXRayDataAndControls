#!/bin/bash
EXP=$1
RUN=$2

bsub -o %J.log -q psnehhiprioq -n 15 mpirun --mca btl ^openib psanaXtcDataExtractor.py -e ${EXP} -r ${RUN}
