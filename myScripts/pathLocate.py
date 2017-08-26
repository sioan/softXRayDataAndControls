#!/usr/bin/python
import sys
import os
import subprocess

commandString="echo $PATH"
myPaths = subprocess.Popen(commandString,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
myPaths = myPaths.stdout.readlines()
myPaths = myPaths[0][:-1].split(":")

myEnv = subprocess.Popen("env",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
myEnv = myEnv.stdout.readlines()
tempPaths=[]

for i in myPaths:
	if(os.path.isdir(i)):
		tempPaths.append(i)

for i in myEnv:
	
	toTestIfPath = i.split("=")[1][:-1]
	if(os.path.isdir(toTestIfPath)):
		tempPaths.append(toTestIfPath)


myPaths = tempPaths
#print myPaths
#print sys.argv

for i in set(myPaths):
#for i in myPaths:
	print i
	os.system("ls -lh " +i+ " | grep -i "+str(sys.argv[1]))
	myCommandString = "grep -is "+str(sys.argv[1])+" "+i+"/*"
	#print(myCommandString)
	os.system(myCommandString)
