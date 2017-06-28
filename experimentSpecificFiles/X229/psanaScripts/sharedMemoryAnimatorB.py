import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import psana
import time
ds = psana.DataSource("shmem=psana.0:stop=no")
#ds = psana.DataSource('exp=sxrlq7615:run=22')
myEvents = enumerate(ds.events())

#nevent,evt = next(myEvents)
#psana.DetNames()

aquiris1 = psana.Detector("Acq01")


# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
#ax = plt.axes(xlim=(0, 500*.125), ylim=(-1, 2.5))
ax = plt.axes(xlim=(-1000, 6000))
line, = ax.plot([], [], lw=2)

# initialization function: plot the background of each frame
def init():
	line.set_data([], [])
	return line,

# animation function.  This is called sequentially
def animate(i):
	global myEvents
	evt = next(myEvents)[1]
	y,x = aquiris1(evt)
	
	x = np.arange(y.shape[1])
	#x = np.linspace(0, 2, 1000)
	#y = np.sin(2 * np.pi * (x - 0.01 * i))

	#y = epics.caget("SXR:NOTE:ARRAY:01")
		
	#x = np.arange(y.shape[0])*.125
	#line.set_data(x, -y/abs(np.mean(y[70:90])))
	line.set_data(x,y[3])
   	return line,

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,frames=20, interval=20, blit=True)

plt.show()
