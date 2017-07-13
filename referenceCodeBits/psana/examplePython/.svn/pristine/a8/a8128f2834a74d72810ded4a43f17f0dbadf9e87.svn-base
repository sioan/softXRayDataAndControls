from psana import *
ds = DataSource('exp=xpptut15:run=54:smd')
det = Detector('cspad')

for nevent,evt in enumerate(ds.events()):
    img = det.image(evt)
    y = img.sum(axis=0)
    break
from psmon.plots import Image,XYPlot
from psmon import publish
publish.local = True
plotimg = Image(0,"CsPad",img)
publish.send('IMAGE',plotimg)
plotxy = XYPlot(0,"Y vs. X",range(len(y)),y)
publish.send('XY',plotxy)
