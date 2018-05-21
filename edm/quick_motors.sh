#!/bin/bash
cd /reg/g/pcds/package/epics/3.14/screens/edm/ims/
edm -x -eolc -m "TITLE=quick_motors,TYPE=ims,M1=SXR:EXP:MMS:01,M2=SXR:EXP:MMS:07,M3=SXR:EXP:MMS:29" /reg/g/pcds/package/epics/3.14/screens/edm/ims/motion-3axis.edl
cd ~/scripts
