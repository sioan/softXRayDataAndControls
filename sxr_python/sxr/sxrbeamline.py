#! /usr/bin/env ipython 
#-nobanner
#import simpleMotor
#
#
import sys
import os
from common.utilities import printnow
printnow("Defining logfile..."),
from common.pypslog import logprint as sxrpythonlogprint
printnow(" done\n")

def mv(motor,pos):
  motor.mv(pos)

def mvr(motor,dist):
  motor.mvr(dist)



DAQ_PLATFORM=1

PYPS_INTERACTIVE = os.getenv('PYPS_INTERACTIVE',"FALSE").lower()=='true'

printnow("Loading grabber..."),
sxrElog = None
from common import pypsElog
if PYPS_INTERACTIVE:
  sxrElog = pypsElog.pypsElog()
else:
  print "WARNING: non-interactive mode.  NOT Loading grabber."
from common import config
config.Elog = sxrElog
printnow(" done\n")




#try:
#  printnow("Loading linac variables..."),
#  from common import linac
#  lcls_linac = linac.Linac()
#except:
#  printnow("\nWARNING: Problem, skipping!\n")
#finally:
#  printnow(" done\n")


# ====================  COMMENTED OUT FOR NOW ====================

# ==> REINCLUDE ONCE CUSTOMISED FOR SXR  

#printnow("Loading sxr motors..."),
#import sxrmotors
#sxrmotors = sxrmotors.SXRMotors()
#printnow(" done\n")

printnow("Loading sxr TEST motors..."),
import testsxrmotors
sxrmotors = testsxrmotors.SXRMotors()
printnow(" done\n")


ccm_111_offset = 7.55
ccm_511_offset = 5.3
ccm_offset = ccm_511_offset


def dumpMotors(fname=None):
  from common.motor import Motor as psmotor
  fields  = []

  def addField(n, f="%.6f", s="."):
    fields.append((n,f,s))
    pass
  
  addField("DESC","'%s'")
  addField("EGU","'%s'")
  addField("RBV")
  addField("LLM")
  addField("HLM")
  addField("OFF")
  addField("DIR","%d")
  addField("S")
  addField("SBAS")
  addField("SMAX")
  addField("ACCL")
  addField("SBAK")
  addField("BACC")
  addField("DRBV")
  addField("LDVL")
  addField("DLLM")
  addField("DHLM")
  addField("ERES")
  addField("MRES")
  addField("SREV")
  addField("UREV")
  addField("RDBD")
  addField("RC","%s",s=":")
  addField("HC","%s",s=":")
  addField("UEIP","%d")
  addField("STAT","'%s'")
  addField("RRBV")
  addField("REP")
  
  def getMotorAttr(m, attr, sep="."):
    val = None
    try:
      val = m.get_pv(attr, sep)
    finally:
      return val
    pass

  writefile = False
  dumpfile = None
  if (fname is not None):
    dumpfile = open(fname,'w')
    writefile = True
    pass
    
  def doprint(str):
    print str
    if (writefile):
      dumpfile.write("%s\n" % (str))
      pass
    pass

  allMotors = []
  d = sxrmotors.__dict__
  for k in d.keys():
    if (isinstance(d[k], psmotor)):
      allMotors.append(k)
      pass
    pass
  allMotors.sort()
  for n in allMotors:
    m = d[n]
    doprint("\n%s\t'%s'" % ("Motor", n))
    for f in fields:
      v = getMotorAttr(m, f[0], f[2])
      if (v is None):
        doprint("%s\tUnknown" % (f[0]))
        pass
      else:
        format = "%s\t" + f[1]
        doprint(format % (f[0], v))
        pass
      #      pos = getMotorAttr(m, 'readback')
      #      print "%20s\t%10.3f\n" % (n, pos)
      #    except Exception, e:
      #      print "%20s\t%s\n" % (n, "unable to query motor")
      #      raise e
      pass
    pass
  if (writefile):
    dumpfile.close()
    pass
  pass
pass



# sxrdetectors COMMENTED OUT UNTIL CUSTOMISED FOR SXR
# ====> FOCUSSED ON JUST IPIMBS ---> LEAVE COMMENTED OUT FOR NOW
#printnow("Loading sxr detectors...\n")
#import sxrdetectors
#d = sxrdetectors = sxrdetectors.SXRDetectors()
#printnow("Loading sxr detectors... done\n")



# ====> SET UP FOR SOLID ATTENUATORS.  SXR RELY ON GAS ATTENUATOR
# WHICH IS JUST A PV TO SET GAS PRESSURE, READ OUT GAS PRESSURE, AND
# READ OUT ATTENUATION.  COULD COME UP WITH CUSTOM CLASS THAT TAKES
# ATTENUATION AND SETS THE APPROPIATE GAS PRESSURE.  
# common.lusiatt COMMENTED OUT. MAY NOT BE NEEDED FOR SXR
#printnow("Loading sxr attenuators...\n")
#try:
#  from common import lusiatt
#  sxratt = lusiatt.Lusiatt(sxrmotors.filt,lcls_linac,"SXR:VARS",4.0)
#  from common import virtualmotor
#  virtualmotor.VirtualMotor(sxrmotors,"SiT",sxratt.setTfast,sxratt.getTvalue,sxratt.wait)
#except:
#  printnow("\nWARNING: Problem, skipping!\n")  
#finally:
#  printnow("Loading sxr attenuators... done\n")



# ====> SET UP FOR SOLID ATTENUATORS.  SXR RELY ON GAS ATTENUATOR
# WHICH IS JUST A PV TO SET GAS PRESSURE, READ OUT GAS PRESSURE, AND
# READ OUT ATTENUATION.  COULD COME UP WITH CUSTOM CLASS THAT TAKES
# ATTENUATION AND SETS THE APPROPIATE GAS PRESSURE.  
# COMMENTED OUT FOR NOW. A VERSION OF THIS MAY BE USEFUL FOR SXR
#printnow("Defining feeatt...")
#try:
#  from common import feeatt
#  feeatt = feeatt.Feeatt(lcls_linac)
#  from common import virtualmotor
#  virtualmotor.VirtualMotor(sxrmotors,"feeA",feeatt.setTfast,feeatt.getTvalue,feeatt.wait)
#except:
#  printnow("\nWARNING: Problem, skipping!\n")  
#finally:
#  printnow(" done\n")


