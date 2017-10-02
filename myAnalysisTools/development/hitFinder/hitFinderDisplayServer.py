import socket
import numpyClientServer
from pylab import *
import Queue
import threading

from psmon.plots import Image,XYPlot
from psmon import publish
import time

basePortNumber = 13000
maxRank = 3

myImageQueue = Queue.Queue()

#this will get hung up if one node fails.
def populateMyImageQueue():
	while(True):
	time.sleep(.05)

	for i in arange(maxRank):
		myData = numpysocket.startServer(basePortNumber+i)
		myImageQueue.put(myData)



populateMyImageQueueThread = threading.Thread(target=populateMyImageQueue)
populateMyImageQueueThread.start()

while not queue.empty():
	#pyqt graph code to show image fast
	plotimg = Image(0,"CsPad", myImageQueue.get())
	publish.send('IMAGE',plotimg)	#line below is used to display image
	#psplot -s <hostname> IMAGE
	
