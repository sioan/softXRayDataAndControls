from psana import *
ds = DataSource('exp=xpptut15:run=54:smd')
det = Detector('cspad')
for nevent,evt in enumerate(ds.events()):
    img = det.image(evt)
    # NOTE: non-contiguous array must be copied before using with MPI
    roi = img[135:140,150:160]
    break

import matplotlib.pyplot as plt
plt.imshow(roi,interpolation='none')
plt.show()
