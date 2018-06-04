import numpy

############################################
###assumes 5x5 array from a larger image
###monte carlo simulation of how a segment of an area detector responds to a  deposited charge at position x and y.
###some number of frames of photon hitting an area detector.
###(very useful for identifying one, two, three, etc... number of photons events such as in the case of speckle.)
###(can also be used to separate out elastic from inelastic photon. (histogramming of ADU)
###(doesn't model the photon-silcon. Instead carries out toy monte carlo by sampling from empircal charge cloud density under the assumption it's a gaussian.
############################################



class BuildToyCluster(object):
    def __init__(self, label, pixelSize, fullWidthHalfMax, nSamples, x=None, y=None):
        self.__headerWords = 2
        self.__clusterSide = 5
        self.__centralOffset = int(self.__clusterSide/2)
        print "cluster is %d by %d, put photons in pixel %d %d" %(self.__clusterSide, self.__clusterSide, self.__centralOffset, self.__centralOffset)
        self.pixelSize = pixelSize
        self.cloudWidth = fullWidthHalfMax/2.355		#FWHM is the spatial extent of the charge depostion
        self.nSamples = nSamples				#number of electrons in the cloud or number of frames
        
        self.label = label+"_%d_%d_%d" %(self.pixelSize, fullWidthHalfMax, self.nSamples)
        self.x = x				#are the position of the photon with sub pixel resolution
        self.y = y				#are the position of the photon with sub pixel resolution
        if x is not None:
            self.label += "_x%d" %(x)
            self.x = x/100. ##convert percent of pixel unit to pixel unit
            if self.x>1 or self.x<0:
                print "x point %0.2f not allowed: range 0-100" %(x)
                raise RuntimeError
        if y is not None:
            self.label += "_y%d" %(y)
            self.y = y/100. ##convert percent of pixel unit to pixel unit
            if self.y>1 or self.y<0:
                print "y point %0.2f not allowed: range 0-100" %(x)
                raise RuntimeError
            
    def buildCluster(self):
        x = self.x
        y = self.y
        if x is None:
            x = numpy.random.uniform()
        if y is None:
            y = numpy.random.uniform()
        return self.buildClusterAtXY(x, y)

    def buildClusterAtXY(self, x, y):
        data = self.__buildCluster(x, y)
        return numpy.append(numpy.array([x, y]), data.flatten())

    def __buildCluster(self, x, y):
        data = numpy.zeros((self.__clusterSide, self.__clusterSide))
        yArray = numpy.random.normal((self.__centralOffset+y)*self.pixelSize, self.cloudWidth, self.nSamples)
        xArray = numpy.random.normal((self.__centralOffset+x)*self.pixelSize, self.cloudWidth, self.nSamples)
        for i in range(self.nSamples):
            iy = int(yArray[i]/self.pixelSize)
            ix = int(xArray[i]/self.pixelSize)
            try:
                data[iy, ix] += 1
            except:
                pass
        return data##/self.nSamples
        
if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-r","--run",dest="run",
                      help="analyze run RUN", metavar="RUN")
    parser.add_option("-n","--nClusters",dest="nClusters", default= 10000,
                      help="generate n clusters", metavar="NCLUSTERS")
    parser.add_option("--xy",dest="xy",
                      help="generate data at x,y (% of pixel, int, e.g. 75,50)", metavar="XY")
    
    (options,args) = parser.parse_args()

    nClusters = eval(options.nClusters)
        
    x = None
    y = None
    if options.xy is not None:
        try:
            x,y = [eval(x) for x in (options.xy.split(','))]
        except:
            print "have to use format x,y, e.g. 75,50"
            raise RuntimeError

    import time
    t0 = time.time()

##    a = BuildToyCluster("toyClusterLibrary", 50, 19, 10000)
##    a = BuildToyCluster("toyClusterLibrary", 110, 30, 2200)
##    a = BuildToyCluster("toyClusterLibrary", 100, 18, 2200)
##    a = BuildToyCluster("toyClusterLibrary", 100, 30, 6)
    a = BuildToyCluster("toyClusterLibrary", 50, 18, 2200, x, y)
            
    for i in range(nClusters):
        if i == 0:
            clusters = a.buildCluster()
        else:
            clusters = numpy.vstack((clusters, a.buildCluster()))
    t1 = time.time()
    print "generation rate for %d photons is %0.3f photons/s" %(nClusters, nClusters/(t1-t0))
    ySum = numpy.zeros(5)
    xSum = numpy.zeros(5)
    for i in range(nClusters):
        b = clusters[i][2:].reshape((5, 5))
        xSum += b.sum(axis=0)
        ySum += b.sum(axis=1)
    print xSum, xSum.mean()
    xCent = 0
    yCent = 0
    for i in range(5):
        xCent += xSum[i]*(i+1)
        yCent += ySum[i]*(i+1)
    xCent /= nClusters
    yCent /= nClusters
    print xCent, yCent
    print clusters[0:2]
    clusters.dump(a.label+'.npy')
