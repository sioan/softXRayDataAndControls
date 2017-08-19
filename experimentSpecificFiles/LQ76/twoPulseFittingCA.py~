import numpy as np
import scipy.optimize as opt
import epics
import time

# load reference pulse
pulse = np.load('ben_single_mcp.npy')
pulse = np.pad(pulse,(500,500),'constant')
xd = np.arange(pulse.size)
xwf = np.arange(500)
rpeak = 518 # peak positionin reference

# Optimization func for fitting
def optfunc(p,wf):
    a1,x1,a2,x2 = p
    err = wf - a1*np.interp(xwf+rpeak-x1,xd,pulse) \
          - a2*np.interp(xwf+rpeak-x2,xd,pulse)
    return err

# Subtract 1st pulse from waveform
def subpulse(p,wf):
    a1,x1 = p
    return wf - a1*np.interp(xwf+rpeak-x1,xd,pulse)

# Sioan function to fit 2 pulse
def twoPulseFitting(wf):
    # Estimate initial fitting parameters
    t1 = np.argmax(wf)
    tempwf = subpulse((wf[t1],t1),wf)
    p0 = [wf[t1],t1,np.max(tempwf),np.argmax(tempwf)]

    # fit 2 pulse mcp trace
    pfit = opt.leastsq(optfunc,p0,args=wf,maxfev=100)[0]
    if pfit[1] > pfit[3]:
        pfit = np.concatenate([pfit[2:4],pfit[0:2]])

    return pfit

x = np.array([0,0,0,0])
while(True):
        time.sleep(.06)
        
    #try:
	y = 0+np.append(0,epics.caget("SXR:NOTE:ARRAY:01")[1:])
        #print str(max(y))
        x = 0.95*x + 0.05*twoPulseFitting(y)
        epics.caput("SXR:MCP:FIRST:AMPLITUDE",x[0])
	epics.caput("SXR:MCP:SECOND:AMPLITUDE",x[2])
	epics.caput("SXR:MCP:FIRST:DELAY",(x[3]-x[1])*0.125)
	#epics.caput("SXR:MCP:SECOND:DELAY",x[3]*0.125)

    #except:
        #break
