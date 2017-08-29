#!/usr/bin/python
# This module provides general functions (mv, wm) that act on more than
# one motor
# 
# Author:         Marco Cammarata (SLAC)
# Created:        June 13, 2010
# Modifications:
#   June 13, 2010 MC
#       first version

from sxrbeamline import *
from common import pypsepics
from common.utilities import estr
import time

def getTtot(toprint=True):
   feeT=feeatt.getTvalue()
   localT=sxratt.getTvalue()
   totalT=feeT*localT
   str= "\nTotal trasmission at working energy = %.3e \n" % totalT
   str+= '\nFee attenuators...\n'+ feeatt.status()
   str+= '\nLocal attenuators...\n'+ sxratt.status()
   if toprint is True:
     printnow(str)
   else:
     return str

def loggrab(In,comment=""):
   scangrab(In,comment)

def scangrab(In,comment=""):
#  import IPython
#  hi = IPython.ipapi.get()
#  h  = hi.magic("history")
  h = In
  has_img=0
#  h.reverse()
  imgfile = "/tmp/sxrdaq.plot.png"
  txtfile = "/tmp/sxrdaq.plot.txt"
  for i in h:
    if ( (i.find("scan")>0) & (i.find("loggrab")!=0) ) > 0:
      str=i
  if (comment != ""):
    str += comment + "\n"
############################################
  str += "\n FEEATT  \n"  	
  str += feeatt.status() + "\n\n"
  str += "SXRATT \n"
  str += sxratt.status() + "\n"	
############################################
  try:
    sxrdaq.plot.fig.savefig(imgfile)
    sxrdaq.savetxt(txtfile)
    has_img = 1
  except:
    pass
  if (has_img==1):
    config.Elog.submit(text=str,tag="grab",file2=imgfile,file_descr2="sxrpython scan figure",file=txtfile,file_descr="sxrpython data point")
  else:
    config.Elog.submit(text=str,tag="grab")


def select_sxrmotors():
  nlist = sxrmotors.__dict__.keys()
  mlist = []
  for i in nlist:
    m = sxrmotors.__getattribute__(i)
    try:
      if ((m.pvname.find("XPP") == 0) or (m.pvname.find("HX2") == 0))and (m.pvname.find("MMS")>0) : mlist.append(m.pvname)
      print m.pvname
    except:
      pass
  for i in range(17,27):
    mlist.append("XPP:SB2:MMS:%d" % i)
  mlist.sort()
  return mlist
    

def motor_par(motor_pvlist):
  pars = [
   'description'         , '.DESC',
   'acceleration'        , '.ACCL',
   'units (EGU)'         , '.EGU',
   'direction'           , '.DIR',
   'encoder step size'   , '.ERES',
   'Gear x Pitch'        , '.UREV',
   'User Offset (EGU)'   , '.OFF',
   'retry deadband (EGU)', '.RDBD',
   'Steps Per Rev'       , '.SREV',
   'Speed(RPS)'          , '.S',
   'Speed(UGU/S)'        , '.VELO',
   'base speed (RPS)'    , '.SBAS',
   'base speed (EGU/s)'  , '.VBAS',
   'backlash'            , '.BDST',
   'run current (%)'     , ':RC',
   'use encoder (:EE)'   , ':EE'
  ]
  fields_desc=pars[::2]
  fields=pars[1::2]
  out=[]
  title1="pvname"
  title2="------"
  for f in fields_desc:
    title1 += ",%s" % f
  for f in fields:
    title2 += ",%s" % f
  out.append(title1)
  out.append(title2)
  for m in motor_pvlist:
    v=m
    for f in fields:
      try:
        vv=pypsepics.get( m + f)
      except:
        print m + f
        vv="?"
      v += ",%s" % vv
    out.append(v)
  return out
    