# COMMENTED OUT FOR NOW UNTIL CUSTOMISED FOR SXR
#printnow("Loading mcc vernier...")
#from common import mccvernier
#vernier = mccvernier.MCCVernier(sxrmotors, "XPP:USER:MCC:EPHOT", "SXR:VARS:MCC:EPHOT_ULIM_LO", "SXR:VARS:MCC:EPHOT_ULIM_HI")
#vernier = mccvernier.MCCVernier(sxrmotors, "MCC:USR:PHOTON:ENERGY", "SXR:VARS:MCC:EPHOT_ULIM_LO", "SXR:VARS:MCC:EPHOT_ULIM_HI")
#printnow(" done\n")

# COMMENTED OUT FOR NOW UNTIL CUSTOMISED FOR SXR
#printnow("Loading sxr stoppers..."),
#from common import xraystopper
#xrtstopper = xraystopper.Xraystopper("STPR:XRT1:1:SH2_PPSSUM","xrt-xray-stopper")
#dg1stopper=xraystopper.Xraystopper("HFX:UM6:STP_01:IN_DI_MPSC","dg1-xray-stopper")
#dg2stopper=xraystopper.Xraystopper("HFX:DG2:STP_01:IN_DI_MPSC","dg2-xray-stopper")
#sxrmainstopper = xraystopper.Xraystopper("PPS:FEH1:5:S5STPRSUM","sxrmain-xray-stopper")
#sxroffstopper = xraystopper.Xraystopper("PPS:FEH1:4:S4STPRSUM","sxroff-xray-stopper")
#printnow(" done\n")


# COMMENTED OUT FOR NOW UNTIL CUSTOMISED FOR SXR
#printnow("Loading sxr reference lasers..."),
#from common import reflaser
#rl1 = sxrrl1=reflaser.RefLaser(sxrmotors.rl1_y,sxrmotors.rlaser1_x,sxrmotors.rlaser1_y,sxrmotors.rlaser1_rx,sxrmotors.rlaser1_ry)
#sxrrl1.set_inpos(50)
#sxrrl1.set_outpos(0)
#rl2 = sxrrl2=reflaser.RefLaser(sxrmotors.rl2_y,sxrmotors.rlaser2_x,sxrmotors.rlaser2_y,sxrmotors.rlaser2_rx,sxrmotors.rlaser2_ry)
#sxrrl2.set_inpos(55)
#sxrrl2.set_outpos(0)
#printnow(" done\n")

#import lasersystem
#sxrlaser=lasersystem.LaserSystem()


# COMMENTED OUT FOR NOW. NEED TO THINK IF A VERSION OF IT IS NEEDED FOR SXR
#printnow("Loading sxr hrms..."),
#try:
#  from common import lusihrms
#  hrm = sxrhrms = lusihrms.HRMS(sxrmotors.hrm1_rot,
#                                sxrmotors.hrm1_y,
#                                sxrmotors.hrm2_rot,
#                                sxrmotors.hrm2_y,
#                                lcls_linac)
#except:
#  printnow("\nWARNING: Problem, skipping!\n")  
#finally:
#  printnow(" done\n")


# COMMENTED OUT FOR NOW 
#printnow("defining trasmission..."),
#try:
#  from common import virtualmotor
#  SiT = virtualmotor.VirtualMotor(sxrmotors,"SiT",sxratt.setTfast,sxratt.getTvalue,sxratt.wait)
#attMirror = simpleMotor.SimpleMotor(sxrmotors.attMirror_x)
#except:
#  printnow("\nWARNING: Problem, skipping!\n")  
#finally:
#  printnow(" done\n")



# COMMENTING OUT FOR NOW UNTIL UNDERSTOOD 
#printnow("Loading sxr ccm"),
#from common import pypsepics
#from time import sleep
#def aliomove(v): return pypsepics.put("SXR:MON:MPZ:01:POSITIONSET",v)
#def alioget():   return pypsepics.get("SXR:MON:MPZ:01:POSITIONGET")
#def aliowait():
#  dt=0.02
#  mt=10.
#  tt=0.
#  while ((tt < mt) and (abs(alioget()-pypsepics.get("SXR:MON:MPZ:01:POSITIONSET"))>3e-4)):
#    sleep(dt)
#    tt+=dt
#alio = virtualmotor.VirtualMotor(sxrmotors,"ccm_alio",aliomove,alioget,aliowait)
#def theta2finemove(v): return pypsepics.put("SXR:MON:MPZ:02:POSITIONSET",v)
#def theta2fineget():   return pypsepics.get("SXR:MON:MPZ:02:POSITIONGET")
#def theta2finewait():
#  while (abs(theta2fineget()-pypsepics.get("SXR:MON:MPZ:02:POSITIONSET"))>1e-3):
#    sleep(0.02)
#virtualmotor.VirtualMotor(sxrmotors,"ccm_theta2fine",theta2finemove,theta2fineget,theta2finewait)
#import common.ccm as ccmModule  # WHERE IS THIS MODULE ??
#gTheta0si111 = 15.270
#gTheta0si511 = 37.8 + 0.54439040148058382# 0.54439.... =  ( alioToTheta(44.146)-alioToTheta(41.8668) )
#ccmModule.gTheta0 = gTheta0si511
#ccmModule.gR      = 3.175
#ccmModule.gD      = 231.303
#gSi111dspacing = 3.13556044  # for Si111
#gSi511dspacing = 1.0452003833195924 # for Si511
#ccmModule.gdspacing = gSi511dspacing
#ccm = sxrccm = ccmModule.CCM(sxrmotors.ccm_x1,
#                 sxrmotors.ccm_x2,
#                 sxrmotors.ccm_y1,
#                 sxrmotors.ccm_y2,
#                 sxrmotors.ccm_y3,
#                 sxrmotors.ccm_alio,
#                 sxrmotors.ccm_theta2coarse,
#                 sxrmotors.ccm_theta2fine,
#                 sxrmotors.ccm_chi2,
#                 PVbase="SXR:VARS")
#from common import virtualmotor
#ccmE = virtualmotor.VirtualMotor(sxrmotors,"ccmE",sxrccm.moveE,sxrccm.wmE,sxrccm.alio.wait)
#ccmTheta = virtualmotor.VirtualMotor(sxrmotors,"ccmTheta",sxrccm.moveTheta,sxrccm.wmTheta,sxrccm.alio.wait)
#sxrccm.E = ccmE
#sxrccm.theta = ccmTheta
#sxrccm.set_inpos(3.3,1.25)
#sxrccm.set_outpos(13.18,1.25)
#printnow(" done\n")

