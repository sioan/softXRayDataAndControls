import networkToolsLibrary as nt
import os
import multiprocessing
import sys
import time

def clear():
	os.system("clear")
	return 

myDict = nt.loadNetworkConfigSearchResults()

hostNames  = [s for s in myDict.keys() if ("sxr" in s) or ("amo" in s)]

def check_ping(hostname):
    response = os.system("ping -c 1 " + hostname + "> /dev/null")
    # and then check the response...
    if response == 0:
       return 1
    else:
        sys.exit()

    return


def checkResponse(hostname):
	#global x
	pingStatus = check_ping(hostname)
	#x.append(hostname+", "+check_ping(hostname))
	return pingStatus

jobs=[]
for i in hostNames:
	p = multiprocessing.Process(name=i,target=check_ping,args=(i,))
	jobs.append(p)
	p.start()
	#print '%s.exitcode = %s' % (j.name, j.exitcode)

time.sleep(2)

for j in jobs:
	j.terminate()


def printJobStatus(jobs):
	myFile = open("pingResults.txt",'w')
	for j in jobs:
		print '%s.exitcode = %s' % (j.name, j.exitcode)
		myFile.write("%s.exitcode = %s \n" %(j.name, j.exitcode))
	myFile.close()

printJobStatus(jobs)