def load_MMS_pars(cvsfile):
  f=open(cvsfile)
  lines = f.readlines()
  for i in range(len(lines)): lines[i]=lines[i].rstrip("\n")
  fields = lines[1];
  lines = lines[2:];
  fields = fields.split(",")[1:]
  for l in lines:
    ll=l.split(",")
    pv=ll[0]
    if pv.startswith("#"): continue
    values=ll[1:]
    for i in range(len(fields)):
      if fields[i].startswith("#"): continue
      if (values[i] != "?"):
        try:
          vv=float(values[i])
        except:
          vv=values[i]
        if (fields[i]==":RC"):  vv=str(values[i]); # for some reason the run current must be a string !
        if (fields[i]==":EE"):  vv=str(values[i]); # for some reason the use encoder must be a string !
        if (fields[i]==".DIR"):  vv=int(values[i]);
        if (fields[i]==".SREV"): vv=int(values[i]);
        try:
          print "setting  ",pv+fields[i]," to ",values[i],
          pypsepics.put(pv+fields[i],vv)
          if (fields[i]==".S"): pypsepics.put(pv+".SMAX",vv)
          print " done"
        except:
          print "FAILED TO set ",pv+fields[i]," to ",values[i]
#        time.sleep(0.1)
        try:
          print "readback ",pv+fields[i], "    " ,pypsepics.get(pv+fields[i])
        except:
          print "FAILED TO READBACK ",pv+fields[i]


def slits(hg=None,vg=None,fast=0,elog = 0):
   all = [s1,s2,s3,s4,s5,s6] # exclude s0 from all but status
   out = "SXR slits: \n"
   if (hg is not None):
      for s in all:
         s.hg.mv(hg)
         pass
      pass
   if (vg is not None):
      for s in all:
         s.vg.mv(vg)
         pass
      pass
   if (not fast):
      for s in all:
         s.wait()
         pass
      pass
   out += s0.status()+ "\n" 	
   #print s0.status() # s0 status
   for s in all:
      out += s.status()+ "\n"  	
      #print s.status()
      pass
   if elog:	
   	return out
   else:
	print out
   pass

def xrtstatus(toprint=1):
  # xraystopper
  str = ""
  str_error = ""
  stopper = xrtstopper.status()
  if ( stopper == "IN" ):
    str +=  "XRT stopper status: %s\n" % estr(stopper,color="red")
  else:
    str +=  "XRT stopper status: %s\n" % estr(stopper,color="green")
  stopper = dg1stopper.status()
  if ( stopper == "IN" ):
    str +=  "DG1 stopper status: %s\n" % estr(stopper,color="red")
  else:
    str +=  "DG1 stopper status: %s\n" % estr(stopper,color="green")
  stopper = dg2stopper.status()
  if ( stopper == "IN" ):
    str +=  "DG2 stopper status: %s\n" % estr(stopper,color="red")
  else:
    str +=  "DG2 stopper status: %s\n" % estr(stopper,color="green")

  str += "## SLITS\n"
  try:
    str += "%s\n" % sxrs1.status()
  except:
    str_error+= 'Could not check slits S1\n'
  try:
    str += "%s\n" % sxrs2.status()
  except:
    str_error+= 'Could not check slits S2\n'
  try:
    str += "%s\n" % sxrs3m.status()
  except:
    str_error+= 'Could not check slits S3m\n'
  str += "## IPMs\n"
  try:
    str += sxripm1.status()
  except:
    str_error+= 'Could not check ipm1\n'
  try:
    str += sxripm2.status()
  except:
    str_error+= 'Could not check ipm2\n'
  try:
    str += sxripm3m.status()
  except:
    str_error+= 'Could not check ipm3m\n'
  str += "## YAGs\n"
  try:
    str += sxryag1.status()
  except:
    str_error+= 'Could not check yag1\n'
  try:
    str += sxryag2.status()
  except:
    str_error+= 'Could not check yag2\n'
  try:
    str += sxryag3m.status()
  except:
    str_error+= 'Could not check yag3m\n'
  try:
    str_temp = sxrrl1.status()
    str+= "## DG1 REFERENCE LASER ##\n"
    str+=str_temp
  except:
    str_error+= 'Could not check ## DG1 REFERENCE LASER ##\n'
  try:
    str_temp=sxrlom.info(toprint=0)
    str +="## Large Offset Mono##\n"
    str+=str_temp
  except:
    str_error+= 'Could not check ##Large Offset Mono##\n'
  try:
    str_temp=sxrccm.status()
    str +="## Channel Cut Mono##\n"
    str +=str_temp
  except:
    str_error+= 'Could not check ##Channel Cut Mono##\n'
  if toprint==1:
     print str
     print str_error
  else: 
     return str,str_error

