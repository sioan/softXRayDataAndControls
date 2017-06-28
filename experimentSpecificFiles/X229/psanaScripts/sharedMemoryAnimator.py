import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import psana
import time

ds = psana.DataSource('exp=sxrlq7615:run=22')
myEvents = enumerate(ds.events())


aquiris1 = psana.Detector("Acq01")


fig = plt.figure()
ax = plt.axes(xlim=(0, 2e-6), ylim=(-0.1, 0.1))
line, = ax.plot([], [], lw='0',marker='.')

# initialization function: plot the background of each frame
def init():
	line.set_data([], [])
	return line,

# animation function.  This is called sequentially
def animate(i):
	global myEvents
	nevent,evt = next(myEvents)
	y,x = aquiris1(evt)

	line.set_data(x[0], y[0])
	return line,

anim = animation.FuncAnimation(fig, animate, init_func=init,frames=20, interval=20, blit=True)

plt.show()
