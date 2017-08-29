from pylab import *

myData = loadtxt("intZall.dat")[:,8:]
#myData = loadtxt("intNall.dat")[5:30,8:280]
#myData = vstack([myData,loadtxt("intPall.dat")[5:30,8:280]])

#myData = loadtxt("intNall.dat")[5:30,8:280] + loadtxt("intPall.dat")[5:30,8:280]

u,s,v = svd(myData)

figure(0)
imshow(myData)

figure(1)
subplot(421)
plot(-v[0],'b-')
subplot(423)
#plot(-3*v[0],'r-')
plot(-v[1],'b-')
subplot(425)
plot(-v[2],'b-')
subplot(427)
plot(-v[3],'b-')


subplot(422)
plot(u[:,0],'bo')

subplot(424)
plot(u[12:,1],'bo')
twinx()
plot(u[12:,0],'ro')

subplot(426)
plot(u[:,2],'bo')
subplot(428)
plot(u[:,3],'bo')

figure(2)
semilogy(s,'bo')

show()