#printnow("Loading sxrlom...")
#import common.lom as lom_module
#lom = sxrlom = lom_module.LOM(sxrmotors.lom_z1,
#                 sxrmotors.lom_x1,
#                 sxrmotors.lom_y1,
#                 sxrmotors.lom_th1,
#                 sxrmotors.lom_ch1,
#                 sxrmotors.lom_h1n,
#                 sxrmotors.lom_h1p,
#                 sxrmotors.lom_th1f,
#                 sxrmotors.lom_ch1f,
#                 sxrmotors.lom_z2,
#                 sxrmotors.lom_x2,
#                 sxrmotors.lom_y2,
#                 sxrmotors.lom_th2,
#                 sxrmotors.lom_ch2,
#                 sxrmotors.lom_h2n,
#                 sxrmotors.lom_diode2,
#                 sxrmotors.lom_th2f,
#                 sxrmotors.lom_ch2f,
#                 sxrmotors.lom_dh,
#                 sxrmotors.lom_dv,
#                 sxrmotors.lom_dr,
#                 sxrmotors.lom_df,
#                 sxrmotors.lom_ddiode1,
#                 sxrmotors.lom_yag_zoom)
#from common import virtualmotor
#lomE1 = virtualmotor.VirtualMotor(sxrmotors,"lomE1",sxrlom.moveE1,sxrlom.getE1,sxrlom.waitE1)
#sxrlom.E1 = lomE1
#lomE2 = virtualmotor.VirtualMotor(sxrmotors,"lomE2",sxrlom.moveE2,sxrlom.getE2,sxrlom.waitE2)
#sxrlom.E2 = lomE2
#lomE = virtualmotor.VirtualMotor(sxrmotors,"lomE",sxrlom.moveE,sxrlom.getE,sxrlom.waitE)
#sxrlom.E = lomE
#sxrlom.set_inpos(0,0)
#sxrlom.set_outpos(-19.5,-4.5) # was -20,-5, but after 8-29-2012, added soft limits so changed these
#sxrlom.set_diode_outpos(0)
#sxrlom.set_diode_inpos(24)
#sxrlom.set_vertical_outpos(40)
#sxrlom.set_yag_inpos(2)
#vslit=range(3)
#vslit[0]=20.5 #100 um 
#vslit[1]=25.5 #500 um 
#vslit[2]=30.5 #2   mm
#sxrlom.set_vslit_pos(vslit) 
#sxrlom.set_horizontal_outpos(110)
#sxrlom.set_dectris_inpos(74)
#hslit=range(3)
#hslit[0]=49.5 #100 um 
#hslit[1]=26.5 #500 um  to be checked
#hslit[2]=8 #2   mm to be checked
#sxrlom.set_hslit_pos(hslit) 
#foils=range(8)
#foils[0]=0.5   #all out
#foils[1]=71    #Mo
#foils[2]=106   #Zr
#foils[3]=143   #Ge
#foils[4]=178.5 #Cu
#foils[5]=215   #Ni
#foils[6]=250   #Fe
#foils[7]=285   #Ti
#sxrlom.set_foils_pos(foils)
#sxrlom.set_crystal_extents( ({'y': 33.7, 'ymin': 28.2, 'ymax': 39.2, 'ref': "111"}, {'y': 14.1, 'ymin': 10.4, 'ymax': 17.8, 'ref': "111", 'dz': -0.404439, 'dth': -0.125586}),
#                            ({'y': 10, 'ymin': 6, 'ymax': 14, 'ref': "111"}, {'y': 42.4, 'ymin': 41.4, 'ymax': 43.4, 'ref': "220", 'dz': 0.002539, 'dth': 0.326014})
#                            )
#printnow(" done\n")



# NO BE LENS IN SXR - COMMENT OUT FOR NOW
#printnow("Loading Be Lenses...")
#from common import beLens
#crl2 = beLens.BeLens(sxrmotors.crl2_x, sxrmotors.crl2_y, sxrmotors.crl2_z, "SB2 Compound Refractive Lens")
#printnow(" done\n")

#printnow("Loading Pulse Picker !!! crazy new cool feature !!!")
#import pulsePicker
#pp = pulsePicker.PulsePicker(sxrmotors.pp_x, sxrmotors.pp_y, sxrmotors.pp_r)
#printnow(" done\n")


# COMMENTED OUT FOR NOW AS NO GONIOMETER AT SXR
# WILL NEED TO LOOK AT THE CODE MORE CLOSELY TO SEE IF ITS USABLE AT SXR
#Printnow("Loading goniometer...")
#from common import goniometer
#diff = goniometer.Goniometer(
#  sxrmotors.gon_x,
#  sxrmotors.gon_y,
#  sxrmotors.gon_theta,
#  sxrmotors.gon_2theta,
#  sxrmotors.gon_chi,
#  sxrmotors.gon_phi,
#  sxrmotors.gon_sx,
#  sxrmotors.gon_sy,
#  sxrmotors.gon_sz,
#  sxrmotors.gon_dy,
#  sxrmotors.gon_gamma,
#  "diff",
#  "SXR:VARS"
#  )


# COMMENTED OUT AS NO DIFFRACTOMETER AS SXR
# Diffractometer detector 2phi rotation virtual motor
#diffDetPhi = virtualmotor.VirtualMotor(sxrmotors,"diffDetPhi",diff.moveDetPhi,diff.wmDetPhi,diff.waitDetPhi,get_hilim=diff.getHiLimDetPhi,get_lowlim=diff.getLowLimDetPhi)
#diff.reflectdet = diffDetPhi

