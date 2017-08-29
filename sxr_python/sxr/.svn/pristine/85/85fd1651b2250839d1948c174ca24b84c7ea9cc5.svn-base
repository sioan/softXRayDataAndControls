import minuit2
import numpy as np
import PeakAnalysis
from scipy.special import erf

sqrt2  = np.sqrt(2)
sqrtpi = np.sqrt(np.pi)
datax  = np.ones(1)
datay  = np.ones(1)
datae  = np.ones(1)


def gaussnorm(x,x0,sigma):
  return 1/sqrt2/sqrtpi/sigma*np.exp( -(x-x0)**2/2./sigma**2 )

def gauss(x,x0,sigma):
  return np.exp( -(x-x0)**2/2./sigma**2 )

def myexp(x,t0,tau):
  v=np.empty_like(x)
  f1=(x>t0)
  v[f1]=(1-np.exp(-(x[f1]-t0)/tau))
  f2=(x<=t0)
  v[f2] = 0
  return v

def conv_gauss_and_const(x,sig):
  return 0.5*(1-erf(-x/sqrt2/sig))

def conv_gauss_and_exp(x,sig,tau):
  return 0.5*exp(-(2*tau*x-sig**2)/2/tau**2)*(1-erf( (-tau*x+sig**2)/sqrt2/tau/sig))

def chi2gauss(a,x0,sigma,c):
  fit  = a*gauss(datax,x0,sigma)+c
  chi2 = (datay-fit)/datae
  return np.sum(chi2*chi2)
  
def fitgauss(x,y,e,a_init=None,x0_init=None,sigma_init=None,c_init=None):
  n_bkg = 3
  g = globals()
  g["datax"] = x; g["datay"] = y; g["datae"] = e
  (x0_guess,fwhm_guess,peak_guess)=PeakAnalysis.PeakAnalysis(x,y,nb=n_bkg)
  if (x0_init is None):    x0_init=x0_guess
  if (sigma_init is None): sigma_init=fwhm_guess/2.35
  if (c_init is None):     c_init = ( y[0:n_bkg].mean()+y[-1-n_bkg:-1].mean() ) /2.
  if (a_init is None):     a_init= (y-c_init).max()
  print x0_init,sigma_init,c_init,a_init
  m = minuit2.Minuit2(chi2gauss,a=a_init,x0=x0_init,sigma=sigma_init,c=c_init)
  m.printMode=1
  m.migrad()
  fit_par = m.values
  fit_err = m.errors
  fit = fit_par["a"]*gauss(x,fit_par["x0"],fit_par["sigma"])+fit_par["c"]
  return (fit_par,fit_err,x,fit)
