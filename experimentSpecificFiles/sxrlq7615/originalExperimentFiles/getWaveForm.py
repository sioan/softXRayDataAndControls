from pylab import *
import psana
from ImgAlgos.PyAlgos import photons
from scipy.signal import convolve2d

ds = psana.DataSource('exp=sxrlq7615:run=22')	#test data from AMO runs 10, 15, and 19
#ds = psana.DataSource('exp=xpptut15:run=280')	#test data from AMO runs 10, 15, and 19
#ds = psana.DataSource('exp=sxrm2316:run=106') 	#real data from specified experiment (sxrm2316)
psana.DetNames()

aquiris1 = psana.Detector("Acq01")

#det = psana.Detector('pnccdFront')				#for LQ76 and test amo data
#det = psana.Detector('andor')				#for sxrm2316

myEvents = enumerate(ds.events())

evt = next(myEvents)[1]
y,x = aquiris1(evt)

yTotal=0
y2Total = 0
yStack = y

if __name__ == "__main__":
	for nevent,evt in myEvents:
		try:
			if (nevent % 10==1):
				print nevent
			#print nevent

			y,x = aquiris1(evt)
			x=x[0]
			y=y[0]

			plot(x,y)
			#print nevent
			#dummy = input("press any key to proceed")
			cla()		

			yTotal += y
			y2Total += y**2
			toStack = y			
			#toStack = y[12700:14000] - mean(y[0:12700])
			#toStack /= std(toStack)
			yStack = vstack([yStack,toStack])

		except KeyboardInterrupt:
			break
	print("broke out of averaging loop")	
	#select region of response after initial pulse
	#substract off mean	
	#pad on right hand size with zero so it's the same size as the original

