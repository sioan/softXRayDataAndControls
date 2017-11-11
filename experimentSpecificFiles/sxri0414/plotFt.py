from pylab import *

myDict={}
myDict["run60"] = loadtxt("FTdata/run60ft.dat")
myDict["run63"] = loadtxt("FTdata/run63ft.dat")
myDict["run79"] = loadtxt("FTdata/run79ft.dat")


fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)
ax.set_title('frequency domain')

myCounter = 0 
for i in myDict:
	ax.semilogx(myDict[i][0],myDict[i][1]**2+myDict[i][2]**2+100*myCounter)
	myCounter+=1

ylim(0,300)
ax.legend(myDict.keys(),loc=0)
ax.set_xlabel('frequency(THz)')
ax.set_ylabel('power spectrum')
