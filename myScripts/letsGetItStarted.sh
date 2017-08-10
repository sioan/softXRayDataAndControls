#!/bin/bash

#add a check if it's already open

#setup gedit screeen
screen -X -S geditScreen quit
screen -d -m -S geditScreen ssh psdev7b
screen -S geditScreen -X stuff 'gedit & \n'
screen -S geditScreen -X stuff 'ssh psusr112 \n'
screen -S geditScreen -X stuff 'cd softXRayDataAndControls/taskManagement \n'
screen -S geditScreen -X stuff 'cd softXRayDataAndControls/taskManagement \n'

#setup google chrome
screen -X -S googleChromeScreen quit
screen -d -m -S googleChromeScreen ssh psdev7b
screen -S googleChromeScreen -X stuff 'ssh psusr112 google-chrome &\n'
screen -S googleChromeScreen -X stuff 'exit \n'

#setup top and iftop on certain screens.  which ones? open ganglia too


#setup the epics ioc and dedm development environment
#gnome-terminal -e epicsDevelopmentEnvironment.sh

#setup psana user analysis code development environment
#gnome-terminal -e psanaUserCodeDevelopmentEnvironment.sh

########################################################################
###############psana cluster trouble shooting ##########################
#setup psana load sharing facility (lsf) trouble shooting environment
#gnome-terminal -e lsfTroubleShooting.sh
#what goes in here?
	#gedit to open psana notes
	#make sure xtc files exists.  open terminals with each of the locations.
		#i.e. ssh to dss nodes and look in /u
	#command references to bhosts, bqueues, top, log files
	#
#contact list and names for chris, clemens, wilko, damiani
########################################################################
########################################################################

########################################################################
###############daq trouble shooting environment ########################
#setup psana load sharing facility (lsf) trouble shooting environment
#gnome-terminal -e daqTroubleShooting.sh
#what goes in here?
#	gedit to open daq notes
#		csh terminal to view results from restarting daq
#		view log files
#		ssh to instruments to make sure they're running. then lsusb,lspci, lsof to see if
#		instrument is present
#contact list and names for jana, damiani, wilko
########################################################################

########################################################################
###############epics trouble shooting environment ########################
#setup psana load sharing facility (lsf) trouble shooting environment
#gnome-terminal -e daqTroubleShooting.sh
#what goes in here? what to bring up?
#	gedit for epics notes
#	bring up ioc manager
#	start sxr home
#	gnome terminals on sxr-console, sxr-control

#contact list and names for stubbs, mike browne
########################################################################
