#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
import os
import sys
import subprocess


f = open('/reg/neh/home5/sioan/softXRayDataAndControls/myScripts/scriptConfigFiles/commonhosts.cfg')

for i in f:
	if ("#" in i):
		continue
	HOST = i[:-1]
	COMMAND="screen -list"
	commandString = "ssh -o ConnectTimeout=4 "+HOST+" "+COMMAND+" &"
	
	#myOutput = subprocess.check_output(myString.split(" "))
	#myOutput = subprocess.check_output(["checkOneScreen.sh"],["psana"])
	#ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	ssh = subprocess.Popen(commandString.split(" "),shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)		
	result = ssh.stdout.readlines()
	if result == []:
		error = ssh.stderr.readlines()
		print >>sys.stderr, "ERROR: %s" % error
	else:
		resultString = HOST+" "+str(result)
		print resultString
