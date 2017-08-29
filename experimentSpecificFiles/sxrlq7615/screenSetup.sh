#!/bin/bash
#runs on psdev7a
screen -X -S monNodeShMem quit
screen -X -S sxrConsoleClient quit
screen -X -S twoPulseFitter quit
screen -X -S pyIOC quit

screen -d -m -S sxrConsoleClient ssh sxr-console
screen -S sxrConsoleClient -X stuff 'cd /reg/neh/home5/sioan/Desktop/upComingExperiments/LQ76 \n'
screen -S sxrConsoleClient -X stuff './runOnSXR.sh \n'

screen -d -m -S monNodeShMem ssh daq-sxr-mon06
screen -S monNodeShMem -X stuff 'cd /reg/neh/home5/sioan/Desktop/upComingExperiments/LQ76 \n'
screen -S monNodeShMem -X stuff './runOnMonNode.sh \n'

screen -d -m -S pyIOC ssh sxr-console
screen -S pyIOC -X stuff 'cd /reg/neh/home5/sioan/Desktop/upComingExperiments/LQ76 \n'
screen -S pyIOC -X stuff 'source pcaspyPathSetup.sh \n'
screen -S pyIOC -X stuff 'python pcaspyTwoPulseCalculations.py \n'

screen -d -m -S twoPulseFitter ssh sxr-console
screen -S twoPulseFitter -X stuff 'cd /reg/neh/home5/sioan/Desktop/upComingExperiments/LQ76 \n'
screen -S twoPulseFitter -X stuff 'source /reg/g/psdm/bin/conda_setup \n'
screen -S twoPulseFitter -X stuff 'PYTHONPATH="$PYTHONPATH:/reg/neh/home/sioan/Desktop/pyepics-3.2.5" \n'
screen -S twoPulseFitter -X stuff 'python twoPulseFittingCA.py \n'

