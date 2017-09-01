from psana import *
import numpy as np
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def merge_dicts(dict_list):
   """
   Given any number of dicts, shallow copy and merge into a new dict,
   precedence goes to key value pairs in latter dicts.
   """
   result = {}
   for dictionary in dict_list:
      print dictionary
      result.update(dictionary)
   return result

dsource = MPIDataSource('exp=xpptut15:run=54:smd')
cspaddet = Detector('cspad')

smldata = dsource.small_data('run54.h5',gather_interval=100)

partial_run_sum = None
andorImages = {}
for nevt,evt in enumerate(dsource.events()):
   fid = evt.get(EventId).fiducials()
   calib = cspaddet.calib(evt)
   if calib is None: continue
   cspad_sum = calib.sum()      # number
   cspad_roi = calib[0][0][3:5] # array
   if partial_run_sum is None:
      partial_run_sum = cspad_roi
   else:
      partial_run_sum += cspad_roi

   if nevt%3==0 and rank!=2: andorImages['time'+str(fid)]=np.array([1,2,3])

   # save per-event data
   smldata.event(cspad_sum=cspad_sum,cspad_roi=cspad_roi)
   if nevt>10: break

allAndorImages = comm.gather(andorImages,root=0)

print allAndorImages
# save HDF5 file, including summary data
if rank==0:
   mergedAndorImages = merge_dicts(allAndorImages)
   print mergedAndorImages
   smldata.save(**mergedAndorImages)
else:
   smldata.save()
