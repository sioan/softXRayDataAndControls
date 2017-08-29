printnow("loading sxr motors..."),
import sxrmotors

printnow("loading goniometer...")
import goniometer
import EnergyAnalyzer

diff = goniometer.Goniometer(
  sxrmotors.gon_x,
  sxrmotors.gon_y,
  sxrmotors.gon_theta,
  sxrmotors.gon_2theta,
  sxrmotors.gon_chi,
  sxrmotors.gon_phi,
  sxrmotors.gon_sx,
  sxrmotors.gon_sy,
  sxrmotors.gon_sz,
  sxrmotors.gon_dy,
  sxrmotors.gon_gamma,
  "diff",
  "SXR:VARS"
  )

ea = EnergyAnalyzer.EnergyAnalyzer(
  sxrmotors.ea_thC,
  sxrmotors.ea_th2D,
  "En",
  "SXR:VARS"
  )

# Diffractometer detector 2phi rotation virtual motor
diffDetPhi = virtualmotor.VirtualMotor(sxrmotors,"diffDetPhi",diff.moveDetPhi,diff.wmDetPhi,diff.waitDetPhi,get_hilim=diff.getHiLimDetPhi,get_lowlim=diff.getLowLimDetPhi)
diff.reflectdet = diffDetPhi

# Diffractometer sample-phi/detector-2phi rotation virtual motor
diffDSPhi = virtualmotor.VirtualMotor(sxrmotors,"diffDSPhi",diff.moveDSPhi,diff.wmDSPhi,diff.waitDSPhi,get_hilim=diff.getHiLimDSPhi,get_lowlim=diff.getLowLimDSPhi)
diff.reflect = diffDSPhi

# Energy Analyzer Theta-2Theta
En = virtualmotor.VirtualMotor(sxrmotors,"En",ea.moveEn,ea.wmEn,ea.waitEn,get_hilim=ea.getHiLimEn,get_lowlim=ea.getLowLimEn)
