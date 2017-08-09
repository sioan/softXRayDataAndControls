#!/bin/bash

#setup google chrome
screen -d -m -S googleChromeScreen ssh psdev7b
screen -S googleChromeScreen -X stuff 'gedit \n'
screen -S googleChromeScreen -X stuff 'ssh psusr112 \n'
screen -S googleChromeScreen -X stuff 'google-chrome \n'

#setup top and iftop on certain screens
