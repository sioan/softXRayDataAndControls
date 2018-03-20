from psana import *
import h5py
import numpy


from scipy.signal import savgol_filter
from scipy.optimize import curve_fit
import sys
import IPython

fullAnalysis = False

class RunningAverage:
    def __init__(self, size):
        self.filterCounter = 0
        self.filterSize = size
        self.ringbuffer = None
    
    def add(self, element):
        # add this trace to the running average:
        if self.ringbuffer is None:
            ttLength = len(element)
            self.ringbuffer = numpy.zeros([self.filterSize,ttLength])
        self.ringbuffer[self.filterCounter, :] = element
        self.filterCounter = (self.filterCounter + 1)%self.filterSize
        self.average = numpy.average(self.ringbuffer, axis=0)
        

        
def peakFunction(x,a,x0,offset):
    return a*(x-x0)**2+offset

class BadEvent(Exception):
    pass

def gather_monitor(results):
    smldata._small_file.file_handle.flush()

####################################################################################
###################### MAIN ########################################################
####################################################################################

runNumber = int(sys.argv[1])

# This is the analysis code for the run:

# settings for the integration boundaries iZero ADCs
iZeroMCPFrom = 1100
iZeroMCPTo = 1300

iZeroMembraneFrom = 1000
iZeroMembraneTo = 2000

diagDiodeFrom = 1000
diagDiodeTo = 3000

transmittedIntensityFrom = 1000
transmittedIntensityTo = 1300

averageTimetool = 10
svd_size =4
runStartingWithMonoCalib = 40

# for shared memory:
#shmem=psana.0:stop=no

dataset_name = "exp=SXR/sxrlr2916:run="+str(runNumber)+":smd:dir=/reg/d/ffb/sxr/sxrlr2916/xtc:live"
#dataset_name = "exp=SXR/sxrlr2916:run="+str(runNumber)+":smd:"
#dataset_name = "exp=xpptut15:run=420:smd"

# read the Eigen base for the time tool background
if fullAnalysis:
    eigenFile = h5py.File("../../tables/eigen"+str(runNumber)+".h5", 'r')
    eigenBackground = (eigenFile['eigen'].value).transpose()
    eigenFile.close()

ds = MPIDataSource(dataset_name)
sampleTransmissionDet = Detector('andor')
monoDet = Detector('MONO_encoder')
monoEpics = Detector('SXR:MON:MMS:06.RBV')
acquiris1 = Detector('Acq01')

# detector for the mono scaling parameters (available for the runs > 40):
if runNumber >= runStartingWithMonoCalib:
    monoCalibA = Detector('SXR:IOC:POLY:POLY:Lambda:O1:G3:A')
    monoCalibB = Detector('SXR:IOC:POLY:POLY:Lambda:O1:G3:B')
    monoCalibC = Detector('SXR:IOC:POLY:POLY:Lambda:O1:G3:C')

acquiris2 = Detector('Acq02')
#hsd = Detector('hsd')
delayStageDet =  Detector('DLS_encoder')

magnetCurrentDet = Detector('SXR:EXP:AIN:1')

laserRfDelay = Detector('LAS:FS2:VIT:FS_TGT_TIME_DIAL')

phaseCavityDet = Detector('PhaseCavity')

# detector for the event receiver:
evr = Detector('evr0')

# time tool analysis: detector

if fullAnalysis:
    timeToolCamera = Detector('TSS_OPAL')
    timeToolBufferEven = RunningAverage(averageTimetool)
    timeToolBufferOdd  = RunningAverage(averageTimetool)

laserThrottle = Detector('SXR:LAS:MCN3:07.RBV')


