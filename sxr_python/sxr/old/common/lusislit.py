import numpy
import sys

class LusiSlit:
  """ Class to control the lusislit
      each slit object is defined by passing the four motor it is connected to.
      (up,down,north,south) plus an optional mnemonic name.
      The 4 motors are combined to provide an offset and gap.
      hg = N-S; ho = (N+S)/2
      vg = U-D; vo = (U+D)/2
      for each [hg,ho,vg,vo] methods are provided to retrieve the value (wm_*)
      move to a given value (mv_*) and set the current position as new value (set_*)
  """
  def __init__(self,u,d,n,s,name=""):
      self.u = u
      self.d = d
      self.n = n
      self.l = n
      self.s = s
      self.r = s
      self.hg = None
      self.vg = None
      self.ho = None
      self.vo = None
      self.upos = self.dpos = self.spos = self.npos = numpy.nan
      self.__name = name

  def __call__(self,hg,vg):
    self.mv_hg(hg)
    self.mv_vg(vg)

  def __repr__(self):
    return self.status()

#  def __getattr__(self,name):
#    if (name == "ho"):
#        return self.__wm_ho()
#    elif (name == "hg"):
#        return self.__wm_hg()
#    elif (name == "vo"):
#        return self.__wm_vo()
#    elif (name == "vg"):
#        return self.__wm_vg()
#    else:
#        return "the attribute '%s' does not exist" % (name)

  def __update(self):
    self.npos = self.n.wm()
    self.spos = self.s.wm()
    self.upos = self.u.wm()
    self.dpos = self.d.wm()

  def status(self):
    self.__update()
    out = "slit %s: (hg,vg) = (%+.4f x %+.4f); (ho,vo) = (%+.4f,%+.4f)" % (self.__name,\
          self.wm_hg(fast=True),self.wm_vg(fast=True),\
          self.wm_ho(fast=True),self.wm_vo(fast=True) )
    return out

  def wm_ho(self,fast=False):
    if (not fast):  self.__update()
    return (self.npos+self.spos)/2
  def wm_hg(self,fast=False):
    if (not fast):  self.__update()
    return (self.npos-self.spos)
  def wm_vo(self,fast=False):
    if (not fast):  self.__update()
    return (self.upos+self.dpos)/2
  def wm_vg(self,fast=False):
    if (not fast):  self.__update()
    return (self.upos-self.dpos)

  def mv_ho(self,offset=0):
    gap = self.wm_hg()
    if (numpy.isnan(gap)):
      print "Problem in getting the current horizontal gap, stopping"
    else:
      self.s.move(offset-gap/2)
      self.n.move(offset+gap/2)

  def set_ho(self,newoffset=0):
    gap = self.wm_hg()
    if (numpy.isnan(gap)):
      print "Problem in getting the current horizontal gap, stopping"
    else:
      self.s.set(newoffset-gap/2)
      self.n.set(newoffset+gap/2)

  def mv_vo(self,offset=0):
    gap = self.wm_vg()
    if (numpy.isnan(gap)):
      print "Problem in getting the current vertical gap, stopping"
    else:
      self.u.move(offset+gap/2)
      self.d.move(offset-gap/2)

  def set_vo(self,newoffset=0):
    gap = self.wm_vg()
    if (numpy.isnan(gap)):
      print "Problem in getting the current vertical gap, stopping"
    else:
      self.d.set(newoffset-gap/2)
      self.u.set(newoffset+gap/2)

  def mv_hg(self,gap=None):
    if (gap is None):
        return
    gap = float(gap)
    offset = self.wm_ho()
    if (numpy.isnan(offset)):
      print "Problem in getting the current horizontal offset position, stopping"
    else:
      self.s.move(offset-gap/2)
      self.n.move(offset+gap/2)

  def set_hg(self,newgap=0):
    newgap = float(newgap)
    offset = self.wm_ho()
    if (numpy.isnan(offset)):
      print "Problem in getting the current horizontal offset position, stopping"
    else:
      self.s.set(offset-newgap/2)
      self.n.set(offset+newgap/2)

  def mv_vg(self,gap=None):
    if (gap is None):
        return
    gap = float(gap)
    offset = self.wm_vo()
    if (numpy.isnan(offset)):
      print "Problem in getting the current vertical offset position, stopping"
    else:
      self.d.move(offset-gap/2)
      self.u.move(offset+gap/2)

  def set_vg(self,newgap=0):
    newgap = float(newgap)
    offset = self.wm_vo()
    if (numpy.isnan(offset)):
      print "Problem in getting the current vertical offset position, stopping"
    else:
      self.d.set(offset-newgap/2)
      self.u.set(offset+newgap/2)

  def wait(self):
    self.d.wait()
    self.u.wait()
    self.s.wait()
    self.n.wait()

  def waith(self):
    self.s.wait()
    self.n.wait()

  def waitv(self):
    self.d.wait()
    self.u.wait()