# Diffractometer sample-phi/detector-2phi rotation virtual motor
#diffDSPhi = virtualmotor.VirtualMotor(sxrmotors,"diffDSPhi",diff.moveDSPhi,diff.wmDSPhi,diff.waitDSPhi,get_hilim=diff.getHiLimDSPhi,get_lowlim=diff.getLowLimDSPhi)
#diff.reflect = diffDSPhi



#printnow(" done\n")

# COMMENTED OUT. NO LADM AT SXR
#printnow("Loading ladm...\n")
#printnow(" ladm stages,")
#import common.ladm as ladm_module
#ladm = sxrladm = ladm_module.LADM(sxrmotors.ladm_x1,
#                 sxrmotors.ladm_y1,
#                 sxrmotors.ladm_x2,
#                 sxrmotors.ladm_y2,
#                 sxrmotors.ladm_z
#                 )
#from common import virtualmotor
#ladmTheta = virtualmotor.VirtualMotor(sxrmotors,"ladmTheta",sxrladm.moveTheta,sxrladm.wmTheta,sxrladm.waitAll,sxrladm.setTheta)
#sxrladm.theta = ladmTheta
#ladmXT = virtualmotor.VirtualMotor(sxrmotors,"ladmXT",sxrladm.moveX,sxrladm.wmX,sxrladm.waitAll,sxrladm._setX, sxrladm._set_hilimX, sxrladm._get_hilimX, sxrladm._set_lowlimX, sxrladm._get_lowlimX)
#sxrladm.XT = ladmXT
#sxrladm.XT.set_lowlim(-10)
#sxrladm.XT.set_hilim(2000)


# WHERE IS blinst MODULE ? -- COMMENT OUT FOR NOW
#printnow(" aerotech stage,")
#from blinst import aerotech
#sxrdet = aerotech.Aerotech(sxrmotors.ladm_dettrans_x,
#                 sxrmotors.ladm_dettrans_y
#                 )


# COMMENTED OUT FOR NOW. DON'T KNOW WHERE BEAMSTOP MODULE IS
#printnow(" beamstops\n")
#from common import beamstop
#ladmbs2 = beamstop.Beamstop(sxrmotors.ladm_bs2_radial,
#                            sxrmotors.ladm_bs2_transverse,
#                            '?? '
#                            )
#ladmbs6 = beamstop.Beamstop(sxrmotors.ladm_bs6_radial,
#                            sxrmotors.ladm_bs6_transverse,
#                            6
#                            )
#ladmbs10 = beamstop.Beamstop(sxrmotors.ladm_bs10_radial,
#                            sxrmotors.ladm_bs10_transverse,
#                            '?? '
#                            )
#from common import beamstops
#ladmbs = beamstops.Beamstops()
#ladmbs.addBeamstop(ladmbs2)
#ladmbs.addBeamstop(ladmbs6)
#ladmbs.addBeamstop(ladmbs10)
#printnow("Loading ladm... done\n")

# COMMENTED OUT FOR NOW. IF TO BE USED, NEEDS TO BE CUSTOMISED FOR SXR
#printnow("Loading local detectors...")
#from common import localDetector
#printnow(" ld1 on Goniometer")
#ld1 = localDetector.LocalDetector(sxrmotors.diff_ldet_svg,
#                                  sxrmotors.diff_ldet_svo,
#                                  sxrmotors.diff_ldet_shg,
#                                  sxrmotors.diff_ldet_sho,
#                                  sxrmotors.diff_ldet_yag,
#                                  sxrmotors.diff_ldet_zm,
#                                  "DIFF"
#                                  )
#printnow(" ld2 on LADM\n")
#ld2 = localDetector.LocalDetector(sxrmotors.ladm_ldet_svg,
#                                  sxrmotors.ladm_ldet_svo,
#                                  sxrmotors.ladm_ldet_shg,
#                                  sxrmotors.ladm_ldet_sho,
#                                  sxrmotors.ladm_ldet_yag,
#                                  sxrmotors.ladm_ldet_zm,
#                                  "LADM"
#                                  )
#printnow("Loading local detectors... done\n")

# COMMENTED OUT FOR NOW.  NEED TO DECIDE IF ITS NEEDED FOR SXR
#printnow("Loading sxr slits..."),
# SLITS
#from common.lusislit import LusiSlit
#s0 = sxrs0 = LusiSlit(sxrmotors.s0_u,sxrmotors.s0_d,sxrmotors.s0_n,sxrmotors.s0_s,"s0")   # FEE Mask Slits
#xpps1 = h2s1 = LusiSlit(sxrmotors.h2s1_u,sxrmotors.h2s1_d,sxrmotors.h2s1_n,sxrmotors.h2s1_s,"xpps1")  # Slit on XPP SB1 (SXR)
#s1 = sxrs1 = LusiSlit(sxrmotors.s1_u,sxrmotors.s1_d,sxrmotors.s1_n,sxrmotors.s1_s,"s1")
#s2 = sxrs2 = LusiSlit(sxrmotors.s2_u,sxrmotors.s2_d,sxrmotors.s2_n,sxrmotors.s2_s,"s2")
#s3 = sxrs3 = LusiSlit(sxrmotors.s3_u,sxrmotors.s3_d,sxrmotors.s3_n,sxrmotors.s3_s,"s3")
#s3m = sxrs3m = LusiSlit(sxrmotors.s3m_u,sxrmotors.s3m_d,sxrmotors.s3m_n,sxrmotors.s3m_s,"s3m")
#s4 = sxrs4 = LusiSlit(sxrmotors.s4_u,sxrmotors.s4_d,sxrmotors.s4_n,sxrmotors.s4_s,"s4")
#s5 = sxrs5 = LusiSlit(sxrmotors.s5_u,sxrmotors.s5_d,sxrmotors.s5_n,sxrmotors.s5_s,"s5")
#s6 = sxrs6 = LusiSlit(sxrmotors.s6_u,sxrmotors.s6_d,sxrmotors.s6_n,sxrmotors.s6_s,"s6")

