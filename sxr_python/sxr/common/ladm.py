#!/usr/bin/python
# This module provides support 
# for the SXR Large Area Detector Mover (LADM or LAM)
# for the SXR beamline (@LCLS)
# 
# Author:         Daniel Flath (SLAC)
# Created:        Aug 19, 2011
# Modifications:
#   Aug 19, 2011 DF
#       first version

import numpy as n
from numpy import rad2deg,arcsin,sqrt,tan
import sys
from utilities import estr
import pypsepics
from pypslog import logprint
from pvupdater import PVUpdater

alpha_r=63*n.pi/180
r=2960.0
R=6735.0

def ThetaToMotors(theta):
   theta=theta*n.pi/180
   x1=r*n.sin(theta)/(n.sin(alpha_r)*n.sin(alpha_r+theta))
   x2=R*n.sin(theta)/(n.sin(alpha_r)*n.sin(alpha_r+theta))
#   dz=x1*n.sin(alpha_r)/n.sin(theta)-r/n.sin(alpha_r)
   dz=r/n.sin(alpha_r)-x1*n.sin(alpha_r)/n.sin(theta)
   if theta==0:
     dz=0
   return x1,x2,dz

def x1ToTheta(x1):
   theta=n.arctan(x1*(n.sin(alpha_r))**2/(r-x1*n.sin(2*alpha_r)/2))
   theta=theta*180/n.pi
   return theta

def x2ToTheta(x2):
   theta=n.arctan(x2*(n.sin(alpha_r))**2/(R-x2*n.sin(2*alpha_r)/2))
   theta=theta*180/n.pi
   return theta

def xTox12(x):
   x12=x/n.sin(alpha_r)
   return x12
def xToz(x):
   z=x/n.tan(alpha_r)
   return z

def MotorsTox(x1,x2,z):
   x_x1=x1*n.sin(alpha_r)
   x_x2=x2*n.sin(alpha_r)
   x_z=z*n.tan(alpha_r)
   return x_x1,x_x2,x_z

    

def ThetaToMotors_print(theta):
    x1,x2,z = ThetaToMotors(theta)
    print 'move x1 to %+.4f' % x1
    print 'move x2 to %+.4f' % x2
    print 'move z  to %+.4f' % z


class LADM:
  """ Class to control the SXR LADM """

  def __init__(self,x1,y1,x2,y2,z):
    
    self.x1   = x1
    self.x2   = x2
    self.y1   = y1
    self.y2   = y2
    self.z    = z
    self.theta=None
    self.XT=None
    self.__lowlimX=None
    self.__hilimX=None
    self.motors = {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "z": z
        }
    self._theta_pv="SXR:VARS:LAM:Theta"
    self._gamma_pv="SXR:VARS:LAM:Gamma"
    pass

    """
    self.thetaUpdater = PVUpdater(self.waitAll, self.__writePVs)

  def __writePVs(self):
    pypsepics.put(self._theta_pv, self.wmTheta())
    pass
    """

  def __theta_movement(self,theta):
    x1,x2,z=ThetaToMotors(theta)
    z_now=self.z.wm()
    try:
       if z_now<z:
         print 'moving z to %+4.f' % z
         self.z.mv(z)
         self.z.wait()
         print 'moving x1 to %+4.f and x2 to %.4f\n' % (x1,x2)
         self.x1.mv(x1);self.x2.mv(x2)
         self.waitAll()
       else: 
         print 'moving x1 to %+4.f and x2 to %.4f\n' % (x1,x2)
         self.x1.mv(x1);self.x2.mv(x2)
         self.x1.wait();self.x2.wait()
         print 'moving z to %+4.f' % z
         self.z.mv(z)
         self.waitAll()
    except KeyboardInterrupt:
       self.stop()
    finally:
       pypsepics.put(self._theta_pv, self.wmTheta())
