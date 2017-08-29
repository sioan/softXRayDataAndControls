from pylab import *

#yTotal -= mean(yTotal[:5000])

#kernelStart = 12853
#kernelEnd = -15

#myKernel = append(yTotal[kernelStart:kernelEnd],zeros(kernelStart-kernelEnd))

#plot(yTotal)
#plot(myKernel)

print yTotal.shape
print myKernel.shape

myKernelFFT = fft(myKernel)

myDeconvolution = real(ifft(fft(yTotal)*abs(myKernelFFT)/(abs(myKernelFFT)**2+1e3)))
figure(1)
plot(myDeconvolution)
#plot(yTotal)
