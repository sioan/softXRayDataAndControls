import math
import numpy, tables
import ROOT, array

from cluster import Cluster, BuildClusters
from buildFrame import BuildFrame

def poisson(n, lmbd):
    p = math.exp(-lmbd)
    for i in xrange(n):
        p *= lmbd
        p /= i+1
    return p

from scipy import special
def neg_bin_distribution(n_k, r, x_avg):
    x = 1.0*numpy.arange(n_k)
    temp1 = numpy.divide(special.gamma(x+r),
                         special.gamma(x+1)*special.gamma(r))
    temp2 = (1 + r/x_avg)**(-x)
    temp3 = (1+ x_avg/r)**(-r)
    return temp1*temp2*temp3


if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-r","--run",dest="run",
                      help="analyze run RUN", metavar="RUN")
    parser.add_option("-n","--nFrames",dest="nFrames", type="int", default=1000,
                      help="generate n frames", metavar="NFRAMES")
    parser.add_option("--rc",dest="rc",
                      help="put photons in row r col c", metavar="RC")
    parser.add_option("-w","--fwhm",dest="fwhm", default=18,
                      help="cloud fwhm in microns", metavar="FWHM")
    parser.add_option("--nc", dest="neighborCut", type="int", default=13,
                      help="neighbor cut in ADU", metavar="NC")
    parser.add_option("-a","--adu",dest="aduPerPhoton", default=120,
                      help="generated adu per photon", metavar="ADU")
    parser.add_option("-l","--lib",dest="lib",
                      help="cloud library", metavar="LIB")
    parser.add_option("--rootLabel", dest="rootLabel", help="root file label")
    parser.add_option("--noiseless", action="store_true", dest="noiseless",
                      default=False, help="do not add noise")

    (options,args) = parser.parse_args()

    nFrames = options.nFrames
    
    testPixelR = None
    testPixelC = None
    if options.rc is not None:
        try:
           testPixelR, testPixelC = [eval(x) for x in (options.rc.split(','))]
        except:
            print "have to use format r,c, e.g. 75,50"
            raise RuntimeError
        print "test pixel row, col:", testPixelC, testPixelR

    fwhm = options.fwhm
    lib = options.lib
    if lib is None:
        lib = "toyClusterLibrary_50_%d_10000.npy" %(fwhm)

    noise = "/reg/neh/home4/philiph/mc/noise_996513537.npy"
    gain = None##"/reg/neh/home1/philiph/psana/xcsi0115/gainPixelCorr_fffs_r88.npy"
    centroidDist = numpy.loadtxt("/reg/neh/home4/philiph/mc/r76_crOffCuts_30_13_1.dat")
    centroid = None
    try:
        import Centroid
        centroid = Centroid.Centroid(centroidDist)
    except:
        pass
    rows = 352*2
    cols = 384*2
    aduPerPhoton = options.aduPerPhoton
    rootLabel = ""
    if options.rootLabel:
        rootLabel = "_" + options.rootLabel

    lmbd = 0.04
    modes = 10.
    nPhotonsMax = 6
    photonDist = numpy.array(nPhotonsMax*[0.])

    if False:
        distType = "pois"
        modes = 0
        for i in range(nPhotonsMax):
            photonDist[i] = poisson(i, lmbd)
    else:
        distType = "nbd"
        nbd = neg_bin_distribution(nPhotonsMax, modes, lmbd)
        for i in range(nPhotonsMax):
            photonDist[i] = nbd[i]

    photonDist /= photonDist.sum()
    print photonDist

    bf = BuildFrame(lib, noise, cols, rows, photonDist, aduPerPhoton/2200., gain, 1.)


    ##tFile = ROOT.TFile('clusters_%s_a%d_l%0.3f_d%s_m%0.2f_gain91full.root' %(lib.split('.')[0], aduPerPhoton, lmbd, distType, modes),'RECREATE')
