#!/bin/bash

myhost=`hostname`
if [[ $myhost != *"psana"* ]]
then
  echo "Need to be logged in to psana node to submit jobs"
  exit
fi
cd /reg/d/psdm/sxr/sxrlq2715/hdf5/smalldata/

#Normal source environment
source /reg/g/psdm/etc/psconda.sh

# offline system
#bsub -o log/%J.log -q psanaq -n 24 mpirun --mca btl ^openib python sxrlq2715.py $1
# priority system only to be used while experiment has no beam
#bsub -o log/%J.log -q psnehprioq -n 64 mpirun --mca btl ^openib python sxrlq2715.py $1
# high priority system (only to be used while experiment has beam)
bsub -o log/%J.log -q psnehhiprioq -n 64 mpirun --mca btl ^openib python sxrlq2715.py $1