def sxrstatus(line='sxr',toprint=1):
  # xraystoppers
  str = ""
  str_error = ""
  stopper = xrtstopper.status()
  if ( stopper == "IN" ):
    str +=  "XRT stopper status: %s\n" % estr(stopper,color="red")
  else:
    str +=  "XRT stopper status: %s\n" % estr(stopper,color="green")
  stopper = dg1stopper.status()
  if ( stopper == "IN" ):
    str +=  "DG1 stopper status: %s\n" % estr(stopper,color="red")
  else:
    str +=  "DG2 stopper status: %s\n" % estr(stopper,color="green")
  stopper = dg2stopper.status()
  if ( stopper == "IN" ):
    str +=  "DG2 stopper status: %s\n" % estr(stopper,color="red")
  else:
    str +=  "DG2 stopper status: %s\n" % estr(stopper,color="green")
  if ((line=='main') or (line=='all')) :
    stopper = sxrmainstopper.status()
    if ( stopper == "IN" ):
      str +=  "MAIN line stopper status: %s\n" % estr(stopper,color="red")
    else:
      str +=  "MAIN line stopper status: %s\n" % estr(stopper,color="green")
  if ((line=='sxr') or (line=='all')) :
    stopper = sxroffstopper.status()
    if ( stopper == "IN" ):
      str +=  "OFFSET line stopper status: %s\n" % estr(stopper,color="red")
    else:
      str +=  "OFFSET line stopper status: %s\n" % estr(stopper,color="green")
  str += "## SLITS\n"
  str += "%s\n" % sxrs1.status()
  str += "%s\n" % sxrs2.status()
  if ((line=='main') or (line=='all')) :
    str += "%s\n" % sxrs3m.status()
  if ((line=='sxr') or (line=='all')) :
    str += "%s\n" % sxrs3.status()
  str += "%s\n" % sxrs4.status()
  str += "%s\n" % sxrs5.status()
  str += "%s\n" % sxrs6.status()
  str += "## IPMs\n"
  str += sxripm1.status()
  str += sxripm2.status()
  if ((line=='main') or (line=='all')) :
    str += sxripm3m.status()
  if ((line=='sxr') or (line=='all')) :
    str += sxripm3.status()
  str += sxripm4.status()
  str += sxripm5.status()
  str += "## CRL2\n"
  str += crl2.status()		
  str += "## YAGs\n"
  str += sxryag1.status()
  str += sxryag2.status()
  if ((line=='main') or (line=='all')) :
    str += sxryag3m.status()
  if ((line=='sxr') or (line=='all')) :
    str += sxryag3.status()
  str += sxryag4.status()
  str += sxryag5.status()
  str += "## DG1 REFERENCE LASER ##\n"
  #str += sxrrl1.status()
  str += "## SB1 REFERENCE LASER ##\n"
#  str += sxrrl2.status()
  str +="## Large Offset Mono\n"
  #str +=sxrlom.info(toprint=0)
  str += lom.status()	
  str +="## Channel Cut Mono\n"
  #str+=sxrccm.status()
  if toprint==1:
     print str
  else: 
     return str


def sxr_out():
# DG1 components
    str_error=''
    try:
      sxrs1(20,20)
    except:
      str_error+= 'Could not open S1\n'
    try:
      sxripm1.diode_out()
      sxripm1.target_out()
    except:
      str_error+= 'Could not move out ipm1 or targets\n'
    try:
      sxryag1.all_out()
    except:
      str_error+= 'Could not move out yag1\n'
