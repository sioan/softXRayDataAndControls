from psana import *
import numpy as np
import matplotlib.pyplot as plt

ds = DataSource('exp=sxr10116:run=37:smd')
itr = ds.events()
acq = Detector('Acq01')
epics = ds.env().epicsStore()
wf = np.zeros(20000)
x = 0

evt = itr.next()
wf = acq.waveform(evt)[0,89100:89600].flatten()
# plt.show()

bins = np.linspace(-.2,.3,100)

xmin = -.2
xmax = .3
print(np.shape(wf))

curve = np.zeros(100)


print(np.shape(bins))
print(np.shape(curve))
n = 0


counts = np.zeros(100)

for nevt,evt in enumerate(ds.events()):
    n += 1

    if n%100 == 0: print(n)
    wf = acq.waveform(evt)[0,89100:89600].flatten()
    sig = np.sum(wf)
    x = epics.value('SXR:RCI:MZM:GRD:x.RBV')
    index = (x-xmin)/(xmax-xmin)*100
    if index < 0: continue
    if index > 99: continue
    curve[index] += sig
    counts[index] += 1

    

curve = curve/counts

plt.plot(bins,curve)
plt.show()
