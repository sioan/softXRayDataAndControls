#!/usr/bin/python -i
import os

myDirectory = "/reg/d/iocData/ioc-sxr-ppl-ims/autosave/"
myFile = "ioc-sxr-ppl-ims.sav_171009-173737"
myPV = "SXR:EXP:MMS:16"

f = open(myDirectory+myFile)

for myLine in f:
	temp = myLine.split(" ")
	if myPV in myLine:
		myString = "caput "+temp[0]+" "+temp[1]
		print myString
