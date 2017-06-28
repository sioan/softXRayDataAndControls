import psana
import matplotlib.pyplot as plt
import numpy as np

myDataSource = psana.MPIDataSource("exp=sxrx22915:run=18:smd")	
myEnumeratedEvents = enumerate(myDataSource.events())
imagingDetectorObject = psana.Detector("pnccd")
#det = Detector('cspad')

myLogList = np.array([])

for nEvent,myEvent in myEnumeratedEvents:
	
	try:
		myImage = imagingDetectorObject.image(myEvent)
		if myImage is None: continue
		myLogList = np.append(myLogList,np.sum(myImage[420:560,80:230])/np.sum(myImage[420:560,1030:1185]))
		#if nevent>=2: break
		# includes pedestal subtraction, common-mode correction, bad-pixel
		# suppresion, and uses geometry to position the multiple CSPAD panels
		# into a 2D image

		#if nEvent%10==0: print nEvent
		#print 'Fetching event number',nevent
		#img = det.image(evt)

		#plt.imshow(img,vmin=-2,vmax=2)
		#plt.show()
	except:
		break
y,x  = np.histogram(myLogList,bins=np.arange(0.8,1.2,0.001))
#plt.plot(x[:-1],y)
#plt.show()

#fig, ax = plt.subplots()
#rects1 = ax.bar(x[:-1],y,0.001)
#plt.show()

np.savetxt("forMingFu.txt",np.array([x[:-1],y]))

print 'Done.'
