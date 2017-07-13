# run the plotting tool: "psplot -s psanacs054 -p 12301 ROI_Spectrum_corrected &"
# run the plotting tool: "psplot -s psanacs054 -p 12301 CsPadImage0 &"

from psana import *

import numpy as np
import matplotlib.pyplot as plt

from psmon import publish
from psmon.plots import XYPlot,Image,MultiPlot

import sys
import os
import h5py
p = ["./psmon/src"]
for pi in p:
    if not (pi in sys.path): sys.path.append(pi)

import threading
from psplotserver import ServerScript

import sys
sys.path.insert(1,'/reg/common/package/mpi4py/mpi4py-1.3.1/install/lib/python')
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

from utilities_emission import *

from CalibPars import findCalibFile

class emission(object):
    def __init__(self):
        if rank == 0:
            print "*** In __init__ "

        # read in the configuration file:
        setConfigFile("psmon/src/emission.cfg")
        self.tile = self.configInt('tile_with_signal')
        self.server_port = self.configInt('server_port')
        self.reset_port = self.configInt('reset_port')
        #online:
        #self.ROI = self.configListStr('roi')
        self.threshold_mode = self.configInt('threshold_mode',0)
        self.threshold = self.configInt('threshold', 0)
        self.high_threshold = self.configInt('high_threshold', 30000)
        self.rms_thresh_factor = self.configFloat('rms_thresh_factor', 1.0)
        self.xfel_off_code = self.configInt('xfel_off_code')
        self.beam_sharing = self.configInt('beam_sharing')
        self.use_BLD = self.configStr('use_BLD','')
        self.filter_ipm = self.configInt('filter_ipm',0)
        self.filter_limit = self.configFloat('filter_limit',0.1)
        self.do_norm = self.configInt('do_norm',0)


        # initialize the plotting
        if rank == 0:
            publish.init()

    # -------------------------------------------------------------------------
    def beginjob(self, evt, env):
        if rank == 0:
            print "*** In beginjob, lets start now"

        # online
        self.ROI = get_ROI(evt.run())

        # create x- and y-axis
        self.ax = np.arange(int(self.ROI[2]),int(self.ROI[3]))
        self.ay_sig = self.ax * 0
        self.ay_bkg = self.ax * 0
        self.ay_corr = self.ax * 0

    # -------------------------------------------------------------------------
    def beginrun(self, evt, env):
        if rank == 0:
            print "*** In beginrun: run number", evt.run()
        self.counter = 0
        self.frameNum = 0
        self.frameEmpty = 0
        self.noEVRcounter = 0
        self.eventNr = 0
        self.shots_skipped = 0
        self.all = 0
        self.hitCounter = 0
        self.nohitCounter = 0

        self.epics = env.epicsStore()
        
        if self.threshold_mode == 1:
            # load the rms-file:
            # beamtimes:
            #dir = '/reg/d/psdm/cxi/'+env.experiment()+'/calib/CsPad2x2::CalibV1/CxiSc1.0:Cspad2x2.0/'
            #dir = '/reg/d/psdm/xpp/'+env.experiment()+'/calib/CsPad2x2::CalibV1/XppGon.0:Cspad2x2.0/'
            dir = '/reg/d/psdm/xpp/xppe0314/calib/CsPad2x2::CalibV1/XppGon.0:Cspad2x2.0/'
            rmsfile = findCalibFile(dir,type='pixel_rms',run=evt.run())
            statusfile = findCalibFile(dir,type='pixel_status',run=evt.run())
            tempMask = np.loadtxt(rmsfile)
            tempStatus = np.loadtxt(statusfile)
            self.rms = np.zeros([185,388,2])
            self.status = np.zeros([185,388,2])
            for i in range(0,185):
                self.rms[i] = tempMask[i*388:(i+1)*388,:]
                self.status[i] = tempStatus[i*388:(i+1)*388,:]
            self.rms = self.rms * self.rms_thresh_factor

        # create list for event plotting
        self.evtList = np.arange(0)
        self.sig_norm_gas_List = np.arange(0)
        self.bkg_norm_gas_List = np.arange(0)
        self.sig_norm_cspad_List = np.arange(0)
        self.bkg_norm_cspad_List = np.arange(0)
        


    # ---------------------------------------------------------------------------------
    def event(self, evt, env):        
        if self.eventNr%100 == 0:
            if rank == 0:
                print "*** In event: run", evt.run(), ",event# =", self.eventNr, "  (", self.frameNum, "images, ", self.frameEmpty, "empty,", self.noEVRcounter, "times no EVR,", self.shots_skipped,"shots skipped,",self.hitCounter,'hits, ',self.nohitCounter,'no hits,', self.counter, 'used frames.'

        self.eventNr += 1

        #----------------------
        # check if the xfel was on:
        xfel_status = 0
        EVR_code = evt.get(EvrData.DataV3, Source('DetInfo(NoDetector.0:Evr.0)'))
        if EVR_code is None:
            #print "**** no evr "
            self.noEVRcounter += 1
            return
        xfel_status = check_xfel_status(EVR_code, [self.xfel_off_code, self.beam_sharing])

        if xfel_status == 0:
            #print "*** event skipped due to beam status"
            self.shots_skipped += 1
            return

        # ---------------------
        # ipm and select if event is chosen or not:
        norm = 1

        # get the gas detector value:
        gdet = evt.get(Bld.BldDataFEEGasDetEnergyV1, Source('BldInfo(FEEGasDetEnergy)'))
        if gdet is None:
            return
        gas_detector = gdet.f_22_ENRC()

        # get the attenuator value
        att = self.epics.value('XPP:ATT:COM:R_CUR')
        
        # get the ipm normalisation
        if self.use_BLD:
            if rank == 0 and self.eventNr%100 == 0:
                print "******* in BLD, do_norm=",self.do_norm,'filter_ipm=',self.filter_ipm         
            norm = ipm_norm(self.do_norm,self.filter_ipm,self.filter_limit)
            if norm == 99:
                return

        
        # ---------------------
        # beamtimes:
        src = Source('DetInfo(XppGon.0:Cspad2x2.0)')
        frame = evt.get(CsPad2x2.ElementV1, src, 'calibrated') 
        #src = Source('DetInfo(CxiSc1.0:Cspad2x2.0)')
        #frame = evt.get(CsPad2x2.ElementV1, src, 'calibrated')

        # ---------------------
        if frame is None:
            self.frameEmpty += 1
            return
            #print "No image has been found for event #",self.counter 

        self.frameNum += 1

        cspad_raw = frame.data()
        if self.threshold_mode == 1:
            cspad_thresh = ((cspad_raw > self.rms) * cspad_raw)
            if self.frameNum == 1 and rank == 0:
                print "*** In noise threshold mode "
                #print "cspad =", cspad, "cspad_raw =", cspad_raw
        else:
            cspad_thresh = ((cspad_raw > self.threshold)*cspad_raw)
            if self.frameNum == 1 and rank == 0:
                print "*** In fixed threshold mode"

        # cut off all higher energy adu (like scattering events)
        cspad_thresh2 = ((cspad_thresh < self.high_threshold)*cspad_thresh)

        # correct for bad pixels
        cspad = ((self.status < 1) * cspad_thresh2)

        # get stripe normalisation value
        norm_cspad = cspad[50:70,0:388,self.tile].sum() / float(50*70*388)
        
        # run the hit finder
        (sig_norm_gas,bkg_norm_gas,sig_norm_cspad,bkg_norm_cspad) = hit_finder(cspad[:,:,self.tile], gas_detector, att, norm_cspad)
        
        # plot signal and background:
        self.evtList = np.append(self.evtList, self.counter)
        self.sig_norm_gas_List = np.append(self.sig_norm_gas_List, sig_norm_gas)
        self.bkg_norm_gas_List = np.append(self.bkg_norm_gas_List, bkg_norm_gas)
        self.sig_norm_cspad_List = np.append(self.sig_norm_cspad_List, sig_norm_cspad)
        self.bkg_norm_cspad_List = np.append(self.bkg_norm_cspad_List, bkg_norm_cspad)

        self.counter += 1

        # fill the cspad arrays
        cspad_sig = cspad[int(self.ROI[0]):int(self.ROI[1]),int(self.ROI[2]):int(self.ROI[3]),self.tile]
        cspad_bkg = cspad[int(self.ROI[0]):int(self.ROI[1]),int(self.ROI[2]):int(self.ROI[3]),1-self.tile]

        cspad0 = cspad[:,:,0]
        cspad1 = cspad[:,:,1]

        # plot single images
        if self.counter < 5 and 6 > 15:
            plt.figure(1)
            plt.imshow(cspad1, vmax=50)
            plt.colorbar()
            plt.show()


        # ---------------------
        # add the images and get the average
        #if self.frameNum == 1:
        if self.counter == 1:
            self.cspad = np.zeros_like(cspad, dtype=np.float)
            self.cspad0 = np.zeros_like(cspad0, dtype=np.float)
            self.cspad1 = np.zeros_like(cspad1, dtype=np.float)
            self.cspad_sig = np.zeros_like(cspad_sig, dtype=np.float)
            self.cspad_bkg = np.zeros_like(cspad_bkg, dtype=np.float)

            if self.tile == 0:
                self.cspadN = np.zeros_like(cspad0, dtype=np.float)
            else:
                self.cspadN = np.zeros_like(cspad1, dtype=np.float)
            self.cspadN_ones = self.cspadN + 1
            
        # add the detector
        self.cspad += cspad
        self.cspad0 += cspad0
        self.cspad1 += cspad1
        self.cspad_sig += cspad_sig
        self.cspad_bkg += cspad_bkg

        # create a map with number of hits above the threshold
        if self.tile == 0:
            self.cspadN += (cspad0 > self.threshold) * self.cspadN_ones 
        else:
            self.cspadN += (cspad1 > self.threshold) * self.cspadN_ones

        if self.counter%100 == 0:
            # plot the images
            # note: this is not needed for the full cspad.
            self.cspad0 = np.ascontiguousarray(self.cspad0)
            self.cspad1 = np.ascontiguousarray(self.cspad1)
            self.cspad_sig = np.ascontiguousarray(self.cspad_sig)
            self.cspad_bkg = np.ascontiguousarray(self.cspad_bkg)
            self.cspadN = np.ascontiguousarray(self.cspadN)
            
            if 'self.cspad0_all' not in locals():
                self.cspad_all = np.empty_like(cspad, dtype=np.float)
                self.cspad0_all = np.empty_like(cspad0, dtype=np.float)
                self.cspad1_all = np.empty_like(cspad1, dtype=np.float)
                self.cspad_sig_all = np.empty_like(cspad_sig, dtype=np.float)
                self.cspad_bkg_all = np.empty_like(cspad_bkg, dtype=np.float)
                self.cspadN_all = np.empty_like(self.cspadN, dtype=np.float)

            # add all images from the different processors
            comm.Reduce(self.cspad, self.cspad_all) # this automatically sums all the cores
            comm.Reduce(self.cspad0, self.cspad0_all)
            comm.Reduce(self.cspad1, self.cspad1_all)
            comm.Reduce(self.cspad_sig, self.cspad_sig_all)
            comm.Reduce(self.cspad_bkg, self.cspad_bkg_all)
            comm.Reduce(self.cspadN, self.cspadN_all)

            # get the correct counter
            counter_nodes = np.array([self.counter])
            counter_all = np.empty_like(counter_nodes)
            comm.Reduce(counter_nodes,counter_all)
            self.all = counter_all[0]

            if rank == 0:
                # get the averages and publish
                self.cspad_ave = self.cspad_all/self.all
                self.cspad0_ave = self.cspad0_all/self.all
                cam = Image(self.all, "CsPadImage0", self.cspad0_ave)
                publish.send("CsPadImage0", cam)
                self.cspad1_ave = self.cspad1_all/self.all
                cam = Image(self.all, "CsPadImage1", self.cspad1_ave)
                publish.send("CsPadImage1", cam)
                self.cspad_sig_ave = self.cspad_sig_all/self.all
                cam = Image(self.all, "CsPad2x2_Signal_ROI", self.cspad_sig_ave)
                publish.send("CsPad2x2_Signal_ROI", cam)
                self.cspad_bkg_ave = self.cspad_bkg_all/self.all
                cam = Image(self.all, "CsPad2x2_Bkg_ROI", self.cspad_bkg_ave)
                publish.send("CsPad2x2_Bkg_ROI", cam)
                self.cspadN_ave = self.cspadN_all/self.all
                cam = Image(self.all, "PixelsAboveThreshold", self.cspadN_all)
                publish.send("PixelsAboveThreshold", cam)
            
                # add the roi projection and plot
                self.ay_sig = self.cspad_sig_ave.sum(axis=0)
                emSignal = XYPlot(self.all, "ROI_Spectrum", self.ax, self.ay_sig)
                publish.send("ROI_Spectrum", emSignal)
                self.ay_bkg = self.cspad_bkg_ave.sum(axis=0)
                emSignal = XYPlot(self.all, "ROI_Bkg", self.ax, self.ay_bkg)
                publish.send("ROI_Bkg", emSignal)
                self.ay_corr = self.ay_sig - self.ay_bkg
                emSignal = XYPlot(self.all, "ROI_Spectrum_Bkg_subtracted", self.ax, self.ay_corr)
                publish.send("ROI_Spectrum_Bkg_subtracted", emSignal)

                hit_norm_gas = XYPlot(self.all, "Gas_normalised", [self.evtList, self.evtList], [self.sig_norm_gas_List, self.bkg_norm_gas_List], formats=['r.','gd'])
                publish.send("Gas_normalised", hit_norm_gas)
                hit_norm_cspad = XYPlot(self.all, "cspad_normalised", [self.evtList, self.evtList], [self.sig_norm_cspad_List, self.bkg_norm_cspad_List], formats=['r.','gd'])
                publish.send("cspad_normalised", hit_norm_cspad)

    def endrun(self, evt, env):
        # collect the reso of the events
        self.cspad0 = np.ascontiguousarray(self.cspad0)
        self.cspad1 = np.ascontiguousarray(self.cspad1)
        self.cspad_sig = np.ascontiguousarray(self.cspad_sig)
        self.cspad_bkg = np.ascontiguousarray(self.cspad_bkg)
        self.cspadN = np.ascontiguousarray(self.cspadN)
            
        if 'self.cspad0_all' not in locals():
            self.cspad_all = np.empty_like(self.cspad, dtype=np.float)
            self.cspad0_all = np.empty_like(self.cspad0, dtype=np.float)
            self.cspad1_all = np.empty_like(self.cspad1, dtype=np.float)
            self.cspad_sig_all = np.empty_like(self.cspad_sig, dtype=np.float)
            self.cspad_bkg_all = np.empty_like(self.cspad_bkg, dtype=np.float)
            self.cspadN_all = np.empty_like(self.cspadN, dtype=np.float)
        
        # add all images from the different processors
        comm.Reduce(self.cspad, self.cspad_all) # this automatically sums all the cores
        comm.Reduce(self.cspad0, self.cspad0_all)
        comm.Reduce(self.cspad1, self.cspad1_all)
        comm.Reduce(self.cspad_sig, self.cspad_sig_all)
        comm.Reduce(self.cspad_bkg, self.cspad_bkg_all)
        comm.Reduce(self.cspadN, self.cspadN_all)
        
        # get the correct counter
        counter_nodes = np.array([self.counter])
        counter_all = np.empty_like(counter_nodes)
        comm.Reduce(counter_nodes,counter_all)
        self.all = counter_all[0]


        if rank == 0:
            print "*** In endrun "
            # get the averages and publish
            self.cspad_ave = self.cspad_all/self.all
            self.cspad0_ave = self.cspad0_all/self.all
            cam = Image(self.all, "CsPadImage0", self.cspad0_ave)
            publish.send("CsPadImage0", cam)
            self.cspad1_ave = self.cspad1_all/self.all
            cam = Image(self.all, "CsPadImage1", self.cspad1_ave)
            publish.send("CsPadImage1", cam)
            self.cspad_sig_ave = self.cspad_sig_all/self.all
            cam = Image(self.all, "CsPad2x2_Signal_ROI", self.cspad_sig_ave)
            publish.send("CsPad2x2_Signal_ROI", cam)
            self.cspad_bkg_ave = self.cspad_bkg_all/self.all
            cam = Image(self.all, "CsPad2x2_Bkg_ROI", self.cspad_bkg_ave)
            publish.send("CsPad2x2_Bkg_ROI", cam)
            self.cspadN_ave = self.cspadN_all/self.all
            cam = Image(self.all, "PixelsAboveThreshold", self.cspadN_all)
            publish.send("PixelsAboveThreshold", cam)
            
            # add the roi projection and plot
            self.ay_sig = self.cspad_sig_ave.sum(axis=0)
            emSignal = XYPlot(self.all, "ROI_Spectrum", self.ax, self.ay_sig)
            publish.send("ROI_Spectrum", emSignal)
            self.ay_bkg = self.cspad_bkg_ave.sum(axis=0)
            emSignal = XYPlot(self.all, "ROI_Bkg", self.ax, self.ay_bkg)
            publish.send("ROI_Bkg", emSignal)
            self.ay_corr = self.ay_sig - self.ay_bkg
            emSignal = XYPlot(self.all, "ROI_Spectrum_Bkg_subtracted", self.ax, self.ay_corr)
            publish.send("ROI_Spectrum_Bkg_subtracted", emSignal)    

            hit_norm_gas = XYPlot(self.all, "Gas_normalised", [self.evtList, self.evtList], [self.sig_norm_gas_List, self.bkg_norm_gas_List], formats=['r.','gd'])
            publish.send("Gas_normalised", hit_norm_gas)
            hit_norm_cspad = XYPlot(self.all, "cspad_normalised", [self.evtList, self.evtList], [self.sig_norm_cspad_List, self.bkg_norm_cspad_List], formats=['r.','gd'])
            publish.send("cspad_normalised", hit_norm_cspad)

        # save the data
        if self.frameNum > 0 and rank == 0:
            # beamtimes:
            #filename = '/reg/neh/home/tkroll/ana-0.12.0/data_offline/xppe0314_'+str(evt.run())+'.h5'
            filename = '/reg/neh/home/snelson/Workarea/ana-0.12.1/data_offline/xppe0314_10'+str(evt.run())+'.h5'
            #filename = 'data/xppd7114_'+str(evt.run())+'.h5'
            #filename = 'data/cxib6714_'+str(evt.run())+'.h5'
            ofile = h5py.File(filename,'w')
            group = ofile.create_group("mydata")
            group.create_dataset("signal_x",data=self.ax)
            group.create_dataset("signal_y",data=self.ay_sig)
            group.create_dataset("bkg_x",data=self.ax)
            group.create_dataset("bkg_y",data=self.ay_bkg)
            group.create_dataset("average_frame",data=self.cspad_ave)
            group.create_dataset("full_frame",data=self.cspad)
            group.create_dataset("NumberOfPixels", data=self.cspadN_all)
            group.create_dataset("BadPixelMap", data=self.status)
            group.create_dataset("event_number", data=self.evtList)
            group.create_dataset("Signal_Gas_normalised", data=self.sig_norm_gas_List)
            group.create_dataset("Bkg_Gas_normalised", data=self.bkg_norm_gas_List)
            group.create_dataset("Signal_cspad_normalised", data=self.sig_norm_cspad_List)
            group.create_dataset("Bkg_cspad_normalised", data=self.bkg_norm_cspad_List)
            ofile.close()
            print 'file saved as ', filename

        if rank == 0:
            print self.eventNr, " events have been processed in run", evt.run(), ": ", self.frameNum, "images, ", self.frameEmpty, "empty frames, ",self.noEVRcounter, "times no EVR, and", self.shots_skipped, "shots were skipped."

    def endjob(self, evt, env):
        if rank == 0:
            print "*** In endjob "

            print "*** done "




        
