import h5py
import numpy as np
from matplotlib import pyplot as plt
plt.ion()

def hist2d(ar1, ar2,limits=[1,99],numBins=[100,100]):
        pmin0 = np.nanmin(ar1); pmin1 = np.nanmin(ar2)
        pmax0 = np.nanmax(ar1); pmax1 = np.nanmax(ar2)
        if not np.isnan(np.percentile(ar1,limits[0])):
            pmin0 = np.percentile(ar1,limits[0])
        if not np.isnan(np.percentile(ar2,limits[0])):
            pmin1 = np.percentile(ar2,limits[0])
        if limits[1]<100:
            if not np.isnan(np.percentile(ar1,limits[1])):
                pmax0 = np.percentile(ar1,limits[1])
            if not np.isnan(np.percentile(ar2,limits[1])):
                pmax1 = np.percentile(ar2,limits[1])
        v0 = ar1
        v1 = ar2
        binEdges0 = np.linspace(pmin0, pmax0, numBins[0])
        binEdges1 = np.linspace(pmin1, pmax1, numBins[1])
        ind0 = np.digitize(v0, binEdges0)
        ind1 = np.digitize(v1, binEdges1)
        ind2d = np.ravel_multi_index((ind0, ind1),(binEdges0.shape[0]+1, binEdges1.shape[0]+1)) 
        iSig = np.bincount(ind2d, minlength=(binEdges0.shape[0]+1)*(binEdges1.shape[0]+1)).reshape(binEdges0.shape[0]+1, binEdges1.shape[0]+1) 
        plt.imshow(iSig,aspect='auto', interpolation='none',origin='lower',extent=[binEdges1[1],binEdges1[-1],binEdges0[1],binEdges0[-1]],clim=[np.percentile(iSig,limits[0]),np.percentile(iSig,limits[1])])
        return iSig


f = h5py.File('/reg/d/psdm/xpp/xpptut15/ftc/ldat_example_lowIntensity_vonHamos.h5')
print 'we open Run 83 of xcs01116 which contains low intensity data on the von Hamos using an Epix. We will make a few plots using the droplets found in this run'
print f['epix'].keys()
#this returns:
#[u'dropletsAdu', u'dropletsNpix', u'dropletsX', u'dropletsY', u'nDroplets']

####
# plot the number of droplets/event
####
hst_nDrop = np.histogram(f['epix/nDroplets'],np.arange(0,200))
plt.figure(1)
plt.plot(hst_nDrop[1][:-1],hst_nDrop[0],'o')
plt.xlabel('# of droplets')
plt.ylabel('events')
print 'Figure 1 shows the number of droplets/event'

####
# get the per-droplets arrays  for ADU, #of pixels, X and Y
####
#get ADU for complete array
allADU = f['epix/dropletsAdu'].value.flatten()
#request that we have an actual droplet and not a "filler" (I fill the arrays to a common shape with zeros.)
xarr = f['epix/dropletsX'].value.flatten()[allADU>0]
yarr = f['epix/dropletsY'].value.flatten()[allADU>0]
ADUarr = f['epix/dropletsAdu'].value.flatten()[allADU>0]
Npixarr = f['epix/dropletsNpix'].value.flatten()[allADU>0]

####
# plot the number of pixels & ADU for each droplet
####
hst_Npix = np.histogram(Npixarr,np.arange(0,20))
hst_ADU = np.histogram(ADUarr,np.arange(65,300))
plt.figure(2)
plt.subplot(211)
plt.plot(hst_Npix[1][:-1],hst_Npix[0],'o')
plt.xlabel('# pixel in droplets')
plt.ylabel('# events')
plt.subplot(212)
plt.plot(hst_ADU[1][:-1],hst_ADU[0],'o')
plt.xlabel('ADU/droplet')
plt.ylabel('# events')
print 'Figure 2 shows the number of pixels & ADU for all droplets'

####
# plot the positions of all droplets in run
####
plt.figure(3)
hst2dl = hist2d(xarr, yarr, numBins=[100,704])
plt.title('Position of all droplets in Run')
print 'Figure 3 shows the X/Y positions for all droplets'

####
# plot the number of droplets in each even again i0 (ipm3/sum here) - Trivial plot
####
plt.figure(4)
plt.plot(f['epix/nDroplets'],f['ipm3/sum'],'o')
plt.xlabel('# of droplets')
plt.ylabel('ipm3 sum')
print 'Figure 4 shows the number of droplets in an event versus i0 (ipm3/sum)'

###############################################################################
#
#  example for "binning" droplets: her3 I bin in ipm3 (trivial) as we did not scan anything!
#
###############################################################################
# digitize: get index for each event
#### 
binNum =  np.digitize(f['ipm3/sum'].value, np.arange(0.1,4.1,0.1))
#### 
# get the summed ipm3 for each bin
#### 
ipm3_binned = np.bincount(binNum, f['ipm3/sum'].value)
#### 
# get the dropletADU arrays for each bin. 
# This will sum all 1st droplets, all 2nd,.... so you loose the single droplets!
#### 
ADU_binned = np.transpose(np.array([ np.bincount(binNum,f['epix/dropletsAdu'].value[:,i]) for i in np.arange(f['epix/dropletsAdu'].value.shape[1]) ]))
aBins=[]
for Abin in ADU_binned:
    aBins.append(Abin.flatten()[Abin.flatten()>0])
adu_binned = np.array([ab.sum() for ab in aBins ])
# now plot the summed ADU/all droplets uin i0 bins versus i0. - Trivial plot.
plt.figure(5)
plt.plot(ipm3_binned,adu_binned,'o')
plt.xlabel('Signal in droplets, binned')
plt.ylabel('ipm3 sum, binned')
print 'Figure 5 shows the total ADU in all droplets versus i0 in BINS.'

#### 
# to get all droplets in each bin to be able to e.g. look at their x-y positions and make projections,...
# we need to loop over the events in each bin
#### 
binnedPos=[]
for thisBin in range(0,binNum.max()):
        #filter is True for events in a given bin
        filter = binNum==thisBin
        #now get all ADU for all droplets in this bin. This includes the "filler" droplets
        thisADU = f['epix/dropletsAdu'][filter,:]
        #here we only look at events in the bin and then require ADU>0 to remove the "fillers"
        theseX = f['epix/dropletsX'][filter,:].flatten()[thisADU.flatten()>0]
        theseY = f['epix/dropletsY'][filter,:].flatten()[thisADU.flatten()>0]
        binnedPos.append([theseX, theseY])

# plot x-y for two different intensity bins. No Normalization. - Trivial plot.
plt.figure(6)
plt.title('droplet positions for different bins in ipm3 intensity')
plt.subplot(211)
hist2d(binnedPos[5][0], binnedPos[5][1], numBins=[20,70])
plt.subplot(212)
hist2d(binnedPos[25][0], binnedPos[25][1], numBins=[20,70])
print 'Figure 6 shows the X/Y positions of all droplets in two different i0 bins. Not i0 normalized.'
