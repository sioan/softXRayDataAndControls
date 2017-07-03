#!/bin/bash
#runs on psana machine (why was psdev7a here?) command to use is line below
#bsub -o %J.log -q psanaq -n 1 mpirun --mca btl ^openib ./screenSetup.sh $1

#this command kills existing screen.  doesn't work with MPI cluster stuff, only with previous shared memory stuff.
#screen -X -S psanaScreen quit


screen -d -m -S psanaScreen
#screen -S psanaScreen -X stuff 'cd /reg/neh/home/sioan/Desktop/softXRayDataAndControls/psanaExperimentation \n'
#screen -S psanaScreen -X stuff 'python -i boringWhile.py \n'		#for testing screenSetup.py comment out.
