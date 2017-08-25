from psana import *
from psmon.plots import Image
from psmon import publish
ds = DataSource('exp=xpptut15:run=54:smd')
det = Detector('cspad')
for nevent,evt in enumerate(ds.events()):
    img = det.image(evt)
    plotimg = Image(0,"CsPad",img)
    publish.send('IMAGE',plotimg)
    raw_input('Hit <CR> for next event')
    if nevent>=2: break
