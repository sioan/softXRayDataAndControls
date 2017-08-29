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

alpha_r=63*n.pi/180
r=2960.0
R=6735.0
def ThetaToMotors(theta):
   theta=theta*n.pi/180
   x1=r*n.sin(theta)/(n.sin(alpha_r)*n.sin(alpha_r+theta))
   x2=R*n.sin(theta)/(n.sin(alpha_r)*n.sin(alpha_r+theta))
   dz=x1*n.sin(alpha_r)/n.sin(theta)-r/n.sin(alpha_r)
   return x1,x2,dz

def x1ToTheta(x1):
   theta=n.arctan(x1*(n.sin(alpha_r))**2/(r-x1*n.sin(2*alpha_r)/2))
   theta=theta*180/n.pi
   return theta

def x2ToTheta(x2):
   theta=n.arctan(x2*(n.sin(alpha_r))**2/(R-x2*n.sin(2*alpha_r)/2))
   theta=theta*180/n.pi
   return theta

def ThetaToMotors_print(theta):
    x1,x2,z = ThetaToMotors(theta)
    print 'move x1 to %+.4f' % x1
    print 'move x2 to %+.4f' % x2
    print 'move relative z by %+.4f' % z

class LADM:
  """ Class to control the SXR LADM """

  def __init__(self,x,y):
    
    self.x   = x
    self.y   = y

  def status(self):
    str = "** LADM Status **\n"
    str +="theta:\n%s\n" % self.theta.wm()
    str += "\t(x1, x2, y1, y2, z) [user]: %+.4f, %+.4f, %+.4f, %+.4f, %+.4f\n" % (self.x1.wm(),self.x2.wm(),self.y1.wm(),self.y2.wm(),self.z.wm())
    str += "\t(x1, x2, y1, y2, z) [dial]: %+.4f, %+.4f, %+.4f, %+.4f, %+.4f\n" % (self.x1.wm_dial(),self.x2.wm_dial(),self.y1.wm_dial(),self.y2.wm_dial(),self.z.wm_dial())
    return str
  
  def ThetaToMotors_print(self,theta):
    x1,x2,z = ThetaToMotors(theta)
    print 'move x1 to %+.4f' % x1
    print 'move x2 to %+.4f' % x2
    print 'move relative z by %+.4f' % z

  def moveTheta(self,theta):
    x1,x2,z=ThetaToMotors(theta)
    self.x1.mv(x1);self.x2.mv(x2);self.z.mv(z)

  def wmTheta(self):
     theta1=x1ToTheta(self.x1.wm())
     theta2=x2ToTheta(self.x2.wm())
     str= "according to x1 %+.4f\n" % theta1
     str+="according to x2 %+.4f" % theta2
     return str


  def __repr__(self):
    return self.status()
