import psana

ds = psana.DataSource('exp=xpptut15:run=54:smd')
det = psana.Detector('cspad')

from ImgAlgos.PyAlgos import PyAlgos
alg = PyAlgos()
alg.set_peak_selection_pars(npix_min=2, npix_max=50, amax_thr=10, atot_thr=20, son_min=5)
 
hdr = '\nSeg  Row  Col  Npix    Amptot'
fmt = '%3d %4d %4d  %4d  %8.1f'
 
for nevent,evt in enumerate(ds.events()):
    if nevent>=2 : break
    nda = det.calib(evt)
    if nda is None: continue

    peaks = alg.peak_finder_v1(nda, thr_low=5, thr_high=21, radius=5, dr=0.05)

    print hdr
    for peak in peaks :
        seg,row,col,npix,amax,atot = peak[0:6]
        print fmt % (seg, row, col, npix, atot)
