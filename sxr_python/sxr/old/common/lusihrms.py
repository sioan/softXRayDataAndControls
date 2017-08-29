from numpy import tan,pi
from periodictable import xsf

class HRMS:
  def __init__(self,m1r,m1y,m2r,m2y,linac):
    self.distance = 530.
    self.angle = None
    self.m1r=m1r
    self.m1y=m1y
    self.m2r=m2r
    self.m2y=m2y
    self.linac = linac

  def get_angle(self):
    return (self.m1r.wm()+self.m2r.wm())/2.

  def calc_offset(self,angle):
    """ calculate beam vertical offset, angle in deg """
    return -tan(2*angle/180.*pi)*self.distance

  def move(self,angle):
    self.angle=angle
    self.m1r.move(angle)
    self.m2r.move(angle)
    self.m1y.move(0)
    offset = self.calc_offset(angle)
    m2y.move(offset)
    print "beam offset %.3f" % offset

  def status(self):
    angle=self.angle=self.get_angle()
    E=self.E=self.linac.getXrayeV()
    out  = "Harmonic Rejection Mirrors (HRMS)\n"
    out += "Angle       = %.3f deg (=%.3f mrad)\n" % (angle,angle/180.*3.14*1e3)
    out += "Beam offset = %.3f mm\n" % (self.calc_offset(angle))
    out += "Beam energy = %.3f keV\n" % (self.E/1e3)
    out += "R(1st harm) = %.3e\n"    % self.getTforE(energy=E)
    out += "R(3rd harm) = %.3e\n"    % self.getTforE(energy=3*E)
    return out

  def getTforE(self,angle=None,energy=None):
    if (energy is None): energy=self.linac.getXrayeV()
    if (angle is None):
      if (self.angle is None): self.angle=self.get_angle()
      angle=self.angle
    r = xsf.mirror_reflectivity("Si",angle=angle,energy=energy/1e3)
    # r**2 because 2 mirrors
    return float(r*r)
    return r*r

  def __repr__(self):
    return self.status()
