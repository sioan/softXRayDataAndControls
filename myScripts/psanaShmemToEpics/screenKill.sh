#!/bin/bash
#runs on psdev7a
screen -X -S monNodeShMem quit
screen -X -S sxrConsoleClient quit
screen -X -S pyIOC quit
screen -X -S twoPulseFitter quit


#screen -d -m -S sxrConsoleClient ssh sxr-console
#screen -S sxrConsoleClient -X stuff 'cd /reg/neh/home5/sioan/Desktop/upComingExperiments/LQ76 \n'
#screen -S sxrConsoleClient -X stuff './runOnSXR.sh \n'

#screen -d -m -S monNodeShMem ssh daq-sxr-mon06
#screen -S monNodeShMem -X stuff 'cd /reg/neh/home5/sioan/Desktop/upComingExperiments/LQ76 \n'
#screen -S monNodeShMem -X stuff './runOnMonNode.sh \n'
