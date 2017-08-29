#!/usr/bin/env python

import sys
import os
import subprocess

def caput(pv, value_list, terse=False, verbose=True):
    pv = str(pv)

    if verbose:
      if isinstance(value_list, (list,tuple)):
        print( "Set %s := [len = %d] %s" % ( pv, len(value_list), ' '.join(map(str,value_list)) ) )
      else:
        print( "Set %s := %s" % ( pv, str(value_list) ) )

    if isinstance(value_list, (list,tuple)):
      value_list = [str(v) for v in value_list]
    else:
      value_list = [str(value_list)]

    args = ['caput', pv]
    
    if len(value_list) > 1:
        args.insert(1, '-a')
        args.append(str(len(value_list)))
    
    if terse:
        args.insert(1, '-t')
    
    args.extend(value_list)

# !! debug
#return ""
    iMaxTry = 3
    iTry    = 0
    while iTry < iMaxTry:        
	process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutdata, stderrdata) = process.communicate()

        if process.returncode == 0: break

        iTry += 1
        #print "** caput %s failed: %s [%d times]" % (pv, stderrdata, iTry)

    if iTry >= iMaxTry:
        print "** caput %s failed [total %d times]" % (pv, iTry)
        return stderrdata

    if iTry > 0:
        print "** caput %s failed %d times, but recovered later" % (pv, iTry)
        pass

    return stdoutdata.strip()

def caget(pv, bGetNumEnum = False):
    pv = str(pv)
    
    if bGetNumEnum:
        args = ['caget', '-n', pv]
      
    else:
      args = ['caget', pv]

    iMaxTry = 3
    iTry    = 0
    while iTry < iMaxTry:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutdata, stderrdata) = process.communicate()

        if process.returncode == 0: break

        iTry += 1
        #print "** caget %s failed: %s [%d times]" % (pv, stderrdata, iTry)

    if iTry >= iMaxTry:
        print "** caget %s failed [total %d times]" % (pv, iTry)
        return stderrdata

    if iTry > 0:
        #print "** caget %s failed %d times, but recovered later" % (pv, iTry)
        pass

    v = stdoutdata.strip().split()

    if not v[1].isdigit():
      return " ".join( v[1:] )

    if len(v) < 3:
      return v[1]

    return v[2:]

def setMotorPv(pvMotor=None, value=None):
  if pvMotor == None or value == None:
    return
  # Set the value twice to ensure the update of position
  for i in [0,1]:
    caput(pvMotor+".VAL",value)
    # wait for motion to be completed
    while True:
      if 1 == int( caget(pvMotor+".DMOV") ): break
      sleep(0.1)

def setScanPv(pvScan=None, value=None, tolerance=None):
  if pvScan == None or value == None or tolerance == None:
    return
  # Set the value twice to ensure the update of value
  for i in [0,1]:
    if abs( value - float(caget(pvScan+".RBV")) ) <= tolerance : break
    caput(pvScan+".VAL",value)
    sleep(0.1)

def arrestMotorPv(pvMotor=None, value=None, oldvalues = None):
  if pvMotor == None or value == None or oldvalues == None:
    return
  oldvalues[0]=caget(pvMotor+".LLM")
  oldvalues[1]=caget(pvMotor+".HLM")
  rbv = caget(pvMotor+".RBV")
  caput(pvMotor+".LLM",rbv)
  caput(pvMotor+".HLM",rbv)

def unarrestMotorPv(pvMotor=None, value=None, oldvalues = None):
  if pvMotor == None or value == None or oldvalues == None:
    return
  caput(pvMotor+".LLM",oldvalues[0])
  caput(pvMotor+".HLM",oldvalues[1])

