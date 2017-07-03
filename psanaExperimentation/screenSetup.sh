#!/bin/bash
#runs on psdev7a
#screen -X -S psanaScreen quit


screen -d -m -S psanaScreen
screen -S psanaScreen -X stuff 'cd /reg/neh/home/sioan/Desktop/softXRayDataAndControls/psanaExperimentation \n'
#screen -S psanaScreen -X stuff 'python -i boringWhile.py \n'		#for testing screenSetup.py comment out.