#       self.thetaUpdater.run()
#       print "done moving"

  def status(self):
    str  = estr("**LADM Status**\n " ,color="white",type="bold")
    str += "\t%10s\t%10s\t%10s\n" % ("Motor","User","Dial")
    str += "\t%10s\t%+10.4f\t%+10.4s\n" % ("theta",self.theta.wm(),"-")
    str += "\t%10s\t%+10.4f\t%+10.4s\n" % ("XT",self.XT.wm(),"-")
    keys = self.motors.keys()
    keys.sort()
    for key in keys:
       m = self.motors[key]
       str += "\t%10s\t%+10.4f\t%+10.4f\n" % (key,m.wm(),m.wm_dial())
    return str
  
  def ThetaToMotors_print(self,theta):
    x1,x2,z = ThetaToMotors(theta)
    print 'move x1 to %+.4f' % x1
    print 'move x2 to %+.4f' % x2
    print 'move  z to %+.4f' % z

  def moveTheta(self,theta):
    theta_now=self.theta.wm()
    if theta_now is n.nan:
      theta1=x1ToTheta(self.x1.wm())
      theta2=x2ToTheta(self.x2.wm())
      x1_th1,x2_th1,z_th1=ThetaToMotors(theta1)
      x1_th2,x2_th2,z_th2=ThetaToMotors(theta2)
      str= "theta(x1)= %.4f \n  Should move x2 to %.4f \n  Should move z to %.4f\n" % (theta1,x2_th1,z_th1)
      str+= "theta(x2)= %.4f \n  Should move x1 to %.4f \n  Should move z to %.4f\n\n" % (theta2,x1_th2,z_th2)
      str+=self.status()
      print str
    else:
       if abs(theta-theta_now)<=28:
          self.__theta_movement(theta)
       else:
          theta_1=(theta+theta_now)/2
          self.__theta_movement(theta_1)
          self.theta.wait()
          self.__theta_movement(theta)
  
  def waitAll(self):
     self.z.wait();self.x1.wait();self.x2.wait()

  def wmTheta(self):
     theta1=x1ToTheta(self.x1.wm())
     theta2=x2ToTheta(self.x2.wm())
     tolerance=.01
     if abs(theta1-theta2)<tolerance:
        return theta1
     else:
        return n.nan
  def setTheta(self,value):
    x1,x2,z=ThetaToMotors(value)
    self.x1.set(x1)
    self.x2.set(x2)
    self.z.set(z)
     
  def moveX(self,x):
    if ((x<=self.__lowlimX)or(x>=self.__hilimX)):
       logprint("Asked to move %s (pv %s) outside limit, aborting" % (self.XT.name,self.XT.pvname),print_screen=1)
    else:
      try:
          x1=xTox12(x)
          x2=xTox12(x)
          z=xToz(x)
          z_now=self.z.wm()
          if z>z_now:
             print 'moving z to %+4.f\n' % z
             self.z.mv(z)
             self.z.wait()
             print 'moving x1 to %+4.f and x2 to %.4f\n' % (x1,x2)
             self.x1.mv(x1);self.x2.mv(x2)
          else:
             print 'moving x1 to %+4.f and x2 to %.4f\n' % (x1,x2)
             self.x1.mv(x1);self.x2.mv(x2)
             self.x1.wait();self.x2.wait()
             print 'moving z to %+4.f\n' % z
             self.z.mv(z)
      except KeyboardInterrupt:
        self.stop()
  def wmX(self):
     x1=self.x1.wm()
     x2=self.x2.wm()
     z=self.z.wm()
     x_x1,x_x2,x_z=MotorsTox(x1,x2,z)
     db_x1=self.x1.get_par("retry_deadband")
     db_x2=self.x2.get_par("retry_deadband")
     tolerance=db_x1+db_x2
     if (abs(x_x1-x_x2)<=tolerance):
        z_theo=xToz(x_x1)
        db_z=self.z.get_par("retry_deadband")
        if abs(z-z_theo)<2*db_z:
          return x_x1
        else:
           return n.nan
     else:
        return n.nan
  def _setX(self,value):
    x1=xTox12(x)
    x2=xTox12(x)
    z=xToz(x)
    self.x1.set(x1)
    self.x2.set(x2)
    self.z.set(z)

  def _set_lowlimX(self,value):
     self.__lowlimX=value
  
  def _set_hilimX(self,value):
     self.__hilimX=value

  def _get_lowlimX(self):
     return self.__lowlimX
  
  def _get_hilimX(self):
     return self.__hilimX
  def stop(self):
     self.x1.stop()
     self.x2.stop()
     self.z.stop() 

  def __repr__(self):
    return self.status()