##    tFile = ROOT.TFile('clusters_%s_a%d_l%0.3f_d%s_m%0.2f_gain91full_centroid.root' %(lib.split('.')[0], aduPerPhoton, lmbd, distType, modes),'RECREATE')
    tFile = ROOT.TFile('clusters_%s_a%d_l%0.3f_d%s_m%0.2f_centroid%s.root' %(lib.split('.npy')[0], aduPerPhoton, lmbd, distType, modes, rootLabel),'RECREATE')
    tTree = ROOT.TTree('ntup','ntup')

    maxClusters = 40000
    tnEvent = array.array('i', [0])
    tnClusters = array.array('i', [0])
    tcOffset = array.array('f',maxClusters*[0])
    trOffset = array.array('f',maxClusters*[0])
    tcFlat = array.array('f',maxClusters*[0])
    trFlat = array.array('f',maxClusters*[0])
    tnPixels = array.array('i',maxClusters*[0])
    tnMaskedPixels = array.array('i',maxClusters*[0])
    tenergy = array.array('f',maxClusters*[0])
    tseedEnergy = array.array('f',maxClusters*[0])
    tseedCol = array.array('i', maxClusters*[0]) 
    tseedRow = array.array('i', maxClusters*[0]) 
    teTotalNoCuts = array.array('f', maxClusters*[0])
    teSecondaryPixelNoCuts = array.array('f', maxClusters*[0])
    tisSquare = array.array('i', maxClusters*[0]) 

    tTree.Branch('nEvent', tnEvent, 'nEvent/I')
    tTree.Branch('nClusters', tnClusters, 'nClusters/I')
    tTree.Branch('energy', tenergy, 'energy[nClusters]/F')
    tTree.Branch('cOffset', tcOffset, 'cOffset[nClusters]/F')
    tTree.Branch('rOffset', tcOffset, 'rOffset[nClusters]/F')
    tTree.Branch('cFlat', tcFlat, 'cFlat[nClusters]/F')
    tTree.Branch('rFlat', trFlat, 'rFlat[nClusters]/F')
    tTree.Branch('nPixels', tnPixels, 'nPixels[nClusters]/I')
    tTree.Branch('nMaskedPixels', tnMaskedPixels, 'nMaskedPixels[nClusters]/I')
    tTree.Branch('seedEnergy', tseedEnergy, 'seedEnergy[nClusters]/F')
    tTree.Branch('seedCol', tseedCol, 'seedCol[nClusters]/I')
    tTree.Branch('seedRow', tseedRow, 'seedRow[nClusters]/I')
    tTree.Branch('eTotalNoCuts', teTotalNoCuts, 'eTotalNoCuts[nClusters]/F')
    tTree.Branch('eSecondaryPixelNoCuts', teSecondaryPixelNoCuts, 'eSecondaryPixelNoCuts[nClusters]/F')
    tTree.Branch('isSquare', tisSquare, 'isSquare[nClusters]/I')

    singles = ROOT.TH1F("singles", "singles", 500, 0, 1000)
    squares = ROOT.TH1F("squares", "squares", 500, 0, 1000)


    filename = 'frames_%s_a%d_l%0.3f_d%s_m%0.2f_centroid%s.h5' %(lib.split('.npy')[0], aduPerPhoton, lmbd, distType, modes, rootLabel)

    tp = tables.open_file(filename, mode='w')
##    atom = tables.Float64Atom((rows, cols)) ## what I expected
    atom = tables.Float64Atom()

##    tableArray = tp.create_earray(tp.root, 'data', atom, (0, nFrames)) ## what I expected
    tableArray = tp.create_earray(tp.root, 'data', atom, (0, rows*cols))

    seedCut = 30
    neighborCut = options.neighborCut
    clusters = []
    for i in range(nFrames):
        bf.makeFrame()
        if not options.noiseless:
            bf.addNoise()
        if testPixelR is None or testPixelC is None:
            bf.addPhotons()
        else:
            bf.addPhotonsToPixel(testPixelC, testPixelR)
##        bf.smearGain()
##        tableArray.append(bf.frame)
        tableArray.append(numpy.array([bf.frame.flatten()])) ## works but is stupid
        if i%100==0:
            print "frame %d" %(i)
            print bf.frame[15:20, 15:20]
        if False:
            continue
        bc = BuildClusters(bf.frame, seedCut, neighborCut)
        fc = bc.findClusters()
        nClusters = 0
        tnEvent[0] = i
        for c in fc:
            if c.goodCluster and nClusters<maxClusters:
                seedCol = c.seedCol
                seedRow = c.seedRow
                centroidCol, centroidRow = c.centroid()
                tcOffset[nClusters] = centroidCol-seedCol
                trOffset[nClusters] = centroidRow-seedRow
                sC = 0
                sR = 0
                if (centroid is not None):
                    sC, sR = centroid.getSmoothedCentroid(tcOffset[nClusters], trOffset[nClusters])
                tcFlat[nClusters] = sC
                trFlat[nClusters] = sR
                tnPixels[nClusters] = c.nPixels
                tnMaskedPixels[nClusters] = c.nMaskedPixels
                tenergy[nClusters] = c.eTotal
                tseedEnergy[nClusters] = c.seedEnergy
                tseedCol[nClusters] = seedCol
                tseedRow[nClusters] = seedRow
                teTotalNoCuts[nClusters] = c.eTotalNoCuts
                teSecondaryPixelNoCuts[nClusters] = c.eSecondaryPixelNoCuts
                tisSquare[nClusters] = int(c.isSquare())
                nClusters += 1
                if c.nPixels == 1:
                    singles.Fill(c.eTotal)
                if c.isSquare:
                    squares.Fill(c.eTotal)


        tnClusters[0] = nClusters
    ##      fullAve = fullSum/ROIrows/ROIcols
        tTree.Fill()

    ##    clusters += fc

    ##import ROOT
    ##tf = ROOT.TFile("testDist_%d.root" %(fwhm), "RECREATE")

    tFile.Write()
    tFile.Close()
