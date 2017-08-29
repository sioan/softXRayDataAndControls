import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import psana
import time
ds = psana.DataSource("shmem=psana.0:stop=no")
myEnumeratedEvents = enumerate(ds.events())


exsOpalDetectorObject = psana.Detector("EXS_OPAL")

fig = plt.figure()


def f(x, y):
	return np.sin(x) + np.cos(y)

x = np.linspace(0, 2 * np.pi, 120)
y = np.linspace(0, 2 * np.pi, 100).reshape(-1, 1)
z = np.zeros([1000,2])

im = plt.imshow(f(x, y), animated=True,clim=(0,72))


def updatefig(*args):
	global myEnumeratedEvents
	global x, y, z
	
	nEvent, myEvent = next(myEnumeratedEvents)

	myEXSOpalImage = exsOpalDetectorObject.raw(myEvent)
	
	x += np.pi / 15.
	y += np.pi / 20.



	#im.set_array(f(x, y))
	im.set_array(myEXSOpalImage)	
	return im,

ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()
