from common.motor import Motor as psmotor
import pyca
from caget import caget
from caput import caput
from Pv import Pv

SXR_MOTOR_PREFIXES = ["HXX", "HFX", "SXR"]


class SXRMotors(object):
  def get_motors(self, sxronly=True, nonuser=True, smartonly=True):
    motors=[]
    #print "retrieving motors"
    mots = self.__dict__.keys()
    mots.sort()
    for name in mots:
      m = self.__dict__[name] 
      if isinstance(m,psmotor):
        pvname = m.pvname
        pvfields = pvname.split(':')
        if sxronly and pvfields[0] not in SXR_MOTOR_PREFIXES:
          #print "Skipping '%s', not SXR" % m.name
          continue
        elif nonuser and pvfields[1] == "USR":
          #print "Skipping '%s', User motor" % m.name
          continue
        elif smartonly and pvfields[2] not in ["MMS","CLZ"]:
          #print "Skipping '%s', not MMS" % m.name
          continue
        else:
          #print "Adding '%s'" % m.name
          motors.append(m)
          pass
        pass
      pass
    return motors

  def clear_all_pu(self, nonuser=True):
    from common import pypsepics
    mots = self.get_motors(nonuser=nonuser)
    for m in mots:
      print m.name,":"
      try:
        pu = pypsepics.get("%s:PU"%m.pvname)
        if not pu:
          print "Ok, pu=",pu
        else:
          print "PU=",pu," resetting..."
          pypsepics.put("%s:SET_PU"%m.pvname,0)
          pu = pypsepics.get("%s:PU"%m.pvname)
          if not pu:
            print "Ok, pu=",pu
          else:
            print "Failed! pu=",pu
            pass
          pass
        pass
      except Exception, ex:
        print ex
          

  def display(self, motors, *fields):
    from caget import caget
    from pyca import pyexc
    fc = len(fields)
    mc = len(motors)
    lines=[["motor name"]+list(fields)]
    cw = [0]*(fc+1)
    for fi in range(fc):
      cw[fi] = len(fields[fi])
      
    for mi in range(mc):
      m = motors[mi]
      line=[m.name]+[""]*fc
      try:
        pvname = m.pvname
        try:
          for fi in range(fc):
            v = repr(caget(pvname+"."+motor.motor_params[fields[fi]][0]))
            line[fi+1] = v
            pass
          pass
        except pyexc, e:
          pass
        finally:
          for i in range(len(line)):
            vw = len(line[i])
            if vw > cw[i]:
              cw[i] = vw
              pass
            pass
          pass
        lines.append(line)
        pass
      finally:
        pass
      pass
    format = ""
    for w in cw:
      format+="   %-"+str(w)+"s"
      pass
    for line in lines:
      print format % tuple(line)
      pass
    pass

  def save_motors(self, motors):
    i=0
    im=len(motors)
    for m in motors:
      er_pvname = m.pvname+":ER"
      er_pv = Pv(er_pvname)
      er_pv.connect(5)
      er_clr_pv = Pv(m.pvname+":CLR_ER")
      er_clr_pv.connect(5)
      er_pv.get(timeout=5)
      pyca.pend_io(5)
      er_old = er_pv.data['value']
      
      pyca.pend_io(5)
      er_pv.get(timeout=5)
      pyca.pend_io(5)
      er_new = er_pv.data['value']
      print "%3d/%3d   %-15s   %2s   %2s" % (int(i+1),im,m.name, str(er_old), str(er_new))
      i+=1
      pass
    pass
    

  def __init__(self):

    self.test1 = psmotor("SXR:TST:MMS:01","TEST_1",
                         readbackpv="SXR:TST:MMS:01.RBV")
    self.test2 = psmotor("SXR:TST:MMS:02","TEST_2",
                         readbackpv="SXR:TST:MMS:02.RBV")
    
    pass

