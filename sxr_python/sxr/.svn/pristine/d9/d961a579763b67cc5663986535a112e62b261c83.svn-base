""" Utilities to perfrom various calculations """

import numpy as n
import scipy as s
import xraylib
import periodictable
from matplotlib.pyplot import *
from matplotlib.mlab import find
from utilitiesCalc import *
from utilitiesLaser import *
from scipy import interpolate
import time

def FreqSpec(cWave,BW):
  """Returns a Gaussian frequency spectrum
     cWave is the center wavelength in nm
     BW is the FWHM bandwidth in nm
  """
  cFreq=lam2f(cWave)
  FreqLow=lam2f(cWave+BW/2.0)
  FreqHigh=lam2f(cWave-BW/2.0)
  FW=FreqHigh-FreqLow
  Sigma=FW/2.3548
  N=n.round(n.log(100001)/n.log(2))   #argument in first log needs to be very large for large chirps
  Freq=n.linspace(0,10e15,2**N)        # frequency axis
  Spectrum=n.exp(-(Freq-cFreq)**2/(2*Sigma**2))
  M=[Freq,Spectrum]
  return M

def Dispersion(cWavelength,BW,Mat=None,MatL=None):
  """Plots the material dispersed laser temporal properties
     Gaussian spectral shape is assumed
     cWavelength is the center wavelength in m
     BW is the FWHM laser bandwidth in m
     Mat is the material list ( 'BK7' or ['BK7','FS'] )
     MatL is the material length in m ( 5e-3 or [5e-3,10e-3] )
  """
  tic=time.time()
  if type(Mat) is not list:
    Mat=[Mat]
  if type(MatL) is not list:
    MatL=[MatL]
  Spectrum=FreqSpec(cWavelength,BW)
  #####  Plot Spectrum   ####
  ii=find(Spectrum[1]>0.0002)
  fmin=Spectrum[0][min(ii)]*u['THz']
  fmax=Spectrum[0][max(ii)]*u['THz']
  l=cWavelength*u['nm']
  bw=BW*u['nm']
  tstr="%3.1f nm Center Wavelength, %3.1f nm Bandwidth" % (l,bw)
  fig=figure(10,figsize=(12,8))
  clf()

  subplot(221)
  plot(Spectrum[0]*u['THz'],Spectrum[1],'b.-')
  ax=fig.add_subplot(221)
  ylabel('Intensity (a.u.)')
  xlabel('Frequency (THz)')
  title(tstr)
  xlim(fmin,fmax)
  ylim(-0.02,1.05)
  grid(True)

  Tlimit=TransformSpectrum(Spectrum)

  #thresh=0.000001
  #peak=[]
  #for i in n.arange(1, len(Tlimit[1]-1)):
  #  if Tlimit[1][i]-Tlimit[1][i-1]>thresh and Tlimit[1][i]-Tlimit[1][i+1]>thresh:
  #    peak.append(i)
  #ftime=n.linspace(min(Tlimit[0][peak]),max(Tlimit[0][peak]),100*len(peak))
  #Envelope=s.interpolate.spline(Tlimit[0][peak],Tlimit[1][peak],ftime)
  #Cross=find(Envelope>=0.5)
  #FWHM=(ftime[Cross[-1]]-ftime[Cross[0]])*u['fs']
  
  Cross=find(Tlimit[1]>=0.5)
  FWHM=(Tlimit[0][Cross[-1]]-Tlimit[0][Cross[0]])*u['fs']
  ##### Plot Tranform Limit   #####
  iii=find(Tlimit[1]>0.0025)
  tmin=Tlimit[0][min(iii)]*u['fs']
  tmax=Tlimit[0][max(iii)]*u['fs']
  subplot(222)
  plot(Tlimit[0]*u['fs'],Tlimit[1],'b.-')#,ftime*u['fs'],Envelope,'r')
  ax=fig.add_subplot(222)
  ylabel('Intensity (a.u.)')
  xlabel('Time (fs)')
  title('Transform Limit')
  xlim(tmin,tmax)
  ylim(-0.02,1.05)
  text(0.05,0.92,'FWHM $\sim$ %3.1f fs' %FWHM, transform=ax.transAxes,bbox={'facecolor':'white','pad':15})
  grid(True)

  ##### Now compute material phase  ######
  cFreq=lam2f(cWavelength)
  Phase0=MatPhase(Mat,MatL,cFreq)

  Phase=n.zeros(len(Spectrum[0]))
  Phase[ii]=MatPhase(Mat,MatL,Spectrum[0][ii])

  ##### Fit the material phase to a polynomial  ####
  pFit=n.polyfit(Spectrum[0][ii]-cFreq,Phase[ii]-Phase0,4)
  GD=pFit[3]/(2*n.pi)*u['ps']
  GDD=2*pFit[2]/(2*n.pi)**2*u['fs']**2
  TOD=6*pFit[1]/(2*n.pi)**3*u['fs']**3
  FOD=24*pFit[0]/(2*n.pi)**4*u['fs']**4
  dGD=GD-sum(MatL)/c['c']*u['ps']


  MatLmm=s.array(MatL)*u['mm']
  MatStr=''
  MatLStr=''
  for el in Mat:
    MatStr+='%s, ' %el
  for el in MatLmm:
    MatLStr+='%3.2f, ' %el
  DispString= 'Material = %s\n' % MatStr
  DispString+= 'Material Length (mm) = %s\n' % MatLStr
  DispString+= '        Delta Group Delay = %3.2f ps\n' % dGD
  DispString+='Group Delay Dispersion = %3.0f fs$^2$\n' % GDD
  DispString+=' Third Order Dispersion = %3.0f fs$^3$\n' % TOD
  DispString+=' Forth Order Dispersion = %3.0f fs$^4$\n' % FOD
  figtext(0.05,0.1,DispString,size='large',linespacing=2)
  
  #Subtract the linear and constant phase term
  Phase[ii]=Phase[ii]-Phase0-pFit[3]*Spectrum[0][ii]

  Chirp=TransformSpectrum(Spectrum,Phase)

  
  Cross=find(Chirp[1]>=0.5)
  FWHM=(Chirp[0][Cross[-1]]-Chirp[0][Cross[0]])*u['fs']
  ##### Plot Tranform Limit   #####
  iii=find(Chirp[1]>0.01)
  tmin=Chirp[0][min(iii)]*u['fs']
  tmax=Chirp[0][max(iii)]*u['fs']
 

  ### Plot chirped beam   #####
  subplot(224)
  plot(Chirp[0]*u['fs'],Chirp[1],'b.-')#,ftime*u['fs'],Envelope,'r')
  ax=fig.add_subplot(224)
  ylabel('Intensity (a.u.)')
  xlabel('Time (fs)')
  title('Dispersed Profile')
  xlim(tmin,tmax)
  ylim(-0.02,1.05)
  text(0.05,0.92,'FWHM $\sim$ %3.1f fs' %FWHM, transform=ax.transAxes,bbox={'facecolor':'white','pad':15})
  grid(True)

  tight_layout()

 