# Stuff for the hdf5 file:
smldata = ds.small_data("../../tables/" + str(runNumber) + '.h5')
smldata.add_monitor_function(gather_monitor)
i=0 
enumEvents = enumerate(ds.events())
# IPython.embed()
for num,evt in enumEvents:
    try:
    
        ec = evr.eventCodes(evt)
        if ec is None:
            raise BadEvent()
    
        # remove dark shots
        #if 162 in ec:
        #    raise BadEvent()
    
        transmissionImg = sampleTransmissionDet.calib(evt)
        if transmissionImg is None:    
            raise BadEvent()
    
        waves1 = acquiris1.waveform(evt)
        if waves1 is None:
            raise BadEvent()
        
        waves2 = acquiris2.waveform(evt)
        if waves2 is None:
            raise BadEvent()
            
        #waves3 = hsd.raw(evt)
        #if waves3 is None:
        #    raise BadEvent()
    
        mono = monoDet.values(evt)
        if mono is None:
            raise BadEvent()
        
        delayStage = delayStageDet.values(evt)
        if delayStage is None:
            raise BadEvent()
        
        phaseCavityVal = phaseCavityDet.get(evt)
        if phaseCavityVal is None:
            raise BadEvent()
        phaseCavity = phaseCavityVal.fitTime1()
        
    
        timeToolError =0.0
        timeToolPosition = 0.0
        # read the time tool camera and calculate the running average
        if fullAnalysis:
            timeToolImage = timeToolCamera.calib(evt)[300:,:]
            if timeToolImage is None:
                raise BadEvent()
            timeToolTrace = numpy.average(timeToolImage, axis=0)
    
    
            timeToolBufferOdd.add(timeToolTrace)
            timeToolTraceAveraged = None
            # here we need to do the actual time tool analysis...
            #if (num % 2 == 0):
            if 141 in ec:
                timeToolBufferEven.add(timeToolTrace)
                timeToolTraceAveraged = timeToolBufferEven.average
            else:
                timeToolBufferOdd.add(timeToolTrace)
                timeToolTraceAveraged = timeToolBufferOdd.average

            # analysis of the time tool data (according to Sioan)
            backgroundSubtracted = timeToolTraceAveraged - numpy.dot(numpy.dot(
                timeToolTraceAveraged,eigenBackground[:svd_size].transpose()),eigenBackground[:svd_size])
            filtered_signal = -savgol_filter(backgroundSubtracted,25,2,0) # don't derive... and use minus...
            win_c = numpy.argmax(abs(filtered_signal))
            initial_guess = [1,win_c,abs(filtered_signal[win_c])]
            
            try:
                popt,pcov = curve_fit(peakFunction,numpy.arange(win_c-4,win_c+5),abs(filtered_signal[win_c-4:win_c+5]), p0=initial_guess)
                timeToolError = pcov[1,1]
                timeToolPosition = popt[1]
            except (RuntimeError,ValueError):
                timeToolError =-999.0
                timeToolPosition = -999.0
    
        # do the averaging of the data of interest:
        transmittedIntensity = numpy.average(transmissionImg[0,transmittedIntensityFrom:transmittedIntensityTo]) \
        - numpy.average(transmissionImg[0,0:transmittedIntensityFrom])
        
        # calculate the integral of the iZero signals (integral over pulse - average before pulse)
        iZeroMCP = numpy.average(waves2[3].astype(float)[iZeroMCPFrom:iZeroMCPTo]) \
        - numpy.average(waves2[3].astype(float)[0:iZeroMCPFrom])
        
        # iZeroMCP = 0.0
        iZeroMembrane = numpy.average(waves1[2, iZeroMembraneFrom:iZeroMembraneTo])-numpy.average(waves1[2, 0:iZeroMCPFrom])
        
        # diagDiode
        diagDiode = numpy.average(waves1[1, diagDiodeFrom:diagDiodeFrom])-numpy.average(waves1[1, 0:diagDiodeFrom])
        
        i=i+1
    
        # add the event to smldata
        
        smldata.event(transmittedIntensity=transmittedIntensity,
                     iZeroMCP = float(iZeroMCP),
                     iZeroMembrane = float(iZeroMembrane),
                     diagDiode = float(diagDiode),
                     monoEncoder = float(mono[0]),
                     monoEpics = float(monoEpics(evt)),
                     magnetCurrentDet=float(magnetCurrentDet(evt)),
                     delayStageEncoder = float(delayStage[0]),
                     timeToolPosition = float(timeToolPosition),
                     timeToolError = float(timeToolError),
                     laserRfDelay = float(laserRfDelay(evt)),
                     phaseCavity = float(phaseCavity),
                     laserThrottle = float(laserThrottle(evt)))
        
    except (BadEvent):
        #print "bad event"
        smldata.event(transmittedIntensity=-999.,
                 iZeroMCP = -999.,
                 iZeroMembrane = -999.,
                 diagDiode = -999.,
                 monoEncoder = -999.,
                 monoEpics = -999.,
                 magnetCurrentDet=-999.,
                 delayStageEncoder = -999.,
                 timeToolPosition = -999.,
                 timeToolError = -999.,
                 laserRfDelay = -999.,
                 phaseCavity  = -999.,
                 laserThrottle = -999.)
        
    #if i > 200:
    #    break
    #if (i % 100) == 0:
    #    print "saving data, i=" + str(i)
    #    smldata.save()
        
if runNumber >= runStartingWithMonoCalib:
    smldata.save(monoCalibA = monoCalibA(evt), monoCalibB = monoCalibB(evt), monoCalibC = monoCalibC(evt))
else:
    smldata.save()
smldata.close()