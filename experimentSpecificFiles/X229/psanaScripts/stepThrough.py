#dsource = psana.MPIDataSource('exp=sxrlq2715:run=56')
#myEnumeratedEvents = enumerate(dsource.events())
eventNumber,thisEvent = next(myEnumeratedEvents)
y,x = histogram((pnccdDetectorObject.image(thisEvent)).flatten(),bins=arange(0,750,1))
plot(x[1:],log(1+y))
show()

