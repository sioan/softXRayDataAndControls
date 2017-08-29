#!/usr/bin/python
# This module provides support 
# for the XPP CCM monochromator
# for the XPP beamline (@LCLS)
# 
# Author:         Marco Cammarata (SLAC)
# Created:        Aug 27, 2010
# Modifications:
#   Aug 27, 2010 MC
#       first version

import numpy as n
import sys
from utilities import estr
import pypsepics
from pypslog import logprint

gR = 3.175
#    self.__D = 232.15
#    self.__theta0 = 15.05
gD = 231.303
#    gTheta0 = 15.08219; # original calibration
gTheta0 = 15.18219; # calibration for split and delay
gSi111dspacing = 3.13556044

def thetaToAlio(theta):
  t_rad = (theta-gTheta0)*n.pi/180.
  x = gR*(1/n.cos(t_rad)-1)+gD*n.tan(t_rad)
  return x

def alioToTheta(alio):
  return gTheta0 + 180/n.pi*2*n.arctan( (n.sqrt(alio**2+gD**2+2*gR*alio)-gD) / (2*gR+alio) )

def thetaToWavelenght(theta):
  return 2*gSi111dspacing*n.sin(theta/180*n.pi)

def wavelenghtToTheta(wavelenght):
  return 180./n.pi*n.arcsin(wavelenght/2/gSi111dspacing )

def alioToWavelenght(alio):
  theta = alioToTheta(alio)
  return thetaToWavelenght(theta)

def alioToE(alio):
  l = alioToWavelenght(alio)
  return wavelenghtToE(l)

def wavelenghtToE(wavelenght):
  return 12.39842/wavelenght

def EToWavelenght(E):
  return 12.39842/E

def EToAlio(E):
  l = EToWavelenght(E)
  t = wavelenghtToTheta(l)
  alio = thetaToAlio(t)
  return alio

class CCM:
  """ Class to control the XPP PIM """
  def __init__(self,x1,x2,y1,y2,y3,alio,t2coarse,t2fine,chi2):
    self.x1   = x1
    self.x2   = x2
    self.y1   = y1
    self.y2   = y2
    self.y3   = y3
    self.alio = alio
    self.theta2fine = t2fine
    self.theta2coarse = t2coarse
    self.chi2 = chi2
    self.__inpos=dict()
    self.__inpos["x1"]=-8.92
    self.__inpos["x2"]=-8.92
    self.__inpos["y1"]=0
    self.__inpos["y2"]=0
    self.__inpos["y3"]=0
    self.__outpos=dict()
    self.__outpos["x1"]=0
    self.__outpos["x2"]=0
    self.__outpos["y1"]=0
    self.__outpos["y2"]=0
    self.__outpos["y3"]=0
#    self.__wmccm()

  def movey(self,pos):
#    myprint("moving x1,x2 to %f,%f" % (x1,x2))
#    myprint("moving y1,y2,y3 to %f,%f" % (y1,y2,y3))
    self.y1.move(pos); self.y2.move(pos); self.y3.move(pos)

  def movex(self,pos):
#    myprint("moving x1,x2 to %f,%f" % (x1,x2))
#    myprint("moving y1,y2,y3 to %f,%f" % (y1,y2,y3))
    self.x1.move(pos); self.x2.move(pos);

  def monoin(self):
    x1=self.__inpos["x1"];
    x2=self.__inpos["x2"];
    y1=self.__inpos["y1"];
    y2=self.__inpos["y2"];
    y3=self.__inpos["y3"];
#    myprint("moving x1,x2 to %f,%f" % (x1,x2))
    self.x1.move(x1); self.x2.move(x2)
    self.x1.wait(); self.x2.wait()
#    myprint("moving y1,y2,y3 to %f,%f" % (y1,y2,y3))
# commented by David
#    self.y1.move(y1); self.y2.move(y2); self.y3.move(y3)

  def monoout(self):
    x1=self.__outpos["x1"];
    x2=self.__outpos["x2"];
    y1=self.__outpos["y1"];
    y2=self.__outpos["y2"];
    y3=self.__outpos["y3"];
#    myprint("moving y1,y2,y3 to %f,%f" % (y1,y2,y3))
# commented by David
#    self.y1.move(y1); self.y2.move(y2); self.y3.move(y3)
#    self.y1.wait(); self.y2.wait(); self.y3.wait()
#    myprint("moving x1,x2 to %f,%f" % (x1,x2))
    self.x1.move(x1); self.x2.move(x2)

  def alioWait(self):
   pass

  def wait(self):
    """ Returns when x1,x2,y1,y2,y3 are not moving """
    self.y1.wait(); self.y2.wait(); self.y3.wait()
    self.x1.wait(); self.x2.wait()
    self.alioWait()


  def moveE(self,E):
    """ E in keV """
    if (E>2000):
      E=E/1e3
    alio = EToAlio(E)
    self.alio.move(alio)

  def __wmccm(self):
    x=self.alio.wm(); 
    self.theta = alioToTheta(x)
    self.wavelenght =thetaToWavelenght(self.theta)
    self.E = wavelenghtToE(self.wavelenght)
    self.resolution = (alioToE(x-1e-4)-alioToE(x))/1e-4
    self.__x1pos = self.x1.wm()
    self.__x2pos = self.x2.wm()
    self.__y1pos = self.y1.wm()
    self.__y2pos = self.y2.wm()
    self.__y3pos = self.y3.wm()

  def wmE(self):
   """ returns the energy in keV"""
   self.__wmccm()
   return self.E

  def isin(self):
    pass

  def status(self):
    self.__wmccm()
    x1= self.__x1pos; x2= self.__x2pos;
    y1= self.__y1pos; y2= self.__y2pos; y3= self.__y3pos
    str  = "alio   (mm): %.4f\n" % self.alio.wm()
    str += "angle (deg): %.3f\n" % self.theta
    str += "lambda  (A): %.4f\n" % self.wavelenght
    str += "Energy (keV): %.4f\n" % self.E
    str += "res (eV/mm): %.1f\n" % (self.resolution*1e3)
    str += "res (eV/um): %.2f\n" % (self.resolution)
    str += "x @ (mm): %.3f [x1,x2=%.3f,%.3f]\n" % ((x1+x2)/2,x1,x2)
    str += "y @ (mm): %.3f [y1,y2,y3=%.3f,%.3f,%.3f]\n" % ((y1+y2+y3)/3,y1,y2,y3)
    return str

  def Escan(self,Emin,Emax,steps,events_per_point,settling_time,*dets):
    from Daq import xppdaq as xppdaq
    pos = []
    if ( (Emin<2000) & (Emax<2000) ):
      Emin=Emin*1e3
      Emax=Emax*1e3
    for cycle in range(steps+1):
      E= (Emax-Emin)*cycle/float(steps) + Emin
      alio = EToAlio(E)
      pos.append( alio )
    dets = xppdaq._Daq__check_dets(dets)
    xppdaq._Daq__ascan(self.alio,pos,events_per_point,settling_time,dets)

  def __repr__(self):
    return self.status()
