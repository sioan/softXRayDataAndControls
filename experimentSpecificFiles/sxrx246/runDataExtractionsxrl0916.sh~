#!/bin/bash

#Priorities

#psnehq
#psnehprioq
#psnehhiprioq

# run batch job
# $1 is run number, $2 is number of events (-1 will iterate through all events)
#bsub -q psnehq -n 32 -a mympi -o ./log/%J.log python extractData_v3.py -c configsxrl0916.cfg -r $1 -n $2
#bsub -q psnehprioq -n 32 -a mympi -o ./log/%J.log python extractData_v5.py -c configsxrl0916.cfg -r $1 -n $2
#bsub -q psnehq -n 32 -o ./log/%J.log mpirun python extractData_v6.py -c configsxrl0916.cfg -r $1 -n $2

bsub -q psnehq -n 32 -o ./log/%J.log mpirun psanaXtcDataExtractor.py -e sxrx24615 -r 21 -c analysis.cfg -t
