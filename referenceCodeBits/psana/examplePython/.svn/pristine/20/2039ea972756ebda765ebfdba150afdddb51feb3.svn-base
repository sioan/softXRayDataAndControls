from psana import *
from skbeam.core.accumulators.histogram import Histogram
import numpy as np

# 1D histogram: 11 bins going from -5.5 to 5.5
hist = Histogram((11,-5.5,5.5))

hist.fill(4)
hist.fill(0,weights=2)
x = np.array((-4,-4,-4))
weights = np.array((1,1,0.5))
hist.fill(x,weights=weights)

import matplotlib.pyplot as plt
plt.plot(hist.centers[0],hist.values)
plt.title('1D Histogram Results')
plt.show()

# 2D histogram: 3 bins in x going from -0.5 to 2.5
# and 2 bins going from -0.5 to 1.5
hist2d = Histogram((3,-0.5,2.5),(2,-0.5,1.5))

hist2d.fill(1,1)
x = np.array((0,1,2))
y = np.array((0,1,2))
weights = np.array((5.5,2.5,9999.))
hist2d.fill(x,y,weights=weights)
print '2D histogram values:\n',hist2d.values
