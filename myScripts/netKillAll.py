#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
import Queue
import os
import sys
import subprocess
import threading
import argparse

def sendSSHCommandQWrapper(q,commandString):
	q.put(sendSSHCommand(commandString))

def sendSSHCommand(commandString):
	ssh = subprocess.Popen(commandString.split(" "),shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)		
	result = ssh.stdout.readlines()
	error = ssh.stderr.readlines()
	if ([]==result):
		#for i in error:
		print >>sys.stderr, "ERROR: %s" % error
	else:
		if ("There is" in str(result)):
		#if(True):
			resultString = commandString+" "+str(result)
			print resultString
		#else:
			#print("no screen")
	return 1

def main(kill,run):

	f = open('/reg/neh/home5/sioan/softXRayDataAndControls/myScripts/scriptConfigFiles/commonhosts.cfg')
	q = Queue.Queue()
	if(kill):
		screenCommand = "killall -v screen"
	else:
		screenCommand = "screen -list"

	for i in f:
		if ("#" in i):
			continue
		HOST = i[:-1]
		COMMAND=screenCommand
		commandString = "ssh -o ConnectTimeout=4 "+HOST+" "+COMMAND+" &"
	
		#myOutput = subprocess.check_output(myString.split(" "))
		#myOutput = subprocess.check_output(["checkOneScreen.sh"],["psana"])
		#ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		#sendSSHCommand(commandString)
		#t = threading.Thread(target=sendSSHCommandQWrapper,args=([q,commandString]))
		t = threading.Thread(target=sendSSHCommand,args=([commandString]))
		t.start()


if __name__ == '__main__':
	
	print("checking screens")
	myParser = argparse.ArgumentParser(description='checks if screens exist on hosts in config file')
		
	myParser.add_argument('-k','--kill',action='store_true', help='kills the host too')
	myParser.add_argument('-r','--run',type=int,help='the run number to use when running offline')

	myArguments = myParser.parse_args()
	print("arguments parsed")

	main(myArguments.kill,
		myArguments.run)


"""
import Queue
import threading
import urllib2

# called by each thread
def get_url(q, url):
    q.put(urllib2.urlopen(url).read())

theurls = ["http://google.com", "http://yahoo.com"]

q = Queue.Queue()

for u in theurls:
    t = threading.Thread(target=get_url, args = (q,u))
    t.daemon = True
    t.start()

s = q.get()
print s"""
