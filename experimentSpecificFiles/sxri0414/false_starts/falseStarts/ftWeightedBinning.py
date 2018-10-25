#code after plotPackage.py to examine fourier properties.
#less lines of code
#arithmetic mean, not geometric shows better smoothed data, but less convincing un smoothed data.  Fourier transform look ok.
#still can't construct meaningful wiener filter. comes out crappy
#data may look better the polynomial I vs I0 fitting

plot(x[:150],ySmoothed[0][:150])
show()
plot(abs(fft(y[:150]))**2)
show()
min(x[:150])
diff9x)
diff(x)
plot(arange(0,10,10.0/150),abs(fft(y[:150]))**2)
show()
plot(y)
show()
from scipy.linalg import dft
dft
dft(10)
dft(10).shape
plot(arange(0,10,10.0/150),abs(dot(dft(150),y[:150]))**2)
show()
xMat = dot(dft(150),diag(yErrorBars))
y.Shape
y
len(y)
clear
xMat = dot(dft(150),diag(yErrorBars[:150]))
beta = dot(dot(inv(dot(xMat.transpose(),xMat)),xMat.transpose()),dot(diag(yErrorBars[:150]),y[:150]))
plot(arange(0,10,10.0/150),abs(beta)**2)
plot(arange(0,10,10.0/150),abs(beta)**2)
plot(x[:150],real(ifft(beta)))

