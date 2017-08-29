import config
from utilities import estr
import pypsepics
from time import time,sleep

class RefLaser:
  def __init__(self,mirror,x,y,rx,ry):
    self.m=mirror
    self.x=x
    self.y=y
    self.rx=rx
    self.ry=ry
    self._inpos=55
    self._outpos=0
  def set_inpos(self,pos):
     self._inpos=pos
  def set_outpos(self,pos):
     self._outpos=pos
  def movein(self):
    self.m.move(self._inpos)

  def moveout(self):
    self.m.move(self._outpos)

  def wait(self):
    self.m.wait()

  def isin(self,pos=None):
    if pos is None:
      pos = self.m.wm()
    return ( abs(pos-self._inpos)<0.3 )

  def isout(self,pos=None):
    if pos is None:
      pos = self.m.wm()
    return ( abs(pos-self._outpos)<0.3 )

  def status(self):
    pos = self.m.wm()
    if self.isin(pos):
      pos_str =  estr("IN",color="red")
    elif self.isout(pos):
      pos_str =  estr("OUT",color="green")
    else:
      pos_str = estr("UNKOWN",color="red")
    str = "Ref laser position is : %s (stage at %.3f mm)\n" % (pos_str,pos)
    str+='pico motors positions: \n'
    str+='x = %+.4f\n' % self.x.wm()
    str+='y = %+.4f\n' % self.y.wm()
    str+='rx = %+.4f\n' % self.rx.wm()
    str+='ry = %+.4f\n' % self.ry.wm()
    return str

  def __repr__(self):
    return self.status()
