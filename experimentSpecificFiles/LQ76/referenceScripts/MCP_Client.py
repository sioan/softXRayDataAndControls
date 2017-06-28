from psana import *
import numpy as np
from mpidata import mpidata 
import scipy.optimize as optimization
import time

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def runclient(args,pars):


    # load single pulse data
    singlePulse = np.load('singlePulse.npz')['avePulse']
    # make it match the length of the Acqiris trace (this will change)    
    singlePulse = np.pad(singlePulse, (7500, 7500), 'constant', constant_values=(0, 0))
    # normalize trace to peak so that the amplitude we fit is proportional to peak values on MCP trace
    singlePulse = singlePulse/np.max(singlePulse)

    # location of peak in reference trace
    peak1 = np.argmax(singlePulse)
    
    # optimization function
    def optFunc(p, xdata, ydata, pulse):
        a1, a2, x1, x2 = p
        err = np.abs(ydata - (a1*np.interp(xdata-x1, xdata, pulse) + a2*np.interp(xdata-x2, xdata, pulse)))
        return err

    # function that returns curve
    def evalFunc(p, xdata, pulse):
        a1, a2, x1, x2 = p
        curve = a1*np.interp(xdata-x1, xdata, pulse) + a2*np.interp(xdata-x2, xdata, pulse)
        return curve
  
    # expected delay based on what we asked from the accelerator
    delay = args.delay

    # initialize fitting parameters (actually I don't think these are being used...)
    x1_0 = 4478.0 # based on visual inspection of data
    x2_0 = x1_0 + delay/.125 # based on expected delay time
    a1_0 = 1.0 # arbitrary
    a2_0 = 1.0 # arbitrary
    p0 = [a1_0, a2_0, x1_0, x2_0] # put into array

    # array for interpolation
    xdata = np.arange(0, 20000)

    # where to find the data
    sh_mem = pars['live']
    expName = pars['expName']
    runNum = args.run
    runString = 'exp='+expName+':run='+runNum+':smd'

    # needed for shared memory access
    calibDir = '/reg/d/psdm/sxr/'+expName+'/calib'
    
    # check whether we're reading from shared memory or old run
    ds = []
    if sh_mem:
        runString += ':dir=/reg/d/ffb/sxr/'+expName+'/xtc:live' 
        ds = DataSource(''.join(['shmem=psana.',
                        str(rank%8),
                        ':stop=no']))
        setOption('psana.calib-dir', calibDir)
    else:
        ds = DataSource(runString)

    # acqiris detector
    acq = Detector('Acq02')

    # number of events between updates (set in MCP_driver.py)
    updateEvents = pars['updateEvents']


    # initialize instance of the mpidata class for communication with the master process
    md = mpidata()
    
    # counter (local per core)
    n1 = -1
    
    # initialize arrays
    x1Array = np.empty(0)
    x2Array = np.empty(0)
    a1Array = np.empty(0)
    a2Array = np.empty(0)

    # initialize acqiris trace
    wf = np.zeros(20000)
    
    # event loop
    for nevent,evt in enumerate(ds.events()):

        # check if we've reached the event limit        
        if nevent == args.noe : break
        if nevent%(size-1)!=rank-1: continue # different ranks look at different events
        # skip damaged events
        if acq.waveform(evt) is None: continue # damage

        # update counter
        n1 += 1
        
        # get MCP trace
        wf = acq.waveform(evt)[0].flatten()
        # subtract background (assume at least 10000 data points before pulse)
        wf = wf - np.mean(wf[0:10000])
        
        # guesses for fit parameters
        # peak of first pulse
        p0a1 = np.max(wf)
        # time position of first pulse (relative to reference)
        p0x1 = np.argmax(wf) - peak1
        # subtract first pulse guess from MCP trace
        wf2 = wf - evalFunc([p0a1,0,p0x1,0],xdata,singlePulse)

        # peak of second pulse
        p0a2 = np.max(wf2)
        # time position of second pulse (relative to reference)
        p0x2 = np.argmax(wf2)-peak1
        # put guesses into a list
        p0 = [p0a1,p0a2,p0x1,p0x2]

        # fit the curve (put small limit on number of function evaluations for speed)
        p = optimization.leastsq(optFunc, p0, args=(xdata, wf, singlePulse),maxfev=10)
      
        # update arrays based on current event
        a1Array = np.append(a1Array,p[0][0])
        a2Array = np.append(a2Array,p[0][1])
        x1Array = np.append(x1Array,p[0][2])
        x2Array = np.append(x2Array,p[0][3])

        if ((n1+1)%updateEvents == 0): # send mpi data object to master when desired
           
            # include fit to current trace to make sure fit looks good
            fit1 = evalFunc([p0a1,p0a2,p0x1,p0x2],xdata,singlePulse)
            md.addarray('wf',wf)
            md.addarray('fit',fit1)
            md.addarray('a1',a1Array)
            md.addarray('a2',a2Array)
            md.addarray('delay',np.abs(x1Array-x2Array)*.125)
            md.small.event = nevent
            md.send()
            
            # reset counter
            n1 = -1
            # reinitialize arrays
            a1Array = np.empty(0)
            a2Array = np.empty(0)
            x1Array = np.empty(0)
            x2Array = np.empty(0)


    md.endrun()	
