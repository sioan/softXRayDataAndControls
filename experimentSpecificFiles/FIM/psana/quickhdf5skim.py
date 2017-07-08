import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import h5py

f = h5py.File("run104b.h5")

pulseArea = nan_to_num(list(f['pulseArea']))
referenceRoiIntensity = nan_to_num(list(f['referenceRoiIntensity']))
"""
subplot(221)
plot(nan_to_num(referenceRoiIntensity),'.')
xlim(2000,6000)

subplot(222)
plot(nan_to_num(pulseArea),'.')
xlim(2000,6000)

show()
"""


fig, ax1 = plt.subplots()
t = np.arange(0.01, 10.0, 0.01)
s1 = np.exp(t)
#ax1.plot(t, s1, 'b-')
ax1.plot(pulseArea, 'b.')
ax1.set_xlabel('event number')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('waveform', color='b')
ax1.tick_params('y', colors='b')

ax2 = ax1.twinx()
s2 = np.sin(2 * np.pi * t)
#ax2.plot(t, s2, 'r.')
ax2.plot(referenceRoiIntensity, 'r.')
ax2.set_ylabel('pnccd roi', color='r')
ax2.tick_params('y', colors='r')

fig.tight_layout()
plt.show()
