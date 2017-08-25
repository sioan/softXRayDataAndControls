from psana import *
import numpy as np
runnum = 54
ds = DataSource('exp=xpptut15:run=%d:smd'%runnum)
det = Detector('cspad')

mask = det.mask(runnum,calib=True,status=True,edges=True,central=True,unbond=True,unbondnbrs=True)
for nevent,evt in enumerate(ds.events()):
    calib_array = det.calib(evt)
    # apply the mask
    calib_masked = calib_array * mask
    break

# make a 2D image (with geometry) out of any correctly-shaped array
mask_image = det.image(runnum,mask)
import matplotlib.pyplot as plt
plt.imshow(mask_image,vmin=-2,vmax=2,interpolation='none')
plt.show()