# DG2 components
    try:
      sxrrl1.moveout()
    except:
      str_error+= 'Could not move DG2 Laser mirror out\n'
    try:
      sxrs2(20,20)
    except:
      str_error+= 'Could not open S2\n'
    try:
      sxripm2.diode_out()
      sxripm2.target_out()
    except:
      str_error+= 'Could not move out ipm2 or targets\n'
    try:
      sxryag2.all_out()
    except:
      str_error+= 'Could not move out yag2\n'
# MONO components
    try:
      sxrccm.moveout()
    except:
      str_error+= 'Could not move out ccm\n'
    try:
      sxrlom.moveout()
    except:
      str_error+= 'Could not move out lom\n'
# DG3m components
    try:
      sxrs3m(20,20)
    except:
      str_error+= 'Could not open S3m\n'
    try:
      sxripm3m.diode_out()
      sxripm3m.target_out()
    except:
      str_error+= 'Could not move out ipm3m or targets\n'
    try:
      sxryag3m.all_out()
    except:
      str_error+= 'Could not move out yag3m\n'
    print str_error
#    raw_input("all elements are out, check beam on yag3m and press enter when done...")
#    sxryag3m.all_out()
#    print "yag3m out, beam ready for CXI"




  

def sxrvacstatus():
  print ""
  print "HXX UM6 01 = %e Torr   PIP = %e Torr" % (pypsepics.get('HXX:UM6:GCC:01:PMON'),pypsepics.get('HXX:UM6:PIP:01:PMON'))
  print "HXX UM6 02 = %e Torr   PIP = %e Torr" % (pypsepics.get('HXX:UM6:GCC:02:PMON'),pypsepics.get('HXX:UM6:PIP:02:PMON'))
#  print "HX3 LOM = %e Torr   PIP = %e Torr" % (pypsepics.get('HX3:MON:GCC:01:PMON'),pypsepics.get('HX3:MON:PIP:01:PMON'))
#  print "HX3 CCM = %e Torr   PIP = %e Torr" % (pypsepics.get('HX3:MON:GCC:02:PMON'),pypsepics.get('HX3:MON:PIP:03:PMON'))
#  print "XPP SB2 = %e Torr" % pypsepics.get('XPP:SB3:GCC:01:PMON')
#  print "XPP SB3 = %e Torr   PIP = %e Torr" % (pypsepics.get('XPP:SB2:GCC:01:PMON'),pypsepics.get('XPP:SB3:PIP:01:PMON'))
#  print "XPP LAS = %e Torr" % pypsepics.get('XPP:SB3:GCC:02:PMON')
#  print "XPP SB4 = %e Torr" % pypsepics.get('XPP:SB4:GCC:01:PMON')
#  print "HX3 DVD = %e Torr   " % pypsepics.get('')



#def Bi_status():
#  print "2theta          = %f" % m.gon_r.wm()
#  print "gon (v,y)       = %f,%f" % (m.gon_v.wm(), m.gon_y.wm())
#  print "gon phi         = %f" % m.gon_phi.wm()
#  print "mono (E,alio)   = (%f,%f)" % (ccm.E,ccm.alio.wm())
#  print "delay stage     = %f" % m.las_delay1.wm()
#  print "power wp        = %f" % m.las_wvp1.wm()
#  print "polarization wp = %f" % m.las_wvp2.wm()
#  print "s2 (hpos,vpos) = %f,%f" % (s2.wm_ho(),s2.wm_vo())
#  print "s2 (hgap,vgap) = %f,%f" % (s2.wm_hg(),s2.wm_vg())
#  print "s4 (hpos,vpos) = %f,%f" % (s4.wm_ho(),s4.wm_vo())
#  print "s4 (hgap,vgap) = %f,%f" % (s4.wm_hg(),s4.wm_vg())
#  print "laser ang shift= %e" % (laser.delay())

