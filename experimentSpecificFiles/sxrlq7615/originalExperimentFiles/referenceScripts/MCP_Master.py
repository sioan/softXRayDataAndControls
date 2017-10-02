from mpi4py import MPI
    
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
import time

from psmon import publish
import psmon.plots as psplt
from psmon.plots import XYPlot,Image,Hist
import h5py
import numpy as np
from mpidata import mpidata


def runmaster(nClients,pars,args):

    # get data source parameters
    expName = pars['expName']
    runNum = args.run
    runString = 'exp='+expName+':run='+runNum
    # get number of events between updates
    updateEvents = pars['updateEvents']
    # expected delay
    nomDelay = args.delay

    # plotting things
    plotFormat = 'ro'
    xdata = np.zeros(updateEvents)
    ydata = np.zeros(updateEvents)

    # initialize plots
    # plot for pulse 1 vs pulse 2 amplitude
    Amplitudes = XYPlot(0, "Amplitudes", xdata, ydata,
		formats=plotFormat,xlabel='Pulse 1 amplitude',
        ylabel='Pulse 2 amplitude')

    publish.send("AMPLITUDES",Amplitudes)

    # plot for MCP trace and fit
    x1 = np.linspace(0, 2500, 20000)
    y1 = np.zeros(20000)

    x1 = [x1[12500:13500],x1[12500:13500]]
    y1 = [y1[12500:13500],y1[12500:13500]+1]
    plotFormat = ['b-','r-']
    legend=['Raw','Fit']

    Trace = XYPlot(0, "Trace", x1, y1, formats=plotFormat,leg_label=legend, xlabel='Time (ns)', ylabel='MCP Signal')

    publish.send("TRACE",Trace)
    
    # histogram of delays based on fit (to make sure fit is working)
    DelayHist = Hist(0, "Delay", np.linspace(nomDelay-1.0, nomDelay+1.0, 101), np.zeros(100),xlabel='Delay (ns)',ylabel='Number of Events')
    publish.send("DELAYHIST",DelayHist)

    # initialize arrays for plotting
    wf = np.zeros(20000)
    fit1 = np.zeros(20000)
    a1 = np.empty(0)
    a2 = np.empty(0)
    delay = np.empty(0)


    # keep plotting until all clients stop
    while nClients > 0:
        # Remove client if the run ended
        #
        # set up data receiving
        md = mpidata()
        # check which client we're receiving from
        rank1 = md.recv()
        # check if this client is finished
        if md.small.endrun:
            nClients -= 1
        else:
            # add new data to arrays
            a1 = np.append(a1,md.a1) 
            a2 = np.append(a2,md.a2)
            delay = np.append(delay,md.delay)
            wf = md.wf
            fit1 = md.fit
            
            # plot if we're receiving from the last client
            if rank1 == size-1:
                # make histogram of delays
                hist1, bins = np.histogram(delay,bins=np.linspace(nomDelay-5,nomDelay+5,101))
                # update plots
                plot(Trace,x1,[wf[12500:13500],fit1[12500:13500]],md.small.event,"TRACE")
                plot(Amplitudes,a1,a2,md.small.event,"AMPLITUDES") 
                histPlot(DelayHist,bins,hist1,md.small.event,"DELAYHIST")
                # re-initialize arrays
                a1 = np.empty(0)
                a2 = np.empty(0)
                delay = np.empty(0)

# function for updating XYplots
def plot(plot1,xdata,ydata,nevent,plotName):
    plot1.xdata = xdata
    plot1.ydata = ydata
    plot1.ts = nevent
    publish.send(plotName, plot1) # send to the display

# function for updating histograms
def histPlot(plot1,bins,values,nevent,plotName):
    plot1.bins = bins
    plot1.values = values
    plot1.ts = nevent
    publish.send(plotName, plot1)
