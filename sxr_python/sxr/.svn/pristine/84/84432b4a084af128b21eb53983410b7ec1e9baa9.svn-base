from periodictable import xsf
from periodictable import formula as ptable_formula
import numpy as np
import sys
import utilities as util
import pypsepics
from pypslog import logprint
from time import sleep

def getAttLen(E,material="Si",density=None):
  """ get the attenuation length (in meter) of material (default Si), if no
      parameter is given for the predefined energy;
      then T=exp(-thickness/att_len); E in keV"""
  att_len = float(xsf.attenuation_length(material,density=density,energy=E))
  return att_len

def calcTrasmissionForList(att_list,E):
  T=1
  for a in att_list: T*=a.transmission(E)
  return T

def calcTrasmissionForThick(d,E,material="Si",density=None):
  """ returns transmission for a given thickness (in meter);
      E is in keV
      material can also be a compund (like SiO2)
      density: in gr/cm^3; if abset default is used; no defaults for compounds
  """
  att_len = getAttLen(E,material,density)
  return np.exp(-d/att_len)

def findFiltersForTrasm(att_list,transmission,E):
  """ Determines which filters have to be moved in the beam to
      achieve a transmission as close as possible to the requested one.
  Note : the function does not move the filters
       to use for calculation"""
  tobe_in  = []
  tobe_out = []
  n = len(att_list)
  deltaT_min = 1e35
  for i in range(1<<n):
    conf = util.dec2bin(i)
    d = 0
    T=1
    for s in range(len(conf)):
      if (conf[-(s+1)] == "1"):
        T *= att_list[s].transmission(E)
    deltaT = abs(T-transmission)
#    print d_needed,conf,d,dist,dist_min
    if (deltaT < deltaT_min):
      deltaT_min=deltaT
#      print d_needed,d,conf,dist_min
      conf_min = conf
  for s in range(len(conf_min)):
    if (conf_min[-(s+1)] == "1"):
      tobe_in.append(att_list[s])
    else:
      tobe_out.append(att_list[s])
  for s in range(len(conf_min),n):
    tobe_out.append(att_list[s])
  return (tobe_in,tobe_out)


def moveIN(att_list,fast=0):
  """ move filters define by the tuple tobe_in in the beam """
  for f in att_list: f.movein()
  if (not fast):
#    sleep(0.3)
    wait(att_list)

def moveOUT(att_list,fast=0):
  """ move filters define by the tuple tobe_in out the beam, the others out """
  for f in att_list: f.moveout()
  if (not fast):
#    sleep(0.3)
    wait(att_list)

def wait(att_list): 
  for f in att_list: f.wait()

def check_filters_position(att_list):
  """ Check which filters are `in` and return a list """
  n = len(att_list)
  list_in = []
  list_out = []
  list_unknown = []
  for i in range(n):
    if att_list[i].isin():
      list_in.append(i)
    elif att_list[i].isout():
      list_out.append(i)
    else:
      list_unknown.append(i)
  return (list_in,list_out,list_unknown)


def getT(att_list,E,printit=1):
  """ Check which filters are `in` and calculate the transmission
      for the energy defined with the `setE` command
      The finding is returned as dictionary """
  wait(att_list)
  n=len(att_list)
  (fin,fout,funknown)=check_filters_position(att_list)
  att_list_in=[]
  s_title = "filter# |"
  for i in range(n):
    s_title += "%d|" % i
  s_in    = " IN     |"
  s_out   = " OUT    |"
  ret = dict()
  for i in range(n):
    if i in fin:
      att_list_in.append(att_list[i])
      s_in +="X|"
      s_out+=" |"
    elif (i in fout):
      s_in +=" |"
      s_out+="X|"
    else:
      s_in +="?|"
      s_out+="?|"
  T = calcTrasmissionForList(att_list_in,E)
  if (E<12.500):
    T3rd = calcTrasmissionForList(att_list_in,E*3)
    ret['1st_Si'] = T
    ret['3rd_Si'] = T3rd
    s  = "Transmission for 1st harmonic (E= %.2fkeV): %.3e\n" % (E,T)
    s += "Transmission for 3rd harmonic (E=%.2fkeV): %.3e\n" % (E*3,T3rd)
  else:
    T1st = calcTrasmissionForList(att_list_in,E/3)
    ret['1st_Si'] = T1st
    ret['3rd_Si'] = T
    s  = "Transmission for 1st harmonic (E= %.2fkeV): %.3e\n" % (E/3,T1st)
    s += "Transmission for 3rd harmonic (E=%.2fkeV): %.3e\n" % (E,T)
  ret["E"]=T
  sret = s_title + "\n" + s_out + "\n" + s_in + "\n" + s
  if (printit):
    print sret
  return (ret,sret)

def getTvalue(att_list,E):
  """ returns float with current transmission. (for the energy previously set)
  """
  (ret,todel) = getT(att_list,E,printit=0)
  return ret["E"]

def setTfast(att_list,transmission,E,printit=1,domove=1):
  """ as setT but it dows not wait for motors ... (and IN and OUT commands
      are sent at the sae time"""
  setT(att_list,transmission,E,fast=True,printit=printit,domove=domove)

def setT(att_list,transmission,E,fast=False,printit=1,domove=1):
  """ Determines which filters have to be moved in othe beam to
      achieve a transmission as close as possible to the requested one.
Note : the function moves the filters
Note2: use the `setE` command before to choose which energy 
       to use for calculation"""
  (tobe_in,tobe_out) = findFiltersForTrasm(att_list,transmission,E)
  if (domove):
    if (printit): util.printnow("Moving attenuators IN")
    moveIN(tobe_in,fast=fast)
    if (printit): util.printnow("... done\n")
    if (printit): util.printnow("Moving attenuators OUT")
    moveOUT(tobe_out,fast=fast)
    if (printit): util.printnow("... done\n")
  T =calcTrasmissionForList(tobe_in,E)
  T3=calcTrasmissionForList(tobe_in,E*3)
  if (printit and (not fast)):
    sleep(0.5)
    getT(att_list,E)
  return (T,T3)