#def Bi_scan():
#  for i in range(10):
#    lp.open()
#    print "move to 36"
#    m.las_wvp2.move_and_wait(36)
#    print "collect"
#    lp.close()
#    sxrdaq.takerun(2000); sxrdaq.disconnect()
#    lp.open()
#    print "move to 94"
#    m.las_wvp2.move_and_wait(94)
#    print "collect"
#    lp.close()
#    sxrdaq.takerun(2000); sxrdaq.disconnect()

#def speckle_status():
#  str  = "## speckle status ##\n"
#  str += "s1 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s1.wm_hg(),s1.wm_vg(),s1.wm_ho(),s1.wm_vo())
#  str += "mono (E,alio)  = (%f,%f)\n" % (ccm.E,ccm.alio.wm())
#  str += "s2 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s2.wm_hg(),s2.wm_vg(),s2.wm_ho(),s2.wm_vo())
#  str += "s3 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s3.wm_hg(),s3.wm_vg(),s3.wm_ho(),s3.wm_vo())
#  str += "Be lenses (x,y,z) = (%.4f,%.4f,%.4f)\n" % (m.Be_xpos.wm(),m.Be_ypos.wm(),m.Be_zpos.wm())
#  str += "s4 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s4.wm_hg(),s4.wm_vg(),s4.wm_ho(),s4.wm_vo())
#  str += "goniometer (x,y,z,h,v) = (%.4f,%.4f,%.4f,%.4f,%.4f)\n" % (m.gon_x.wm(),m.gon_y.wm(),m.gon_z.wm(),m.gon_h.wm(),m.gon_v.wm())
#  str += "ss : %+.0f x %+.0f; center @ (%+.0f,%+.0f)\n" % (m.sshap.wm(),m.ssvap.wm(),m.sshcen.wm(),m.ssvcen.wm())
#  str += "sample   (x,y,z) = (%f,%f,%f)\n" % (m.samx.wm(),m.samy.wm(),m.samz.wm())
#  str += "pinhole  (x,y,z) = (%f,%f,%f)\n" % (m.pinx.wm(),m.piny.wm(),m.pinz.wm())
#  str += "beamstop (x,y,z) = (%f,%f,%f)\n" % (m.beamsx.wm(),m.beamsy.wm(),m.beamsz.wm())
#  r=att.getT()
#  print str
#  str += "attenuation for 1st harm: %e\n" % (r['1st_tot'])
#  str += "attenuation for 3rd harm: %e\n" % (r['3rd_Si'])
#  logbook.submit(str,tag="status")

#def xcca_status():
#  str  = "## xcca status ##\n"
#  str += "s1 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s1.wm_hg(),s1.wm_vg(),s1.wm_ho(),s1.wm_vo())
#  str += "mono (E,alio)  = (%f,%f)\n" % (ccm.E,ccm.alio.wm())
#  str += "s2 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s2.wm_hg(),s2.wm_vg(),s2.wm_ho(),s2.wm_vo())
#  str += "s3 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s3.wm_hg(),s3.wm_vg(),s3.wm_ho(),s3.wm_vo())
#  str += "Be lenses (x,y,z) = (%.4f,%.4f,%.4f)\n" % (m.Be_xpos.wm(),m.Be_ypos.wm(),m.Be_zpos.wm())
#  str += "s4 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s4.wm_hg(),s4.wm_vg(),s4.wm_ho(),s4.wm_vo())
#  str += "goniometer (x,y,z,h,v) = (%.4f,%.4f,%.4f,%.4f,%.4f)\n" % (m.gon_x.wm(),m.gon_y.wm(),m.gon_z.wm(),m.gon_h.wm(),m.gon_v.wm())
#  str += "flow : %.4f\n" % (m.flow.wm())
#  str += "wire : %.4f\n" % (m.wire.wm()) 
#  r=att.getT()
#  print str
#  str += "attenuation for 1st harm: %e\n" % (r['1st_tot'])
#  str += "attenuation for 3rd harm: %e\n" % (r['3rd_Si'])
#  logbook.submit(str,tag="status")

