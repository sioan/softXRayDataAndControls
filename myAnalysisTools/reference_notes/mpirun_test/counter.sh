#!/bin/bash
#export LD_LIBRARY_PATH=/reg/neh/home/cpo/junk
echo `hostname`
export PYTHONPATH=""
export LD_LIBRARY_PATH=""
source /reg/g/psdm/etc/psconda.sh

export PATH="/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.52/bin:/reg/g/psdm/sw/conda/manage/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin"


python /reg/neh/home/sioan/softXRayDataAndControls/myAnalysisTools/reference_notes/mpirun_test/counter.py

##############################
####this is command line######
#`which mpirun` --oversubscribe -H daq-amo-mon02,daq-amo-mon03,daq-amo-mon04,daq-amo-mon05,daq-amo-mon06 -n 4 ./counter.sh
#`which mpirun` --oversubscribe -H daq-amo-mon04,daq-amo-mon05,daq-amo-mon06 -n 3 ./counter.sh
#`which mpirun` -n 2 -H daq-amo-mon04,daq-amo-mon05 ./counter.sh

