from psana import *

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import threading
from utilities import binEvents

import sys
sys.path.insert(1,'/reg/common/package/mpi4py/mpi4py-1.3.1/install/lib/python')
sys.path.insert(1,'/reg/g/xpp/xppcode/python')
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

from ixppy.cspad import commonModeCorrectImg
from ixppy.cspad import commonModeCorrectTile
from cspad import get_cspad_pixel_coordinate_index_arrays
import pyimgalgos.GlobalGraphics       as gg
from utilities import *

class xpp_cspadMovie(object):
    def __init__(self):
        if rank == 0:
            print "*** In __init__ "

        self.debug = self.configBool('debug')
        self.timeIt = self.configBool('timeIt')
        self.saveToFile = self.configBool('saveToFile')
        self.fileBasename = self.configStr('fileBasename')
        self.subtractZeroImg = self.configBool('subtractZeroImg')
        self.combined = False
        self.readCspadImage = self.configBool('readCsPadImage')

        self.ipm_lower = self.configFloat('ipm_lower')
        self.ipm_upper = self.configFloat('ipm_upper')
        self.range_lower_tot = self.configFloat('range_lower')
        self.range_upper_tot = self.configFloat('range_upper')
        self.num_bins_tot = self.configInt('num_bins')
        self.requireL3T = self.configBool('requireL3T')
        self.splitBins = self.configBool('splitBins')
        self.online = False

        self.ttCorr = self.configListStr('ttCorr')
        self.binVar = self.configListStr('binVar')

        if (size > 1) and self.splitBins:
            self.num_bins = (int)(self.num_bins_tot/size)
            delta = (self.range_upper_tot-self.range_lower_tot)/size
            self.range_lower = self.range_lower_tot+delta*rank
            self.range_upper = self.range_lower_tot+delta*(rank+1)
        else:
            self.range_lower = self.range_lower_tot
            self.range_upper = self.range_upper_tot
            self.num_bins = self.num_bins_tot

        print 'done with ***Init***'

    # -------------------------------------------------------------------------
    def beginjob(self, evt, env):
        print '*****beginjob***', rank
        if rank == 0:
            print "*** In beginjob, lets start now"
            self.t1 = MPI.Wtime()
        self.total_intens = np.zeros(1)
        self.bin_cspad_sum = binEvents(self.range_lower, self.range_upper, self.num_bins)
        self.bin_intens = binEvents(self.range_lower, self.range_upper, self.num_bins)
        self.expname = env.experiment()
        if (env.jobName().find('shmem')>=0):
            import RegDB.experiment_info
            self.expname =  RegDB.experiment_info.active_experiment('XPP')[1]
            self.online = true
        self.path_calib = '/reg/d/psdm/xpp/'+self.expname+'/calib/CsPad::CalibV1/XppGon.0:Cspad.0/'

    # -------------------------------------------------------------------------
    def beginrun(self, evt, env):
        print '*****beginrun***', rank
        self.eventNr = -1
        self.run = evt.run()
        if rank == 0:
            print "*** In beginrun: run number", self.run
        self.time_ev_sum = 0.
        self.outfileBasename = self.fileBasename+self.expname + '_' + str(self.run) + '_' 
        if (size > 1 ) and self.splitBins:
            self.outfileBasename = self.outfileBasename + 'rank_' + str(rank)

    # ---------------------------------------------------------------------------------
    def begincalibcycle(self, evt, env):

      if self.debug and rank == 0:
        print '*** here in begincalib'

    # ---------------------------------------------------------------------------------
    def event(self, evt, env):        
        self.time_ev_start = MPI.Wtime()
        self.eventNr += 1
        if self.eventNr%100 == 0:
            if rank == 0:
                print "*** In Event: run", self.run, ",event# =", self.eventNr

        ldat = evt.get(object,'littleData')
        if self.eventNr<1 and rank == 0 and self.debug:
            ldat.printKeys()
            
        if self.requireL3T and ldat.l3t.l3t<1:
            if (self.debug):
                print 'failed L3 trigger'
            return

        if len(self.binVar) == 1:
            binVar = ldat.step.ctrlVal[0]
        else:
            binVar = ldat.__dict__[self.binVar[0]].__dict__[self.binVar[1]][0]
            #lxt vitara is in seconds -> xxe-11
            #if self.binVar[0].find('lxt')>=0:
                #binVar *= 1e12 #???
        if len(self.ttCorr) > 1:
            corr = ldat.__dict__[self.ttCorr[0]].__dict__[self.ttCorr[1]][0]
            if corr is not np.nan:
                binVar += corr
        intens = ldat.ipm3.sum[0]

        self.bin_intens.update_bins(binVar, intens)
    
        if not self.readCspadImage:
            cspad_src = psana.Source('DetInfo(XppGon.0:Cspad2x2.0)') 
            cspad_data=evt.get(psana.CsPad2x2.ElementV1, cspad_src )
            #cspad_src = psana.Source('DetInfo(XppGon.0:Cspad.0)')
            #cspad_data=evt.get(psana.CsPad.DataV2, cspad_src )
            if cspad_data is None:
                print "*** could not retrieve cspad data. Skipping event"
                return
            else:
                #q0=cspad_data.quads(0).data()
                #q1=cspad_data.quads(1).data()
                #q2=cspad_data.quads(2).data()
                #q3=cspad_data.quads(3).data()
                #cspad_array=np.concatenate((q0,q1,q2,q3))
                cspad_array = cspad_data.data()
        else:
            #cspad_array = evt.get(psana.ndarray_int16_2, psana.Source('DetInfo(XppGon.0:Cspad.0)'), 'cspad_img')
            cspad_array = evt.get(psana.ndarray_int16_2, psana.Source('DetInfo(XppGon.0:Cspad2x2.0)'), 'cspad_img')
            if cspad_array is None:
                print "*** could not retrieve cspad data. Skipping event"
                return
                        
        self.bin_cspad_sum.update_bins(binVar, cspad_array.flatten().astype(np.int32))

        self.time_ev_stop = MPI.Wtime()
        self.time_ev_sum += self.time_ev_stop-self.time_ev_start

    def endrun(self, evt, env):
        self.t1b = MPI.Wtime()
        self.combine()
        self.combined = True

        if self.timeIt:
            print 'time in cspad event for rank: ', rank,' is ',self.time_ev_sum
        if rank == 0:
            print "*** In endrun: rank 0 "
            self.t2 = MPI.Wtime()
            print "time to endrun ", str(self.t1b-self.t1), " seconds."
            print "time reduced ", str(self.t1c-self.t1b), " seconds."
            print "time arrayShape ", str(self.t1d-self.t1c), " seconds."
            print "time writeFile ", str(self.t1e-self.t1d), " seconds."
            print "time end ", str(self.t2-self.t1b), " seconds."
            print "************* end of run ******************"
            print "total time ", str(self.t2-self.t1), " seconds."
            print "************* end of run ******************"

    def endjob(self, evt, env):
        if rank == 0:
            print "*** In endjob "
            self.t2 = MPI.Wtime()

            #combine now: may not have gone to end of run
        if not self.combined:
            self.combine()

        print 'rank ',rank,' says: done. '
        print "total time ", str(self.t2-self.t1), " seconds."
        print "************* end of job ******************"

    def combine(self):
        if self.bin_cspad_sum._img is None:
            print 'no image has been found!'
            self.t1c = MPI.Wtime()
            self.t1d = self.t1c
            self.t1e = self.t1c
            return
        bin_cspad_sum_img=np.zeros(self.bin_cspad_sum._img.shape, dtype=np.int32)
        comm.Reduce( self.bin_cspad_sum._img, bin_cspad_sum_img)
        if self.debug:
            print 'Bin0: ',np.sum(bin_cspad_sum_img[0]), rank
            print 'Bin1: ',np.sum(bin_cspad_sum_img[1]), rank

        bin_cspad_sum_count=np.zeros(self.bin_cspad_sum._bin_count.shape)
        # if bin_intens._img is not None:
        bin_intensity=np.zeros(self.bin_intens._img.shape)
        if (size > 1) and not self.splitBins:
            comm.Reduce( self.bin_cspad_sum._bin_count, bin_cspad_sum_count)
            comm.Reduce( self.bin_intens._img, bin_intensity)
        else:
            bin_cspad_sum_count =  self.bin_cspad_sum._bin_count
            bin_intensity = self.bin_intens._img

        if self.debug:
            print 'bin count: ',bin_cspad_sum_count, self.bin_cspad_sum._bin_count, rank
        
        #write file with 2-d images only once.
        if rank == 0 or self.splitBins:
            self.t1c = MPI.Wtime()
            binVars = np.linspace(self.bin_cspad_sum._min, self.bin_cspad_sum._max, self.bin_cspad_sum._num_bins)
            if not self.readCspadImage:
                iX, iY = get_cspad_pixel_coordinate_index_arrays(self.path_calib, self.run)

            imageAr=[]
            for iTime in range(0, bin_cspad_sum_img.shape[0]):
                if iTime%10==0:
                    print 'bin number: ',iTime
                if self.debug:
                    print 'iTime: ',iTime,' ',np.sum(bin_cspad_sum_img[iTime,:]),' ',np.sum(bin_cspad_sum_img[0,:])
                if bin_cspad_sum_count[iTime] != 0:
                    if self.subtractZeroImg:
                        imgArray = bin_cspad_sum_img[iTime,:].astype(float)/bin_cspad_sum_count[iTime]-bin_cspad_sum_img[0,:].astype(float)/bin_cspad_sum_count[0]
                    else:
                        imgArray = bin_cspad_sum_img[iTime,:].astype(float)/bin_cspad_sum_count[iTime]
                    if self.readCspadImage:
                        imageAr.append(imgArray)
                    else:
                        #imageAr.append(gg.getImageFromIndexArrays(iX, iY, imgArray))
                        #no geo correction for 2x2
                        imageAr.append(imgArray)
                        
            self.t1d = MPI.Wtime()
            if self.saveToFile:
                print 'saving data to files names like: ',self.outfileBasename
                np.savetxt(self.outfileBasename+"binVars.txt", binVars)
                np.savetxt(self.outfileBasename+"intensity.txt", bin_intensity)
                np.savetxt(self.outfileBasename+"bin_count.txt", bin_cspad_sum_count)
                imageAr = np.array(imageAr)
                imageAr.astype('int32').tofile(outfileBasename+"cspad")
                permiss_cmd = "setfacl -R -m group:" + self.expname + ":rwx " + outdir
                os.system(permiss_cmd)
            self.t1e = MPI.Wtime()