#def mixing_status():
#  str  = "## mixing status ##\n"
#  str += "mono (E,alio)  = (%f,%f)\n" % (ccm.E,ccm.alio.wm())
#  str += "s1 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s1.wm_hg(),s1.wm_vg(),s1.wm_ho(),s1.wm_vo())
#  str += "s2 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s2.wm_hg(),s2.wm_vg(),s2.wm_ho(),s2.wm_vo())
#  str += "s3 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s3.wm_hg(),s3.wm_vg(),s3.wm_ho(),s3.wm_vo())
#  str += "s4 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s4.wm_hg(),s4.wm_vg(),s4.wm_ho(),s4.wm_vo())
#  str += "goniometer (h,v,r) = (%.4f,%.4f,%.4f)\n" % (m.gon_h.wm(),m.gon_v.wm(),m.gon_r.wm())
#  str += "Sample (x,y,r) : (%.4f,%.4f,%.4f)\n" % (m.samx.wm(),m.samy.wm(),m.samr.wm())
#  str += "ss1 : %+.0f x %+.0f; center @ (%+.0f,%+.0f)\n" % (m.ss1hg.wm(),m.ss1vg.wm(),m.ss1ho.wm(),m.ss1vo.wm())
#  str += "cc (r) = (%.4f)\n" % (m.cc.wm())
#  str += "ss2 : %+.0f x %+.0f; center @ (%+.0f,%+.0f)\n" % (m.ss2hg.wm(),m.ss2vg.wm(),m.ss2ho.wm(),m.ss2vo.wm())
#  str += "Laser delay (delay stage, phase shifter) = (%.4f,%.15f)\n" % (m.las_delay1.wm(), laser.delay())
#  str += "Laser waveplates (energy, polarisation) = (%.2f,%.2f)\n" % (m.las_wvp1.wm(), m.las_wvp2.wm())
#  str += "Laser compressor = (%.4f)\n" % (m.las_comp.wm())
#  str += "Laser lens (h,v) = (%.3f,%.3f)\n" % (m.las_lensh.wm(), m.las_lensv.wm())
#  r=att.getT()
#  print str
#  str += "attenuation for 1st harm: %e\n" % (r['1st_tot'])
#  str += "attenuation for 3rd harm: %e\n" % (r['3rd_Si'])
#  logbook.submit(str,tag="status")

#def marc_status():
#  str  = "## Marc status ##\n"
#  str += "s1 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s1.wm_hg(),s1.wm_vg(),s1.wm_ho(),s1.wm_vo())
#  str += "s2 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s2.wm_hg(),s2.wm_vg(),s2.wm_ho(),s2.wm_vo())
#  str += "s3 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s3.wm_hg(),s3.wm_vg(),s3.wm_ho(),s3.wm_vo())
#  str += "s4 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s4.wm_hg(),s4.wm_vg(),s4.wm_ho(),s4.wm_vo())
#  str += "goniometer (h,v,phi,samz) = (%.4f,%.4f,%.4f,%.4f)\n" % (m.gon_h.wm(),m.gon_v.wm(),m.gon_phi.wm(),m.sam_z.wm())
#  r=att.getT()
#  print str
#  str += "attenuation for 1st harm: %e\n" % (r['1st_tot'])
#  str += "attenuation for 3rd harm: %e\n" % (r['3rd_Si'])
#  logbook.submit(str,tag="status")

#def xcav_status():
#  str  = "## Xcav status ##\n"
#  str += "s1 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s1.wm_hg(),s1.wm_vg(),s1.wm_ho(),s1.wm_vo())
#  str += "s2 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s2.wm_hg(),s2.wm_vg(),s2.wm_ho(),s2.wm_vo())
#  str += "s3 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s3.wm_hg(),s3.wm_vg(),s3.wm_ho(),s3.wm_vo())
#  str += "s4 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s4.wm_hg(),s4.wm_vg(),s4.wm_ho(),s4.wm_vo())
#  str += "Xcav1 (x,y) = (%.3f,%.3f)\n" % (m.cav1x.wm(), m.cav1y.wm())
#  str += "Xcav2 (x,y) = (%.3f,%.3f)\n" % (m.cav2x.wm(), m.cav2y.wm())
#  r=att.getT()
#  print str
#  str += "attenuation for 1st harm: %e\n" % (r['1st_tot'])
#  str += "attenuation for 3rd harm: %e\n" % (r['3rd_Si'])
#  logbook.submit(str,tag="status")

