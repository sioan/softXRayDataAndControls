import psana

ds = psana.DataSource('exp=xpptut15:run=54:smd')
det = psana.Detector('cspad')

from ImgAlgos.PyAlgos import PyAlgos
alg = PyAlgos()
 
for nevent,evt in enumerate(ds.events()):
    if nevent>=2 : break
    nda = det.calib(evt)
    if nda is None: continue

    thr = 20
    numpix = alg.number_of_pix_above_thr(nda, thr)
    totint = alg.intensity_of_pix_above_thr(nda, thr)
    print '%d pixels have total intensity %5.1f above threshold %5.1f' % (numpix, totint, thr)