#s0hg = virtualmotor.VirtualMotor(sxrmotors,"s0hg",sxrs0.mv_hg,sxrs0.wm_hg,sxrs0.waith,sxrs0.set_hg)
#s1hg = virtualmotor.VirtualMotor(sxrmotors,"s1hg",sxrs1.mv_hg,sxrs1.wm_hg,sxrs1.waith,sxrs1.set_hg)
#s2hg = virtualmotor.VirtualMotor(sxrmotors,"s2hg",sxrs2.mv_hg,sxrs2.wm_hg,sxrs2.waith,sxrs2.set_hg)
#s3mhg = virtualmotor.VirtualMotor(sxrmotors,"s3mhg",sxrs3m.mv_hg,sxrs3m.wm_hg,sxrs3m.waith,sxrs3m.set_hg)
#s3hg = virtualmotor.VirtualMotor(sxrmotors,"s3hg",sxrs3.mv_hg,sxrs3.wm_hg,sxrs3.waith,sxrs3.set_hg)
#s4hg = virtualmotor.VirtualMotor(sxrmotors,"s4hg",sxrs4.mv_hg,sxrs4.wm_hg,sxrs4.waith,sxrs4.set_hg)
#s5hg = virtualmotor.VirtualMotor(sxrmotors,"s5hg",sxrs5.mv_hg,sxrs5.wm_hg,sxrs5.waith,sxrs5.set_hg)
#s6hg = virtualmotor.VirtualMotor(sxrmotors,"s6hg",sxrs6.mv_hg,sxrs6.wm_hg,sxrs6.waith,sxrs6.set_hg)


#s0vg = virtualmotor.VirtualMotor(sxrmotors,"s0vg",sxrs0.mv_vg,sxrs0.wm_vg,sxrs0.waitv,sxrs0.set_vg)
#s1vg = virtualmotor.VirtualMotor(sxrmotors,"s1vg",sxrs1.mv_vg,sxrs1.wm_vg,sxrs1.waitv,sxrs1.set_vg)
#s2vg = virtualmotor.VirtualMotor(sxrmotors,"s2vg",sxrs2.mv_vg,sxrs2.wm_vg,sxrs2.waitv,sxrs2.set_vg)
#s3mvg = virtualmotor.VirtualMotor(sxrmotors,"s3mvg",sxrs3m.mv_vg,sxrs3m.wm_vg,sxrs3m.waitv,sxrs3m.set_vg)
#s3vg = virtualmotor.VirtualMotor(sxrmotors,"s3vg",sxrs3.mv_vg,sxrs3.wm_vg,sxrs3.waitv,sxrs3.set_vg)
#s4vg = virtualmotor.VirtualMotor(sxrmotors,"s4vg",sxrs4.mv_vg,sxrs4.wm_vg,sxrs4.waitv,sxrs4.set_vg)
#s5vg = virtualmotor.VirtualMotor(sxrmotors,"s5vg",sxrs5.mv_vg,sxrs5.wm_vg,sxrs5.waitv,sxrs5.set_vg)
#s6vg = virtualmotor.VirtualMotor(sxrmotors,"s6vg",sxrs6.mv_vg,sxrs6.wm_vg,sxrs6.waitv,sxrs6.set_vg)


#s0ho = virtualmotor.VirtualMotor(sxrmotors,"s0ho",sxrs0.mv_ho,sxrs0.wm_ho,sxrs0.waith,sxrs0.set_ho)
#s1ho = virtualmotor.VirtualMotor(sxrmotors,"s1ho",sxrs1.mv_ho,sxrs1.wm_ho,sxrs1.waith,sxrs1.set_ho)
#s2ho = virtualmotor.VirtualMotor(sxrmotors,"s2ho",sxrs2.mv_ho,sxrs2.wm_ho,sxrs2.waith,sxrs2.set_ho)
#s3mho = virtualmotor.VirtualMotor(sxrmotors,"s3mho",sxrs3m.mv_ho,sxrs3m.wm_ho,sxrs3m.waith,sxrs3m.set_ho)
#s3ho = virtualmotor.VirtualMotor(sxrmotors,"s3ho",sxrs3.mv_ho,sxrs3.wm_ho,sxrs3.waith,sxrs3.set_ho)
#s4ho = virtualmotor.VirtualMotor(sxrmotors,"s4ho",sxrs4.mv_ho,sxrs4.wm_ho,sxrs4.waith,sxrs4.set_ho)
#s5ho = virtualmotor.VirtualMotor(sxrmotors,"s5ho",sxrs5.mv_ho,sxrs5.wm_ho,sxrs5.waith,sxrs5.set_ho)
#s6ho = virtualmotor.VirtualMotor(sxrmotors,"s6ho",sxrs6.mv_ho,sxrs6.wm_ho,sxrs6.waith,sxrs6.set_ho)


#s0vo = virtualmotor.VirtualMotor(sxrmotors,"s0vo",sxrs0.mv_vo,sxrs0.wm_vo,sxrs0.waitv,sxrs0.set_vo)
#s1vo = virtualmotor.VirtualMotor(sxrmotors,"s1vo",sxrs1.mv_vo,sxrs1.wm_vo,sxrs1.waitv,sxrs1.set_vo)
#s2vo = virtualmotor.VirtualMotor(sxrmotors,"s2vo",sxrs2.mv_vo,sxrs2.wm_vo,sxrs2.waitv,sxrs2.set_vo)
#s3mvo = virtualmotor.VirtualMotor(sxrmotors,"s3mvo",sxrs3m.mv_vo,sxrs3m.wm_vo,sxrs3m.waitv,sxrs3m.set_vo)
#s3vo = virtualmotor.VirtualMotor(sxrmotors,"s3vo",sxrs3.mv_vo,sxrs3.wm_vo,sxrs3.waitv,sxrs3.set_vo)
#s4vo = virtualmotor.VirtualMotor(sxrmotors,"s4vo",sxrs4.mv_vo,sxrs4.wm_vo,sxrs4.waitv,sxrs4.set_vo)
#s5vo = virtualmotor.VirtualMotor(sxrmotors,"s5vo",sxrs5.mv_vo,sxrs5.wm_vo,sxrs5.waitv,sxrs5.set_vo)
#s6vo = virtualmotor.VirtualMotor(sxrmotors,"s6vo",sxrs6.mv_vo,sxrs6.wm_vo,sxrs6.waitv,sxrs6.set_vo)


