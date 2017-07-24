from pylab import *
import os

def saveAndTouchKernel(myArray):
	#myArray /= std(myArray)**2
	savetxt("myKernel.txt",myArray)
	os.system("touch myKernel.txt")
