#steps for generating filter
from pylab import *

onePulseRun20 = np.loadtxt("singlePulseRun20.txt")
twoPulseRun21 = np.loadtxt("twoPulseRun21.txt")
twoPulseRun22 = np.loadtxt("twoPulseRun22.txt")

y = mean(onePulseRun20,axis=0)

#y is averaged one pulse data
myFilter = conjugate(fft(y))/(abs(fft(y))**2+.3)
myKernel = real(ifft(myFilter))[4500:5500]
myRecon = convolve(myKernel,onePulseRun20[1])

x = arange(200)
broadeningImpulse = 1/((x*1.0-100)**2+400.0)
myBroadening = conjugate(fft(broadeningImpulse))/(abs(fft(broadeningImpulse))**2+.0000003)
myDeBroadeningKernel = convolve(real(ifft(myBroadening)),[1,1,1,1])
