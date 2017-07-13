#template for creating a dict from search results using netconfig
#parsees the results from netconfig search all and puts in in a dict 
#whose keynames are the cname (record in the Domain Name System)
#based on pingAll.py that goes through every
#actual loading of dicts is done by loadNetworkConfigSearchResults


import networkToolsLibrary as nt
import os
import numpy as np
import multiprocessing
import sys
import time

def clear():
	os.system("clear")
	return 

#load the data into 
myDict = nt.loadNetworkConfigSearchResults()

#choose names if they're in amo or sxr
hostNames  = [s for s in myDict.keys() if ("sxr" in s) or ("amo" in s)]

f = open("locationList.txt","w")


locationList = []

for thisKey in hostNames:
	#imyString = line
	#myString = myString.split(".exit")[0]
	#print myString
	locationList.append(myDict[thisKey]["Location"])


def unique(a):
    """ return the list with duplicate elements removed """
    return list(set(a))

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))


for i in unique(locationList):
	if 'same' in i:
		continue
	if 'Same' in i:
		continue
	if 'na' == i:
		continue

	f.write(i)


f.close()
