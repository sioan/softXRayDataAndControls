#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
import Queue
import os
import sys
import subprocess
import threading
import argparse
import socket
import IPython

thisHost = socket.gethostname()

def sendSSHCommandQWrapper(q,commandString):
	q.put(sendSSHCommand(commandString))

def sendSSHCommand(HOST,COMMAND):

	commandString = "ssh -o ConnectTimeout=4 "+HOST+" "+COMMAND+" &"

	mySshSubProcess = subprocess.Popen(commandString.split(" "),shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)		
	myStdOut = mySshSubProcess.stdout
	myStdErr = mySshSubProcess.stderr
	for i in myStdOut:
		print HOST+", "+i,

	for i in myStdErr:
		print HOST+", "+i,
	
	return myStdOut,myStdErr


def main(myCommand):

	f = open('/reg/neh/home5/sioan/softXRayDataAndControls/myScripts/scriptConfigFiles/commonhosts.cfg')
	q = Queue.Queue()
	myDict= {}

	for i in f:
		if ("#" in i):
			continue
		HOST = i[:-1]
		COMMAND=myCommand
		
	

		t = threading.Thread(target=sendSSHCommand,args=([HOST,COMMAND]))
		t.start()
		#temp = sendSSHCommand(commandString)

	#IPython.embed()

if __name__ == '__main__':
	
	print("checking screens")
	myParser = argparse.ArgumentParser(description='checks if screens exist on hosts in config file')
		
	myParser.add_argument('-c command','--command',type=str, help='command to send')
	#myParser.add_argument('-r','--run',type=int,help='the run number to use when running offline')

	myArguments = myParser.parse_args()
	print("arguments parsed")

	main(myArguments.command)


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
