import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import psana
import time
ds = psana.DataSource("exp=sxrx22915:run=18")				#using file comment out as necessary.

#psana.setOption('psana.calib-dir','/reg//d/psdm/sxr/sxrx22915/calib')	#using shared memory
#ds = psana.DataSource("shmem=psana.0:stop=no")				#using shared memory


myEnumeratedEvents = enumerate(ds.events())

#myBackGroundImage = 0

#imagingDetectorObject = psana.Detector("EXS_OPAL")
imagingDetectorObject = psana.Detector("pnccd")
#waveFormDetectorObject = psana.Detector("Acq01")

nEvent, myEvent = next(myEnumeratedEvents)
myImage = imagingDetectorObject.image(myEvent)

Intensity_ROI1 = np.zeros(100)
Intensity_ROI2= np.zeros(100)

fig = plt.figure()

def f(x, y):
	return np.sin(x) + np.cos(y)

x = np.linspace(0, 2 * np.pi, 120)
y = np.linspace(0, 2 * np.pi, 100).reshape(-1, 1)
z = np.zeros([1000,2])

#im = plt.imshow(f(x, y), animated=True,clim=(-500,1400))

Intensity_ROI1 = np.zeros(100)
Intensity_ROI2= np.zeros(100)
Intensity_ROI1[9] = 20e6
Intensity_ROI1[9] = 20e6

nEvent, myEvent = next(myEnumeratedEvents)
myImage = imagingDetectorObject.image(myEvent)
myHistogram = np.histogram2d(Intensity_ROI1,Intensity_ROI2,bins = (np.arange(0,20e6,20e4),np.arange(0,20e6,20e4)))

#im = plt.imshow(myImage, animated=True,clim=(-500,1400))
im = plt.imshow(myHistogram[0], animated=True,clim=(0,10))

def updatefig(*args):
	global myEnumeratedEvents,myBackGroundImage, myImage,myHistogram
	global x, y, z,Intensity_ROI1,Intensity_ROI2
	

	nEvent, myEvent = next(myEnumeratedEvents)
	#if nEvent%10==0:
		#print nEvent

	myImage = imagingDetectorObject.image(myEvent)

	if myImage is None: return np.random.rand()

	#myImage = imagingDetectorObject.raw(myEvent)
	#myImage = np.hstack([np.vstack([myImage[0],myImage[1][::-1,::-1]]),np.vstack([myImage[3],myImage[2][::-1,::-1]])])
	#myBackGroundImage = myBackGroundImage +	myImage

	Intensity_ROI1 = np.append(Intensity_ROI1,np.sum(myImage[420:560,80:230]))[-10000:]
	Intensity_ROI2 = np.append(Intensity_ROI2,np.sum(myImage[420:560,1030:1185]))[-10000:]

	myHistogram = np.histogram2d(Intensity_ROI1,Intensity_ROI2,bins = (np.arange(0,20e6,20e4),np.arange(0,20e6,20e4)))

	#x += np.pi / 15.
	#y += np.pi / 20.

	#myArray = np.vstack([myArray,np.sum(myImage,axis=0)])

	#im.set_array(f(x, y))
	#im.set_array(myImage)
	im.set_array(myHistogram[0][::-1,::1])
	im.set_clim(0,max((myHistogram[0].flatten())[10:]))
	return im,

ani = animation.FuncAnimation(fig, updatefig, interval=10, blit=True)
plt.show()
