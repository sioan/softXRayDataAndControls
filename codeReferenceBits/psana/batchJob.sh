#!/bin/bash
myhost=`hostname`
if [[ $myhost != *"psana"* ]]
then
  echo "Need to be logged in to psana node to submit jobs"
  exit
fi
#cd ~sioan/Desktop/psana/
#source /reg/g/psdm/etc/ana_env.sh
# offline system
#bsub -o %J.log -q psanaq -n 24 mpirun python fastHD5.py $1
# high priority system (only to be used while experiment has beam)
# bsub -o /reg/d/psdm/sxr/sxrn2316/scratch/cpo/%J.log -q psnehhiprioq -n 32 mpirun python sxrn2316.py $1
#bsub -o /reg/d/psdm/sxr/sxrn2316/scratch/cpo/%J.log -q psnehhiprioq -n 32 mpirun python fastHD5.py $1

#bsub -o /reg/neh/home/sioan/Desktop/psana/%J.log -q psanaq -n 2 mpirun python fastHD5.py $1

#bsub -o /reg/neh/home/sioan/Desktop/referenceCodeBits/psana/%J.log -q psnehq -n 32 mpirun --mca btl ^openib python fastHD5.py $1

bsub -o /reg/neh/home/sioan/Desktop/referenceCodeBits/psana/%J.log -q psanaq -n 32 mpirun --mca btl ^openib python fastHD5.py $1
