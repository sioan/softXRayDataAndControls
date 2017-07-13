#template for creating a dict from search results using netconfig
#parsees the results from netconfig search all and puts in in a dict 
#whose keynames are the cname (record in the Domain Name System)
#based on pingAll.py that goes through every
#actual loading of dicts is done by loadNetworkConfigSearchResults


import networkToolsLibrary as nt
import os
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


