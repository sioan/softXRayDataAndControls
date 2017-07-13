import numpy as np
import h5py
from os import walk
from os import path

def getFilelist(expname, run, dirname):
    filelist=[]
    fnameBase = 'ldat_%s_Run%i_'%(expname,run)
    print 'dirname: ',dirname, ' BASE ',fnameBase
    for (dirpath, dirnames, filenames) in walk(dirname):
        for fname in filenames:
            if fname.find(fnameBase) >=0:
                filelist.append(dirname+fname)
    filelist.sort()
    return filelist

def getKeys(h5file):
    fullkeys = []
    for key in (h5file).keys():
        try:
            for skey in (h5file)[key].keys():
                print'%s/%s'%(key,skey)
                fullkeys.append('%s/%s'%(key,skey))
        except:
            fullkeys.append('%s'%(key))
            pass
    return fullkeys    

def merge(files, expname, run, outDir):
    fnameBase = 'ldat_%s_Run%i'%(expname,run)
    foutName=outDir+fnameBase+".h5"
    fMerged = h5py.File(foutName, "w")
    fullkeys = getKeys(files[0])
    for key in fullkeys:
        if key == 'cnf':
            dsetcnf = fMerged.create_dataset('cnf', [1.], dtype='f')
            dsetcnf.attrs['cnf'] = (files[0])['cnf'].attrs.values()[0]
        else:
            #get data.
            Ar = ((files[0])[key].value).tolist()
            npAr = (files[0])[key].value
            for i in range(1, len(flist)):
                #print 'file ',i
                #print 'key: ',key
                arTemp = ((files[i])[key].value).tolist()
                Ar.extend(arTemp)
            arShape=()
            for i in range(0,len(npAr.shape)):
                if i == 0:
                    arShape+=(len(Ar),)
                else:
                    arShape+=(npAr.shape[i],)
            if key.find('EvtID')>=0:
                print 'create dset of int32: ',key
                dset = fMerged.create_dataset(key, arShape, dtype='int32')
            else:
                print 'create dset of float: ',key
                dset = fMerged.create_dataset(key, arShape, dtype='f')
            dset[...] = np.array(Ar)
    fMerged.close()
    print 'closed file: ',foutName


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("expname", help="experiment name")
parser.add_argument("run", help="run number", type=int)
parser.add_argument("indir", help="input directory", default='./')
parser.add_argument("outdir", help="output directory", default='./')
args = parser.parse_args()
runInput = args.run
expName = args.expname
inDir = args.indir
outDir = args.outdir

flist = getFilelist(expName, runInput, inDir)
print 'for expname ',expName,' and run ',runInput,' we will merge these files: ',flist,' and write it to: ',outDir
    
files = []
for fname in flist:
    files.append(h5py.File(fname,"r"))

merge(files, expName, runInput, outDir)
