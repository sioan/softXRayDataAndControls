import os
import re
import subprocess
import time

time.sleep(1)

workingDirectory = "/home/c1z/Desktop/softXRayDataAndControls/psanaExperimentation"

#reading the list of screens 
myString = str(subprocess.check_output(["screen","-list"]))

#parsing the output
myStringList = myString.split("\\t")
listOfScreenNames = [s for s in myStringList if "myScreen" in s]

for i in listOfScreenNames:
	
	myString = "screen -S "+i+" -X stuff 'cd "+workingDirectory+"'\r\n"
	os.system(myString)

	myString = "screen -S "+i+" -X stuff 'python -i boringWhile.py'\r\n"
	os.system(myString)
