import os
import re
import subprocess
import time

time.sleep(1)


#workingDirectory = "/home/c1z/Desktop/softXRayDataAndControls/psanaExperimentation"
workingDirectory ="/reg/neh/home/sioan/Desktop/softXRayDataAndControls/psanaExperimentation"


try:
	#reading the list of screens 
	myString = str(subprocess.check_output(["screen","-list"])) # this works on home computer
except subprocess.CalledProcessError as grepexc:
	print "error code", grepexc.returncode, grepexc.output #this modifies homecompueter code for slac
	myString = grepexc.output

#proc = subprocess.Popen(["screen","-list"],stdout = subprocess.PIPE)	#this modifies home computer to work on slac in one line but code below needs munging


#parsing the output
myStringList = myString.split("\t")
listOfScreenNames = [s for s in myStringList if "psanaScreen" in s]

for i in listOfScreenNames:
	
	myString = "screen -S "+i+" -X stuff 'cd "+workingDirectory+"'\r\n"
	os.system(myString)
	#print myString

	myString = "screen -S "+i+" -X stuff 'python -i boringWhile.py'\r\n"
	os.system(myString)
	#print myString