#sxrs0.hg=s0hg; sxrs0.ho=s0ho; sxrs0.vg=s0vg; sxrs0.vo=s0vo
#sxrs1.hg=s1hg; sxrs1.ho=s1ho; sxrs1.vg=s1vg; sxrs1.vo=s1vo
#sxrs2.hg=s2hg; sxrs2.ho=s2ho; sxrs2.vg=s2vg; sxrs2.vo=s2vo
#sxrs3.hg=s3hg; sxrs3.ho=s3ho; sxrs3.vg=s3vg; sxrs3.vo=s3vo
#sxrs3m.hg=s3mhg; sxrs3m.ho=s3mho; sxrs3m.vg=s3mvg; sxrs3m.vo=s3mvo
#sxrs4.hg=s4hg; sxrs4.ho=s4ho; sxrs4.vg=s4vg; sxrs4.vo=s4vo
#sxrs5.hg=s5hg; sxrs5.ho=s5ho; sxrs5.vg=s5vg; sxrs5.vo=s5vo
#sxrs6.hg=s6hg; sxrs6.ho=s6ho; sxrs6.vg=s6vg; sxrs6.vo=s6vo


#printnow(" done\n")


#printnow("Loading sxr ipms..."),
#from common import lusiipm
# in user coordinates ...
#dg1_tpos = range(5)
#dg1_tpos[0] = 0
#dg1_tpos[1] = 23.5-6  #thickest
#dg1_tpos[2] = 37-6
#dg1_tpos[3] = 50.5-6
#dg1_tpos[4] = 64-6  #thinnest
#ipm1 = sxripm1 = lusiipm.IPM(sxrmotors.ipm1_xd,
#                   sxrmotors.ipm1_yd,
#                   sxrmotors.ipm1_yt,
#                   dg1_tpos,sxrdetectors.ipm1,"ipm1")
#sxripm1.set_ccmoffset(ccm_offset)
#sxripm1.set_diodeout(-40)
#sxripm1.set_diodein(0)


#dg2_tpos = range(5)
#dg2_tpos[0] = 0
#dg2_tpos[1] = 15.85
#dg2_tpos[2] = 29.4983
#dg2_tpos[3] = 42.89525
#dg2_tpos[4] = 56.3994
#ipm2 = sxripm2 = lusiipm.IPM(sxrmotors.ipm2_xd,
#                   sxrmotors.ipm2_yd,
#                   sxrmotors.ipm2_yt,
#                   dg2_tpos,sxrdetectors.ipm2,"ipm2")
#sxripm2.set_ccmoffset(ccm_offset)
#sxripm2.set_diodeout(-40)
#sxripm2.set_diodein(0)

#ipm_mon_tpos = range(5)
#ipm_mon_tpos[0] = 2
#ipm_mon_tpos[1] = 26
#ipm_mon_tpos[2] = 39
#ipm_mon_tpos[3] = 53
#ipm_mon_tpos[4] = 66.3
#ipmmono = sxripmmono = lusiipm.IPM(sxrmotors.ipm_mon_xd,
#                   sxrmotors.ipm_mon_yd,
#                   sxrmotors.ipm_mon_yt,
#                   ipm_mon_tpos,sxrdetectors.ipmmono,"ipmmono")
#sxripmmono.set_ccmoffset(ccm_offset)
#sxripmmono.set_diodeout(-40)
#sxripmmono.set_diodein(0)

#"""
#dg3m_tpos = range(5)
#dg3m_tpos[0] = 0
#dg3m_tpos[1] = 25-6
#dg3m_tpos[2] = 39-6
#dg3m_tpos[3] = 53-6
#dg3m_tpos[4] = 66-6
#sxripm3m = lusiipm.IPM(sxrmotors.ipm3m_xd,
#                   sxrmotors.ipm3m_yd,
#                   sxrmotors.ipm3m_yt,
#                   dg3m_tpos,sxrdetectors.ipm3m,"ipm3m")
#sxripm3m.set_ccmoffset(ccm_offset)
#sxripm3m.set_diodeout(-40)
#sxripm3m.set_diodein(0)
#"""

#dg3_tpos = range(5)
#dg3_tpos[0] = 0
#dg3_tpos[1] = 22.1
#dg3_tpos[2] = 35.75
#dg3_tpos[3] = 49.2
#dg3_tpos[4] = 62.6
#ipm3 = sxripm3 = lusiipm.IPM(sxrmotors.ipm3_xd,
#                   sxrmotors.ipm3_yd,
#                   sxrmotors.ipm3_yt,
#                   dg3_tpos,sxrdetectors.ipm3,"ipm3")
#sxripm3.set_ccmoffset(ccm_offset)
#sxripm3.set_diodeout(-40)
#sxripm3.set_diodein(0)

#sb1_tpos = range(5)
#sb1_tpos[0] =  0
#sb1_tpos[1] =  18.55
#sb1_tpos[2] =  32
#sb1_tpos[3] =  45.6
#sb1_tpos[4] =  59
#ipm4 = sxripm4 = lusiipm.IPM(sxrmotors.ipm4_xd,
#                   sxrmotors.ipm4_yd,
#                   sxrmotors.ipm4_yt,
#                   sb1_tpos,sxrdetectors.ipm4,"ipm4")

#sxripm4.set_ccmoffset(ccm_offset)
#sxripm4.set_diodeout(-40)
#sxripm4.set_diodein(0)

#sb2_tpos = range(5)
#sb2_tpos[0] = 0
#sb2_tpos[1] = 18.25
#sb2_tpos[2] = 32
#sb2_tpos[3] = 45.35
#sb2_tpos[4] = 58.799
#ipm5 = sxripm5 = lusiipm.IPM(sxrmotors.ipm5_xd,
#                   sxrmotors.ipm5_yd,
#                   sxrmotors.ipm5_yt,
#                   sb2_tpos,sxrdetectors.ipm5,"ipm5")
#sxripm5.set_ccmoffset(ccm_offset)
#sxripm5.set_diodeout(-46.5)
#sxripm5.set_diodein(0)