#def Gregori_status():
#  str  = "## Gregori status ##\n"
#  str += "s1 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s1.wm_hg(),s1.wm_vg(),s1.wm_ho(),s1.wm_vo())
#  str += "mono (E,alio)  = (%f,%f)\n" % (ccm.E,ccm.alio.wm())
#  str += "s2 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s2.wm_hg(),s2.wm_vg(),s2.wm_ho(),s2.wm_vo())
#  str += "s3 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s3.wm_hg(),s3.wm_vg(),s3.wm_ho(),s3.wm_vo())
#  str += "Be lenses (x,y,z) = (%.4f,%.4f,%.4f)\n" % (m.Be_xpos.wm(),m.Be_ypos.wm(),m.Be_zpos.wm())
#  str += "s4 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s4.wm_hg(),s4.wm_vg(),s4.wm_ho(),s4.wm_vo())
#  str += "goniometer (x,y,z,h,v) = (%.4f,%.4f,%.4f,%.4f,%.4f)\n" % (m.gon_x.wm(),m.gon_y.wm(),m.gon_z.wm(),m.gon_h.wm(),m.gon_v.wm())
#  str += "Laser delay (delay stage, phase shifter) = (%.4f,%.15f)\n" % (m.las_delay1.wm(), laser.delay())
#  str += "Laser waveplates (energy, polarisation) = (%.2f,%.2f)\n" % (m.las_wvp1.wm(), m.las_wvp2.wm())
#  str += "Laser compressor = (%.4f)\n" % (m.las_comp.wm())
#  str += "Laser lens (h,v) = (%.3f,%.3f)\n" % (m.las_lensh.wm(), m.las_lensv.wm())
#  str += "Target (x,y,z) = (%.3f,%.3f,%.3f)\n" % (m.tpx.wm(), m.tpy.wm(), m.tpz.wm())
#  str += "CM (x,y,z) = (%.3f,%.3f,%.3f)\n" % (m.cmx.wm(), m.cmy.wm(), m.cmz.wm())
#  str += "Overlap Lens (x) = (%.3f)\n" % (m.lx.wm())
#  str += "GR (z,y) = (%.3f,%.3f)\n" % (m.grz.wm(), m.gry.wm())
#  r=att.getT()
#  print str
#  str += "attenuation for 1st harm: %e\n" % (r['1st_tot'])
#  str += "attenuation for 3rd harm: %e\n" % (r['3rd_Si'])
#  logbook.submit(str,tag="status")

#def PX_status():
#  str  = "## PX status ##\n"
#  str += "s1 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s1.wm_hg(),s1.wm_vg(),s1.wm_ho(),s1.wm_vo())
#  str += "s2 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s2.wm_hg(),s2.wm_vg(),s2.wm_ho(),s2.wm_vo())
#  str += "s3 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s3.wm_hg(),s3.wm_vg(),s3.wm_ho(),s3.wm_vo())
#  str += "Be lenses (x,y,z) = (%.4f,%.4f,%.4f)\n" % (m.Be_xpos.wm(),m.Be_ypos.wm(),m.Be_zpos.wm())
#  str += "s4 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s4.wm_hg(),s4.wm_vg(),s4.wm_ho(),s4.wm_vo())
#  str += "goniometer (h,v,phi,x,y,z) = (%.4f,%.4f,%.4f,%.4f,%.4f,%.4f)\n" % (m.gon_h.wm(),m.gon_v.wm(),m.gon_phi.wm(),m.sam_x.wm(),m.sam_y.wm(),m.sam_z.wm())
#  r=att.getT()
#  print str
#  str += "attenuation for 1st harm: %e\n" % (r['1st_tot'])
#  str += "attenuation for 3rd harm: %e\n" % (r['3rd_Si'])
#  logbook.submit(str,tag="status")


