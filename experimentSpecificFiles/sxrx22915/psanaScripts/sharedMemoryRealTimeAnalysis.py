import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import psana
import time
from scipy.odr import *
ds = psana.DataSource("exp=sxrx22915:run=18")				#using file comment out as necessary.

#psana.setOption('psana.calib-dir','/reg//d/psdm/sxr/sxrx22915/calib')	#using shared memory
#ds = psana.DataSource("shmem=psana.0:stop=no")				#using shared memory


myEnumeratedEvents = enumerate(ds.events())

#myBackGroundImage = 0

#imagingDetectorObject = psana.Detector("EXS_OPAL")
imagingDetectorObject = psana.Detector("pnccd")
#waveFormDetectorObject = psana.Detector("Acq01")

myAverageImage = 0
Intensity_ROI1 = np.zeros(100)
Intensity_ROI2 = np.zeros(100)

#im = plt.imshow(np.zeros([5,5]), animated=True,clim=(-500,1400))

def data_gen():
    t = data_gen.t
    cnt = 0
    while cnt < 1000:
        cnt+=1
        t += 0.05
        y1 = np.sin(2*np.pi*t) * np.exp(-t/10.)
        y2 = np.cos(2*np.pi*t) * np.exp(-t/10.)
        # adapted the data generator to yield both sin and cos
        yield t, y1, y2

data_gen.t = 0

# create a figure with two subplots
#fig, (ax1, ax2) = plt.subplots(1,2)
fig, ((ax1, ax2),(ax3,ax4)) = plt.subplots(2,2)

# intialize two line objects (one in each axes)
line1, = ax1.plot([], [], lw=0,marker='o')
#line2, = ax2.plot([], [], lw=2, color='r')
line2 = ax2.imshow(np.zeros([1273,1027]), animated=True,clim=(-500,1400))
line3, = ax3.plot([], [], lw=0,marker='o')
line4, = ax4.plot([], [], lw=0,marker='o')
line = [line1, line2,line3,line4]

#the same axes initalizations as before (just now we do it for both of them)
ax1.set_xlim(0, 1e7)
ax1.set_ylim(0,1e7)
ax1.set_xlabel("I ROI1")
ax1.set_ylabel("I ROI2")
ax2.set_xlim(0, 1027)
ax2.set_ylim(0,1273)
ax3.set_xlim(-1, 101)
ax3.set_ylim(7.2e-4,8e-4)
ax3.set_xlabel("events")
ax3.set_ylabel("standDev I1/I2 slope")


#for ax in [ax1, ax2]:
#	ax.set_ylim(-1.1, 1.1)
#	ax.set_xlim(0, 5)
#	ax.grid()

# initialize the data arrays 

def linearModel(B,x):
	return B[0]*x + B[1]
linear = Model(linearModel)

myBetaSTD = np.array([0])
myResiduals = np.array([0,0])

xdata, y1data, y2data = [], [], []
def run(data):
	global Intensity_ROI1,Intensity_ROI2,myAverageImage,myBetaSTD,myResiduals
	nEvent, myEvent = next(myEnumeratedEvents)
	numberOfEventsInAnalysis = 100	
	#if nEvent%10==0:
		#print nEvent

	myImage = imagingDetectorObject.image(myEvent)
	
	myAverageImage=0.7*myAverageImage+0.3*myImage

	if myImage is None: return np.random.rand()

	#myImage = imagingDetectorObject.raw(myEvent)
	#myImage = np.hstack([np.vstack([myImage[0],myImage[1][::-1,::-1]]),np.vstack([myImage[3],myImage[2][::-1,::-1]])])
	#myBackGroundImage = myBackGroundImage +	myImage

	Intensity_ROI1 = np.append(Intensity_ROI1,np.sum(myImage[420:560,80:230]))[-numberOfEventsInAnalysis:]
	Intensity_ROI2 = np.append(Intensity_ROI2,np.sum(myImage[420:560,1030:1185]))[-numberOfEventsInAnalysis:]

	dataForODR = RealData(Intensity_ROI1,Intensity_ROI2)
	myODR = ODR(dataForODR, linear, beta0=[1., 2.])
	myOdrOutput=myODR.run()

	myBetaSTD = np.append(myBetaSTD,myOdrOutput.sd_beta[0])[-100:]

	#x = (Intensity_ROI1[-1]+Intensity_ROI2[-1]-myOdrOutput.beta[0])/(1+myOdrOutput.beta[1])
	#y = linearModel(myOdrOutput.beta,x)
	#print str(x)+" test "+str(y)

	#myResiduals = vstack([myResiduals,[x-Intensity_ROI1[-1],y-Intensity_ROI2[-1]]])

	# update the data
	t, y1, y2 = data
	xdata.append(t)
	y1data.append(y1)
	y2data.append(y2)

	# axis limits checking. Same as before, just for both axes
	#for ax in [ax1,ax3,ax4]:
	#	xmin, xmax = ax.get_xlim()
	#	if t >= xmax:
	#		ax.set_xlim(xmin, 2*xmax)
	#		ax.figure.canvas.draw()
	
	myMax = np.max(myBetaSTD)
	myMin= np.min(myBetaSTD)
	ax3.set_ylim(0.95*myMin,1.05*myMax)


	# update the data of both line objects
	
	#line[0].set_data(xdata, y1data)
	line[0].set_data(Intensity_ROI1, Intensity_ROI2)
	#line[1].set_data(xdata, y2data)
	line[1].set_array(myAverageImage)
	#line[2].set_data(t,y1)
	line[2].set_data(np.arange(myBetaSTD.shape[0]), myBetaSTD)
	return line

ani = animation.FuncAnimation(fig, run, data_gen, blit=True, interval=50,repeat=False)
plt.show()