#printnow(" done\n")

# COMMENT OUT FOR NOW
#printnow("Loading sxr pims..."),
#from common import lusipim

#xppyag1 = lusipim.PIM(sxrmotors.yagh2_yscreen,
#                  sxrmotors.yagh2_zoom,
#                  led="HXX:UM6:CIL:01",
#                  det=sxrdetectors.dio1,
#                  desc="xppyag1(in h2)")

#yag1 = sxryag1 = lusipim.PIM(sxrmotors.yag1_yscreen,
#                  sxrmotors.yag1_zoom,
#                  led="HXX:UM6:CIL:01",
#                  det=sxrdetectors.dio1,
#                  desc="yag1(dg1)")
#sxryag1.set_screen_in(0)
#sxryag1.set_diode_in(26)
#sxryag1.set_all_out(-52)

#yag2 = sxryag2 = lusipim.PIM(sxrmotors.yag2_yscreen,
#                  sxrmotors.yag2_zoom,
#                  led="HFX:DG2:CIL:01",
#                  det=sxrdetectors.dio2,
#                  desc="yag2(dg2)")
#sxryag2.set_screen_in(0)
#sxryag2.set_diode_in(26)
#sxryag2.set_all_out(-52)

#yag3m = sxryag3m = lusipim.PIM(sxrmotors.yag3m_yscreen,
#                  sxrmotors.yag3m_zoom,
#                  led="HFX:DG3:CIL:01",
#                  det=sxrdetectors.dio3m,
#                  desc="yag3m(dg3main)")
#sxryag3m.set_screen_in(0)
#sxryag3m.set_diode_in(26)
#sxryag3m.set_all_out(-52)

#yag3 = sxryag3 = lusipim.PIM(sxrmotors.yag3_yscreen,
#                  sxrmotors.yag3_zoom,
#                  led="SXR:DG3:CIL:02",
#                  det=sxrdetectors.dio3,
#                  desc="yag3(dg3offset)")
#sxryag3.set_screen_in(0)
#sxryag3.set_diode_in(26)
#sxryag3.set_all_out(-52)

#yag4 = sxryag4 = lusipim.PIM(sxrmotors.yag4_yscreen,
#                  sxrmotors.yag4_zoom,
#                  led="SXR:SB1:CIL:01",
#                  det=sxrdetectors.dio4,
#                  desc="yag4(sb1)")
#sxryag4.set_screen_in(0)
#sxryag4.set_diode_in(26)
#sxryag4.set_all_out(-52)

#yag5 = sxryag5 = lusipim.PIM(sxrmotors.yag5_yscreen,
 #                 sxrmotors.yag5_zoom,
 #                 #lens_focus_motor=sxrmotors.yag5_focus,
 #                 led="SXR:SB2:CIL:01",
 #                 det=sxrdetectors.dio5,
 #                 desc="yag5(sb2)")
#sxryag5.set_screen_in(0)
#sxryag5.set_diode_in(26)
#sxryag5.set_all_out(-56.2)

#printnow(" done\n")


printnow("Loading daq interface..."),
if PYPS_INTERACTIVE:
  from common import daq
  sxrdaq = daq.Daq(host="sxr-control",platform=DAQ_PLATFORM)
  from common import daq_config
  sxrdaqconfig = daq_config.DaqConfig() #current
  #sxrdaqconfig = daq_config.DaqConfig(dbpath="/reg/g/pcds/dist/pds/sxr/configdb/oct17")
else:
  print "WARNING: Not Loading DAQ because not in interactive mode"
  pass
printnow(" done\n")



"""
printnow("Loading control evr..."),
try:
  from common import controlevr
  #sxrevr1 = controlevr.ControlEVR("SXR:R04:EVR:33")
  #sxrevr1 = controlevr.ControlEVR("SXR:R32:EVR:41")
  #sxrevr1 = controlevr.ControlEVR("SXR:R38:EVR:41")
  sxrevrpp = controlevr.ControlEVR("SXR:R42:EVR:01",trigger=2)

  from common import eventsequencer
  #sxrevent = eventsequencer.EventSequencer(local_iocbase="SXR:RXX:IOC:XX:EV",sequence_group=2)
  sxrevent = eventsequencer.EventSequencer(local_iocbase="SXR:ECS:IOC:01",sequence_group=4)
except:
  printnow("\nWARNING: Problem, skipping!\n")  
finally:
  printnow(" done\n")

printnow("Loading sxr functions..."),
from sxrfunctions import *
printnow(" done\n")
"""


#from functions import *


#######################################
#######################################
####                               ####
####  Devices on User Patch Panel  ####
####                               ####
#######################################
#######################################

## JJ Slits on MMS-17/20
# COMMENT OUT FOR NOW.  NEED TO DECIDE IF SUCH A MODULE IS NEEDED FOR SXR
#from common import jjSlits2, jjSlits
# Normal orientation:
#s7 = jjSlits.JJSlits(sxrmotors.user_dumb_17,sxrmotors.user_dumb_18,sxrmotors.user_dumb_19,sxrmotors.user_dumb_20,"Sample-Slits")
# With Cables down, but Z-orientation maintained (must make MMS:18 reverse direction)
#s7 = jjSlits.JJSlits(sxrmotors.user_dumb_19,sxrmotors.user_dumb_20,sxrmotors.user_dumb_17,sxrmotors.user_dumb_18,"Sample-Slits")
#s8 = jjSlits.JJSlits(sxrmotors.user_dumb_23,sxrmotors.user_dumb_24,sxrmotors.user_dumb_21,sxrmotors.user_dumb_22,"LADM-Nose-Slits")


###### L729 Madsen ######
###### L729 Madsen ######
#import l729

##### import user setup into sxr_python
"""
printnow("Importing user setup...\n")
from experiments import current
user = current.USER(elog=sxrElog)
printnow(" User setup: " +  user.objName + "[imported]\n")
printnow("Importing user setup... done\n")
"""
###############################################