#def TRPX_status():
#  str  = "## TRPX status ##\n"
#  str += "mono (E,alio)  = (%f,%f)\n" % (ccm.E,ccm.alio.wm())
#  str += "s1 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s1.wm_hg(),s1.wm_vg(),s1.wm_ho(),s1.wm_vo())
#  str += "s2 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s2.wm_hg(),s2.wm_vg(),s2.wm_ho(),s2.wm_vo())
#  str += "s3 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s3.wm_hg(),s3.wm_vg(),s3.wm_ho(),s3.wm_vo())
#  str += "Be lenses (x,y,z) = (%.4f,%.4f,%.4f)\n" % (m.Be_xpos.wm(),m.Be_ypos.wm(),m.Be_zpos.wm())
#  str += "s4 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s4.wm_hg(),s4.wm_vg(),s4.wm_ho(),s4.wm_vo())
#  str += "goniometer (h,v,phi,x,y,z) = (%.4f,%.4f,%.4f,%.4f,%.4f,%.4f)\n" % (m.gon_h.wm(),m.gon_v.wm(),m.gon_phi.wm(),m.sam_x.wm(),m.sam_y.wm(),m.sam_z.wm())
#  r=att.getT()
#  str += "Laser delay (delay stage, phase shifter) = (%.4f,%.15f)\n" % (m.las_delay1.wm(), laser.delay())
#  str += "Laser waveplates (energy) = (%.2f)\n" % (m.las_wvp1.wm())
#  str += "Laser compressor = (%.4f)\n" % (m.las_comp.wm())
#  print str
#  str += "attenuation for 1st harm: %e\n" % (r['1st_tot'])
#  str += "attenuation for 3rd harm: %e\n" % (r['3rd_Si'])
#  logbook.submit(str,tag="status")

#def SD_status():
#  str  = "## Split & Delay status ##\n"
#  str += "mono (E,alio)  = (%f,%f)\n" % (ccm.E,ccm.alio.wm())
#  str += "s1 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s1.wm_hg(),s1.wm_vg(),s1.wm_ho(),s1.wm_vo())
#  str += "s2 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s2.wm_hg(),s2.wm_vg(),s2.wm_ho(),s2.wm_vo())
#  str += "s3 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s3.wm_hg(),s3.wm_vg(),s3.wm_ho(),s3.wm_vo())
#  str += "Be lenses (x,y,z) = (%.4f,%.4f,%.4f)\n" % (m.Be_xpos.wm(),m.Be_ypos.wm(),m.Be_zpos.wm())
#  str += "s4 : %+.4f x %+.4f; center @ (%+.4f,%+.4f)\n" % (s4.wm_hg(),s4.wm_vg(),s4.wm_ho(),s4.wm_vo())
#  str += "goniometer (x,y,z,h,v) = (%.4f,%.4f,%.4f,%.4f,%.4f)\n" % (m.gon_x.wm(),m.gon_y.wm(),m.gon_z.wm(),m.gon_h.wm(),m.gon_v.wm())
#  str += "ss : %+.0f x %+.0f; center @ (%+.0f,%+.0f)\n" % (m.sshap.wm(),m.ssvap.wm(),m.sshcen.wm(),m.ssvcen.wm())
#  str += "sample   (x,y,z) = (%f,%f,%f)\n" % (m.samx.wm(),m.samy.wm(),m.samz.wm())
#  str += "pinhole  (x,y,z) = (%f,%f,%f)\n" % (m.pinx.wm(),m.piny.wm(),m.pinz.wm())
#  str += "beamstop (x,y) = (%f,%f)\n" % (m.beamsx.wm(),m.beamsy.wm())
#  print str
#  r=att.getT()
#  str += "attenuation for 1st harm: %e\n" % (r['1st_tot'])
#  str += "attenuation for 3rd harm: %e\n" % (r['3rd_Si'])
#  logbook.submit(str,tag="status")



