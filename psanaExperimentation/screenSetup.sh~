#!/bin/bash
#runs on psana machine (why was psdev7a here?) command to use is line below
#bsub -o %J.log -q psanaq -n 1 mpirun --mca btl ^openib ./screenSetup.sh $1

#this command kills existing screen.  doesn't work with MPI cluster stuff, only with previous shared memory stuff.
#screen -X -S psanaScreen quit


screen -d -m -S psanaScreen
#screen -S psanaScreen -X stuff 'cd /reg/neh/home/sioan/Desktop/softXRayDataAndControls/psanaExperimentation \n'
#screen -S psanaScreen -X stuff 'python -i boringWhile.py \n'		#for testing screenSetup.py comment out.

#to run interactively 
#ipython -i ../../myAnalysisTools/psanaXtcDataExtractor.py -- -e sxri0414 -r 79 -td TSS_OPAL -tc 162 -f 150 -s 4 -t

#to run on batch nodes
#bsub -o %J.log -q psnehprioq -n 48 mpirun --mca btl ^openib psanaXtcDataExtractor.py -e sxri0414 -r 60 -td TSS_OPAL -tc 162

#mpi for specified hosts
#mpirun -n 40 --host daq-amo-mon02,daq-amo-mon03,daq-amo-mon04,daq-amo-mon05,daq-amo-mon06 amon0816.sh

bsub -o %J.log -q psnehprioq -n 4 mpirun --mca btl ^openib --host psana1502 screen -d -m -S myPsanaScreen interactiveXtcExtractor.sh -e sxri0414 -r 63 -f 10000 -s 4

bsub -o %J.log -q psnehprioq -n 4 mpirun --mca btl ^openib --host psana1502 screen -d -m -S myPsanaScreen interactiveXtcExtractor.sh -e sxri0414 -r 63 -f 10000 -s 4

bsub -o %J.log -q psnehprioq -n 4 -m psana1502 mpirun --mca btl ^openib screen -d -m -S myPsanaScreen interactiveXtcExtractor.sh -e sxri0414 -r 63 -f 10000 -s 4
#this doesn't work