'''
madsen = l729.L729(diamondx = sxrmotors.user_mmn_02,
                   diamondy = sxrmotors.user_mmn_01,
                   specphi = sxrmotors.user_mmn_03,
                   speczoom = sxrmotors.user_dumb_32,
                   specfocus = sxrmotors.user_dumb_31,
                   yagzoom = sxrmotors.user_dumb_29,
                   yagfocus = sxrmotors.user_dumb_30,
                   cspadx = sxrmotors.user_mmn_05,
                   objName = "madsen",
                   presetsfile = "/reg/neh/operator/sxropr/sxrpython_data/L729_presets.py"
                   )
'''


###### L710 Hill ######
"""
# Energy Analyzer
import EnergyAnalyzer
ea = EnergyAnalyzer.EnergyAnalyzer(
  ath = sxrmotors.user_ims_16,
  atth = sxrmotors.user_ims_15,
  anaz = sxrmotors.user_dumb_23,
  detz = sxrmotors.user_dumb_22,
  achi = sxrmotors.user_dumb_21,
  yagzoom = sxrmotors.user_dumb_32,
  yagfocus = sxrmotors.user_dumb_31,
  diamondx = sxrmotors.user_mmn_04,
  diamondy = sxrmotors.user_mmn_02,
  objName = "ea",
  pvBase = "SXR:VARS"
  )

# Energy Analyzer Theta-2Theta
eaen = virtualmotor.VirtualMotor(sxrmotors,"en",ea.moveEn,ea.wmEn,ea.waitEn,get_hilim=ea.getHiLimEn,get_lowlim=ea.getLowLimEn,set_hilim=ea.setHiLimEn,set_lowlim=ea.setLowLimEn)
ea.en = eaen
#print ea.motors
ea.motors["en"]=eaen
#print ea.motors
"""

###### L637 David ######

# from l637 import G2,Sample,Sample2

# g2 = G2(sxrmotors.user_dumb_29,
#         sxrmotors.user_dumb_30,
#         sxrmotors.user_dumb_31,
#         sxrmotors.user_mmn_09,
#         sxrmotors.user_mmn_10,
#         sxrmotors.user_mmn_11,
#         'g2',
#         None,
#         '/reg/neh/operator/sxropr/sxrpython_data/l637g2presets.py'
#         )

# sample = Sample2(sxrmotors.user_mmn_02,
#                  sxrmotors.user_mmn_03,
#                  sxrmotors.user_mmn_01,
#                  sxrmotors.ladm_dumb_62,
#                  sxrmotors.ladm_dumb_63,
#                  sxrmotors.ladm_dumb_64,
#                  sxrmotors.ladm_dumb_65,
#                  sxrmotors.user_mmn_05,
#                  sxrmotors.user_mmn_04,
#                  sxrmotors.user_mmn_06,
#                  sxrmotors.user_ims_01,
#                  'sample',
#                  None,
#                  '/reg/neh/operator/sxropr/sxrpython_data/l637samplepresets2.py'
#                  )

####### L569 Kim #######
"""
sam_bsy = sxrmotors.user_mmn_02
sam_bsx = sxrmotors.user_mmn_06

sam_knifex = sxrmotors.user_mmn_03
sam_x = sxrmotors.user_mmn_08
"""


# Normal orientation:
#sAPS = jjSlits.JJSlits(sxrmotors.user_dumb_25,sxrmotors.user_dumb_26,sxrmotors.user_dumb_27,sxrmotors.user_dumb_28,"APS-Slits")


# Spectrometer:
#speczoom = sxrmotors.user_dumb_29



# SAXS Setup during 2011 Nov 24-28 Run (L304)
#import gruebelSaxs
#saxs = gruebelSaxs.GruebelSaxs(sxrmotors.user_ims_09, sxrmotors.user_ims_03, sxrmotors.user_ims_02, sxrmotors.user_ims_06, sxrmotors.user_ims_04, sxrmotors.user_ims_05)

#ljx = sxrmotors.user_dumb_21
#ljy = sxrmotors.user_dumb_22

#pnccdsamx = sxrmotors.user_mmn_01
#pnccdsamy = sxrmotors.user_mmn_02


if PYPS_INTERACTIVE:
  from pylab import ion
  ion()
else:
  print "WARNING: Not Loading ion because not in interactive mode"
  pass

# COMEMENTED OUT AS SXR HAS NO PULSE PICKER
#printnow("Loading Pulse Picker...\n")
#from pp_nogui import PPicker

#ppcfg = {}
#ppcfg['Instr']                      = 'sxr'
#ppcfg['Sequencer Pv']               = 'SXR:RXX:IOC:XX:EV'
#ppcfg['Seq play mode Pv']           = 'IOC:IN20:EV01'
#ppcfg['PP Rotation motor Pv']       = 'SXR:SB2:MMS:09'
#ppcfg['PP Y translation Pv']        = 'SXR:SB2:MMS:21'
#ppcfg['PP X translation Pv']        = 'SXR:SB2:MMS:08'
#ppcfg['PP ioc name']                = 'ioc-sxr-trigger-ims'
#ppcfg['PP ioc server name']         = 'ioc-sxr-mot1'
#ppcfg['EVR Pv']                     = 'SXR:R42:EVR:01'
#ppcfg['EVR Burst mode delay']       = '4500'
#ppcfg['EVR Single mode delay']      = '5500'
#ppcfg['EVR trigger channel number'] = '2'
#ppcfg['EDM PP motor screen script'] = 'ppm_gui.sh'
#ppcfg['EDM EVR screen script']      = 'evr_gui.sh'
#ppcfg['EVR edm screen release']     = 'R3.3.0-2.6.0'
#ppcfg['PP edm screen release']      = 'R2.3.7'
#ppcfg['Configuration directory']    = '~/'
#ppcfg['Current working directory']  = os.getcwd()
#ppcfg['Alignment offset']           = 68.1328 + 11.25

#pp = PPicker(ppcfg)
#printnow("Loading Pulse Picker... done\n")
#pp.help()

print "DONE Loading sxrbeamline!"