def TransformSpectrum(Spectrum,Phase=None):
  AmplitudeSpec=n.array(n.sqrt(Spectrum[1]))
  mAmplitudeSpec=n.flipud(AmplitudeSpec[1:])
  mirror_AmplitudeSpectrum=n.concatenate((mAmplitudeSpec,AmplitudeSpec),1)
  if Phase==None:
    mirror_Phase=0
  else:
    mPhase=n.flipud(-Phase[1:])
    mirror_Phase=n.concatenate((mPhase,Phase),1)
  t_pulse=n.fft.fftshift(n.fft.ifft(n.fft.fftshift(mirror_AmplitudeSpectrum*n.exp(-mirror_Phase*1j))))
  t_pulse=t_pulse/max(t_pulse) #normalize
  t_power=n.abs(t_pulse)**2
  dt=1/(2*max(Spectrum[0]))
  Time=n.arange(0,len(t_pulse))*dt-len(t_pulse)*0.5*dt
  M=[Time,t_power]
  return M

def MatPhase(Mat,MatL,Freq):
  lam=f2lam(Freq)
  try:
    len(Freq)
    Phase=n.zeros(len(Freq))
  except:
    Phase=0
  if Mat[0]==None:
    return Phase
  for i in n.arange(len(Mat)):
    oi=OpticalIndex(Mat[i],lam)
    Phase+=oi*Freq*2*n.pi*MatL[i]/c['c']
  return Phase


