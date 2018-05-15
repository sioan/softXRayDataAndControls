import numpy

class BuildFrame(object):
    def __init__(self, lib, noise, cols, rows, photonDist, aduPerPhoton=120/2200., gain=None, gainScale=0.1):
        self.libData = numpy.load(lib)
        self.nClustersInLib = len(self.libData)
        self.counter = 0
        self.noiseData = numpy.load(noise) + 0.001 ## random gets unhappy if 0
        if self.noiseData.shape != (rows, cols):
            print self.noiseData.shape, rows, cols
            raise
        self.rows = rows
        self.cols = cols
        self.__makeCumulativePhotonDist(photonDist)
        self.aduPerPhoton = aduPerPhoton
        self.gain=None
        if gain is not None:
            self.gain = (numpy.load(gain)-1.)*gainScale + 1.

    def __makeCumulativePhotonDist(self, photonDist):
        if abs(photonDist.sum()-1)>0.001:
            print photonDist.sum(), 1.
            raise
        self.__lenPhotonDist = len(photonDist)
        self.__cumulativePhotonDist = numpy.cumsum(photonDist)

    def getNphotons(self):
        r = numpy.random.uniform()
        for i in range(self.__lenPhotonDist):
            if r>self.__cumulativePhotonDist[i]:
                continue
            return i
        ## shouldn't happen, but:
        return self.__lenPhotonDist-1

    def __getCluster(self):
        self.counter += 1
        return self.libData[(self.counter-1)%self.nClustersInLib][2:].reshape((5,5))

    def makeFrame(self):
        self.frame = numpy.zeros((self.rows, self.cols))

    def addNoise(self):
        for col in range(self.cols):
            for row in range(self.rows):
                self.frame[row][col] += numpy.random.normal(0., self.noiseData[row][col])
    
    def addPhotons(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.addPhotonsToPixel(col, row)

    def addPhotonsToPixel(self, col, row):
        n = self.getNphotons()
##              if col==17 and row==17:
##                  n = 1
        for i in range(n):
            cluster = self.__getCluster()
            for j in range(5):
                colOffset = col-2+j
                for k in range(5):
                    rowOffset = row-2+k
                    try:
                        self.frame[rowOffset][colOffset] += cluster[k][j]*self.aduPerPhoton
                    except:
                        pass ## fell off edge of array
                            
    def smearGain(self):
        self.frame *= self.gain

if __name__ == "__main__":
    lib = "toyClusterLibrary_50_20_10000.npy"
    noise = "/reg/neh/home1/philiph/psana/xcsi0115/r90_step_0_rowCm_noise.npy"
    rows = 352
    cols = 384
    photonDist = numpy.array([0.95, 0.042, 0.005, 0.0025, 0.0005])
    bf = BuildFrame(lib, noise, cols, rows, photonDist)
    nFrames = 10
    for i in range(nFrames):
        bf.makeFrame()
        bf.addNoise()
        bf.addPhotons()
        print bf.frame[15:20, 15:20]
