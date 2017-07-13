from pyEpics import *
from pylab import *
import time

myData = [0,0,0,0,0,0,0]


for i in arange(360*3):
	time.sleep(1.0/360)
	myData = vstack([myData,])
	
