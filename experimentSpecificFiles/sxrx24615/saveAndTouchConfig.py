from pylab import *
import os

def saveAndTouchConfig(myConfig):
	#myConfig = array([[100,-100],[100,-100],[100,-100],[100,-100]])	
	savetxt("myConfig.dat",myConfig)
	os.system("touch myConfig.dat")
