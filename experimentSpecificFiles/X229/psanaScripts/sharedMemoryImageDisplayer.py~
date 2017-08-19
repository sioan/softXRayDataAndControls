import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import psana
import time
#ds = psana.DataSource("exp=sxrx22915:run=18")				#using file comment out as necessary.

psana.setOption('psana.calib-dir','/reg//d/psdm/sxr/sxrx22915/calib')	#using shared memory
ds = psana.DataSource("shmem=psana.0:stop=no")				#using shared memory


myEnumeratedEvents = enumerate(ds.events())

#myBackGroundImage = 0

#imagingDetectorObject = psana.Detector("EXS_OPAL")
imagingDetectorObject = psana.Detector("pnccd")
#waveFormDetectorObject = psana.Detector("Acq01")

fig = plt.figure()
myArray = np.zeros(1024)

def f(x, y):
	return np.sin(x) + np.cos(y)

x = np.linspace(0, 2 * np.pi, 120)
y = np.linspace(0, 2 * np.pi, 100).reshape(-1, 1)
z = np.zeros([1000,2])

im = plt.imshow(f(x, y), animated=True,clim=(-500,1400))


nEvent, myEvent = next(myEnumeratedEvents)
myImage = imagingDetectorObject.image(myEvent)

def updatefig(*args):
	global myEnumeratedEvents,myBackGroundImage,myArray,myImage
	global x, y, z
	
	nEvent, myEvent = next(myEnumeratedEvents)
	#if nEvent%10==0:
		#print nEvent

	myImage = imagingDetectorObject.image(myEvent)
	#myImage = imagingDetectorObject.raw(myEvent)
	#myImage = np.hstack([np.vstack([myImage[0],myImage[1][::-1,::-1]]),np.vstack([myImage[3],myImage[2][::-1,::-1]])])
	#myBackGroundImage = myBackGroundImage +	myImage

	
	#x += np.pi / 15.
	#y += np.pi / 20.

	#myArray = np.vstack([myArray,np.sum(myImage,axis=0)])

	#im.set_array(f(x, y))
	im.set_array(myImage)	
	return im,

ani = animation.FuncAnimation(fig, updatefig, interval=10, blit=True)
plt.show()
