from skbeam.core.accumulators.binned_statistic import RadialBinnedStatistic, RPhiBinnedStatistic
import numpy as np
img = np.reshape(np.arange(9),(3,3))
print 'Image:\n',img
mask = np.ones_like(img)
mask[1][1]=0
print '\nMask:\n',mask

radbinstat = RadialBinnedStatistic(img.shape, bins=3,
                                   statistic='sum',
                                   origin=(0,0),
                                   range = (0,2),
                                   mask=mask)
rphibinstat = RPhiBinnedStatistic(img.shape, bins=(3,1),
                                  statistic='sum',
                                  origin=(0,0),
                                  range = ((0,2),(0,np.pi/3)))
rphibinstat_mask = RPhiBinnedStatistic(img.shape, bins=(3,1),
                                       statistic='sum',
                                       origin=(0,0),
                                       range = ((0,2),(0,np.pi/3)),
                                       mask=mask)
print '\nAngular integration with mask:'
print radbinstat(img)
print '\nBin edges and centers:'
print radbinstat.bin_edges
print radbinstat.bin_centers
print '\n2D R/Phi Angular integration (1 phi bin) with phi range and mask:'
print rphibinstat_mask(img)
print '\n2D R/Phi Angular integration (1 phi bin) with phi range and no mask:'
print rphibinstat(img)
print '\nR/Phi bin edges:'
print rphibinstat.bin_edges[0]
print rphibinstat.bin_edges[1]
