myMax = max(array(f['delayStage']))
myMin = min(array(f['delayStage']))
delayScanStep = (myMax - myMin)/100.0

delayScanRange = arange(myMin,myMax,delayScanStep)

mySize = len(f['acqiris2'][myMask])
mySubset = array([f['acqiris2'][myMask],f['GMD'][myMask],f['delayStage'][myMask]])

myMatrix = ones(len(myDict['GMD']))
myMatrix = vstack([myMatrix,myDict['GMD']])
myMatrix = vstack([myMatrix,myDict['GMD']**2])
myMatrix = vstack([myMatrix,myDict['acqiris2']])
myMatrix = vstack([myMatrix,myDict['acqiris2']**2])
myMatrix = vstack([myMatrix,myDict['delayStage']])

myMask = loadtxt("myMask.dat")
myMask = myMask.astype(bool)

myMatrix = myMatrix[:,myMask]


#myMatrix = array([i/dot(i,i) for i in myMatrix])

u,s,v = svd(myMatrix,full_matrices=0)

toExport = dot(diag(s),v).transpose()

savetxt("svd.dat",toExport)
