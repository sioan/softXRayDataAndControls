import numpy as np
from pylab import *
from matplotlib import pyplot as plt
from matplotlib import animation
import os

execfile('/reg/neh/home5/sioan/Desktop/upComingExperiments/LQ76/numpyClientServer.py')
onePulseRun20 = np.loadtxt("singlePulseRun20.txt")
twoPulseRun21 = np.loadtxt("twoPulseRun21.txt")
twoPulseRun22 = np.loadtxt("twoPulseRun22.txt")

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(0, 6000), ylim=(-0.1, 0.1))
line, = ax.plot([], [], lw=2)


#fig, (ax1, ax2) = plt.subplots(2,1)
#line1, = ax1.plot([], [], lw=2)
#line2, = ax2.plot([], [], lw=2, color='r')
#line = [line1, line2]

kernelLastModTime = os.path.getatime("myKernel.txt")
myKernel = np.loadtxt("myKernel.txt")
#y = -onePulseRun20[0]
y = -twoPulseRun21[0]

# initialization function: plot the background of each frame
def init():
    line.set_data([], [])
    #line[1].set_data([], [])
    return line,

# animation function.  This is called sequentially
def animate(i):
    global kernelLastModTime
    global myKernel
    global y
    #x = np.linspace(0, 2, 1000)
    #y = np.sin(2 * np.pi * (x - 0.01 * i))
    
    #y = epics.caget("SXR:NOTE:ARRAY:01")
    if(kernelLastModTime != os.path.getatime("myKernel.txt")):
        myKernel = np.loadtxt("myKernel.txt")
        os.system("touch myKernel.txt")
        kernelLastModTime = os.path.getatime("myKernel.txt")
        print "new kernel"

    #y = 0.975*y+-0.025*convolve(myKernel,onePulseRun20[i])[0:y.shape[0]]
    y = 0.975*y+-0.025*convolve(myKernel,twoPulseRun22[i])[0:y.shape[0]]

    x = np.arange(y.shape[0])
    line.set_data(x, y)
    #line.set_data(x, -twoPulseRun21[i])
    #print myKernel
    ax.set_ylim(1.1*min(y),1.1*max(y))
    
    return line,

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=200, interval=40, blit=True)


plt.show()

