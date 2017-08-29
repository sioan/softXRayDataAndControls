from utilities import notice
import pydaq
import pypsepics
import detectors
import sys
import signal
import Plot
import motor
import virtualmotor
import motor_PV
import time
from time import sleep
from numpy import abs,array,nan
import config
import KeyPress
import os
import pyami

class Daq:
  def __init__(self,host="xpp-daq",platform=0):
    self._host=host
    self._platform=platform
    self.__daq = None
    self.__scanstr = None
    self.__monitor=None
    self.__dets = None
    self.__filter_det = None
    self.__filter_min = None
    self.__filter_max = None
    self.__npulses = None
    self.__running=False
    self.issingleshot=0
    self.plot=None
    self.doplot=True
    self.record=None
    self.settling_time = 0.

  def set_monitor(self,det=None):
    if (det is None):
      self.__monitor=None
      return
    try:
      det.name
    except:
      print "The detector used for monitor is not right"
    self.__monitor = det

  def set_filter(self,*k):
    """ enable data filtering:
        usage:
        set_filter(); remove filtering
        set_filter(min,max); enable filtering between min and max on the monitor
        set_filter(det,mix,max); enable filtering using det
    """
    if len(k)==0:
      self.__filter_det = None
    if len(k) == 2 :
      self.__filter_det = self.__monitor
      self.__filter_min = k[0]
      self.__filter_max = k[1]
    if len(k) == 3 :
      self.__filter_det = k[0]
      self.__filter_min = k[1]
      self.__filter_max = k[2]

  def set_detectors(self,*dets):
    self.__dets=dets
    if len(self.__dets) == 0: self.__dets = None

  def status(self):
    s  = "DAQ status\n"
    s += "  default DETECTORS read in scan : "
    if (self.__dets is None):
      s += "  NONE\n"
    else:
      for d in self.__dets: s += " %s " % d.name
      s+="\n"
    s += "  MONITOR used for normalization : "
    if (self.__monitor is None):
      s += "  NONE\n"
    else:
      s += " %s\n" % self.__monitor.name
    s += "  FILTERING : "
    if (self.__filter_det is None):
      s += "  NONE\n"
    else:
      s += " %f<%s<%f\n" % (self.__filter_min,self.__filter_det.name,self.__filter_max)
    if (self.record is None):
      s += "  Recording RUN: selected by GUI\n"
    elif (self.record):
      s += "  Recording RUN: YES\n"
    elif (not self.record):
      s += "  Recording RUN: NO\n"
    s += "  SETTLING time after motor movement: %.3f sec\n" % self.settling_time
    return s

  def __repr__(self):
    return self.status()

  def connect(self):
    self.disconnect()
    self.__daq = pydaq.Control(self._host,self._platform)
    return self.__daq

  def disconnect(self):
    del self.__daq
    self.__daq = None

  def __check_dets(self,dets):
    try:
      if (type(dets[0]) is tuple): dets=dets[0]
    except:
      pass
    dd = []
    for i in range(len(dets)):
      if (self.__monitor != dets[i]): dd.append(dets[i])
    if (self.__dets is not None):
      for i in range(len(self.__dets)):
        if (self.__monitor != self.__dets[i]): dd.append(self.__dets[i])
    if (self.__monitor is not None):
      try :
        dd.index(self.__monitor)
      except:
        dd.append(self.__monitor)
    if (self.__filter_det is not None):
      filter_aminame = self.__filter_det.aminame
      filter_str = "%f<%s<%f" % (self.__filter_min,filter_aminame,self.__filter_max)
      for i in range(len(dd)):
        dd[i].pyamiE = pyami.Entry(dd[i].aminame,"Scalar",filter_str)
    else:
      for i in range(len(dd)):
        dd[i].pyamiE = pyami.Entry(dd[i].aminame,"Scalar")
    return dd

  def __start_av(self,dets):
    t0=time.time()
    if len(dets)!=0:
      for det in dets:
        det.connect()
        det.clear()
    if (config.TIMEIT):
      print "time needed for __start_av: %.3f" % (time.time()-t0)

  def __normalize(self,det,mon):
    try:
      det["mean"] /= mon["mean"]
      det["err"] = det["err"]/mon["mean"]+abs(det["mean"]/mon["mean"])**2*mon["err"]
    except ZeroDivisionError:
      det["mean"]=nan
      det["err"]=nan
    return det

  def __stop_av(self,dets):
    t0=time.time()
    ret = ""
    retv=dict()
    if (self.__monitor is not None):
      mon = dets[-1].get()
    if len(dets)!=0:
      for det in dets:
        v=det.get()
        det.clear()
        if ( (self.__monitor is not None) & (det != self.__monitor) ):
          v=self.__normalize(v,mon)
        retv[det]=v
        ret += "|%+11.4e %+11.4e" % (v["mean"],v["err"])
        try:
          self.__y[det].append(v["mean"])
          self.__e[det].append(v["err"])
        except:
          pass
    try:
      ret += "| %.2f" % ( float(v["entries"])/self.__npulses*100)
    except:
      pass
    if (config.TIMEIT>0):
      print "time needed for __stop_av: %.3f" % (time.time()-t0)
    return ret,retv

  def configure(self,events,controls=[],monitors=[]):
    self.connect()
    if (self.record is None):
      print "Record is what you set in GUI"
      self.__daq.configure(events=events,
                           controls=controls,monitors=monitors)
    else:
      print "Record is: " , bool(self.record)
      self.__daq.configure(record=bool(self.record),events=events,
                           controls=controls,monitors=monitors)

  def begin(self,events=None,controls=[],monitors=[]):
    if (self.__daq is None): self.configure(events,controls,monitors)
    self.__running=True
    if (events is None):
      self.__daq.begin(controls,monitors); # use default number of events set with configure
    else:
      self.__daq.begin(events=events,controls=controls,monitors=monitors)

  def wait(self):
    if (self.__running):
      self.__daq.end()
      self.__running=False

  def runnumber(self):
    if (self.__daq is not None):
      return self.__daq.runnumber()
    else:
      return 0

  def calibcycle(self,events=None,controls=[],monitors=[]):
    t0=time.time()
    self.__npulses=events
    if (self.__daq is None): self.configure(events,
            controls=controls,monitors=monitors)
    self.begin(events,controls,monitors)
    self.wait()
    tneeded = time.time()-t0
    if (config.TIMEIT>0):
      print "Daq.calibcycle: time needed for %d shots: %f" % (events,tneeded)

  def __prepare_plot(self,dets):
    plotID=1
    self.__y=dict()
    self.__e=dict()
    self.__x=[]
    for det in dets:
      self.__y[det]=[]
      self.__e[det]=[]
    return plotID

  def __prepare_dets_title(self,dets):
    line1 = ""
    line2 = ""
    for det in dets:
      line1 += "|%s" % det.name.center(23)
      line2 += "|%s" % "avg".center(11)
      line2 += " %s" % "err".center(11)
    line1+="|"
    line2+="|%pulses"
    return line1,line2

  def ct(self,sec,*dets):
    """ like spec ct (the DAQ has to be started) ... """ 
    from time import sleep
    ## take care of the detectors
    dets=self.__check_dets(dets)

    # start monitoring ...
    self.__start_av(dets)
    sleep(sec)
    rep = self.__stop_av(dets)

    print "   number of sec per point: %.3f (got" % sec,
    for det in dets:
      print " %d" % rep[1][det]["num"],
    print " shots)"
    line1,line2 = self.__prepare_dets_title(dets)
    print "%5s%s" % ('',line1)
    print "%5s%s" % ("point",line2)
    cycle = 0
    print "%5d%s" % ( (cycle+1),rep[0] )

  def takeshots_test(self,events_per_point,d):
    from xppbeamline import xppdetectors
#    self.configure(events_per_point)
    self.__start_av((d,));
    sleep(1)
    self.calibcycle(events_per_point)
    sleep(1)

  def takeshots(self,events_per_point,*dets):
    """ start a run with a certain number of events (starting/stopping the DAQ) """ 

    ## take care of the detectors
    dets=self.__check_dets(dets)
    self.configure(events_per_point)

    # Wait for the DAQ to declare 'configured'
    print "   number of shots per point: %d" % events_per_point
    print "%s" % ("point".ljust(10)),
    if len(dets)!=0:
      for det in dets:
        print " %s" % (det.name+"(avg)").ljust(14),
        print " %s" % (det.name+"(err)").ljust(14),
    print " "
    cycle=0
    t0=time.time()
    self.__start_av(dets)
    self.calibcycle( events_per_point )
    ret = self.__stop_av(dets)
    print "%s" % ("1".ljust(10)),
    print ret[0]

  def test(self,sec,*dets):
    print globals()
    print locals()
    """ like spec timescan """
    str = "xppdaq.test(%d" % sec
    for d in dets:
      str+=",d.%s" % d.name
    str +=")"
    print str
#    config.logbook.submit(str,tag="scan")

  def timescan(self,sec,*dets):
    """ like spec timescan """
    ## take care of the detectors
    dets=self.__check_dets(dets)
    ## get ready for plot
    plotid=self.__prepare_plot(dets)
    self.plot=Plot.Plot2D(plotid)
    self.__scanstr = "#   integration time per point: %.3f\n" % sec
    line1,line2 = self.__prepare_dets_title(dets)
    self.__scanstr += "#%5s%s\n" % ('',line1)
    self.__scanstr += "#%5s%s" % ("point",line2)
    print self.__scanstr,
    cycle=0
    while(1):
      # start monitoring ...
      self.__start_av(dets)
      sleep(sec)
      rep = self.__stop_av(dets)
      str = "%5d%s" % ( (cycle+1),rep[0] )
      self.__scanstr += "%s\n" % str
      self.__x.append(cycle+1)
      if (cycle>2):
        self.plot.setdata(self.__x,self.__y[dets[0]])
#        myplot.update()
      cycle=cycle+1

      

  def __ascan(self,tMot,tPos,events_per_point,dets):
    if type(tMot) is not tuple: tMot = (tMot,)
    ostr = "#%s" % self.status()
    ostr = ostr.replace("\n","\n#")
    if ( self.__monitor is not None ):
      ostr += "#readings (except for monitor) are normalized\n"
    ## take care of the motor first
    initial_pos = []
    for m in tMot: initial_pos.append( m.wm() )
    sys.stdout.flush()
    self.__scanstr= ostr
    controls = []
    for m in tMot: controls.append( (m.name,m.wm()) )
    self.configure(events_per_point,controls=controls)
    if (len(dets) != 0):
      plotid=self.__prepare_plot(dets)
      self.plot=Plot.Plot2D(plotid)
      self.plot.set_xlabel(tMot[0].name)
      self.plot.set_ylabel(dets[0].name)
    for m in tMot:
      self.__scanstr+= "#** Scanning  motor: %s (pvname: %s)\n" % (m.name,m.pvname)
    self.__scanstr+= "#   number of points: %d\n" % len(tPos)
    self.__scanstr+= "#   number of shots per point: %d\n" % events_per_point
    line1,line2 = self.__prepare_dets_title(dets)
    self.__scanstr += "%6s" % ("")
    for m in tMot: self.__scanstr += "%11s" % ("")
    self.__scanstr += "%s\n" % (line1)
    self.__scanstr += "point|"
    for m in tMot: self.__scanstr += "%11s" % ("position")
    self.__scanstr += "%s\n" % (line2)
    print self.__scanstr,
    for cycle in range(len(tPos)):
      t0cycle=time.time()
      pos = tPos[cycle];
      if ( (type(pos) is not tuple) and (type(pos) is not list) ): pos=(pos,)
      for i in range(len(pos)): tMot[i].move_silent(pos[i])
      for i in range(len(pos)): tMot[i].wait()
      sys.stdout.flush()
      if (self.settling_time != 0): sleep(self.settling_time)
      if (config.TIMEIT>0): print "time needed for moving and settling %.3f" % (time.time()-t0move)
      self.__start_av(dets)
      for m in tMot: controls.append( (m.name,m.wm()) )
      self.calibcycle( events_per_point, controls=controls )
      ret = self.__stop_av(dets)
      ostr = "%5d" % (cycle+1)
      sleep(0.05); # to make sure readback is uptodate (20ms)
      for i in range(len(pos)): ostr+="|%11.4e" % pos[i]
      ostr += "%s" % (ret[0])
      print ostr
      self.__scanstr+="%s\n" % ostr
      t0plots=time.time()
      if ( len(dets) != 0 ):
        self.__x.append(pos[0])
        if ( cycle>1 ):
          self.plot.setdata(self.__x,self.__y[dets[0]])
      if (config.TIMEIT>0): print "time needed for updating plot %.3f" % (time.time()-t0plots)
      c=KeyPress.getc()
      if (c=="q"):
        print "exiting"
        break
      if (config.TIMEIT>0): print "time needed for complete scan point %.3f" % (time.time()-t0cycle)
    for i in range(len(tMot)):
      print "Moving back %s to initial position (%e)..." % (tMot[i].name,initial_pos[i])
      tMot[i].move_silent(initial_pos[i])
    print " ... done"

  def ascan_repeat(self,mot,a,b,points,events_per_point,repeats,*dets):
    ## take care of the detectors
    dets=self.__check_dets(dets)
    pos=[]
    for i in range(repeats):
      for cycle in range(points+1):
        pos.append( (b-a)*cycle/float(points) + a )
    self.__ascan(mot,pos,events_per_point,dets)

  def __check_mot(self,mot):
    if (type(mot) is motor.Motor): m = mot
    elif (type(mot) is virtualmotor.VirtualMotor): m = mot
    elif (type(mot) is motor_PV.motorPV): m = mot
    else: m=motor_PV.motorPV(mot,mot)
    return m

  def ascan(self,mot,a,b,points,events_per_point,*dets):
    """ Scan the motor from a to b (in user coordinates) """ 
    ## take care of the detectors
    dets=self.__check_dets(dets)
    ## take care of the motor first
    # if we send a real motor
    mot = self.__check_mot(mot)
    mot_and_pos = [ ( mot,mot.wm() ) ]
    pos=[]
    for cycle in range(points+1):
      pos.append( (b-a)*cycle/float(points) + a )
    try:
      self.__ascan( mot ,pos,events_per_point,dets)
    except KeyboardInterrupt:
      self.cleanup(mot_and_pos=mot_and_pos)
    finally:
      self.cleanup(mot_and_pos=mot_and_pos)


     
  def cleanup(self,dets=None,mot_and_pos=None):
    """ mot_and_pos is a list of tuples [ (motor1,pos1), (motor2,pos2) , etc.] """
    #pypsepics.monitor_stop_all(clear=True)
    for el in mot_and_pos:
      m = el[0]; p = el[1]
      print "Moving the motor %s to initial position %.3e" % (m.name,p)
      m.move(p)
    print "Stopping scan and cleaning up"

  def a2scan(self,m1,a1,b1,m2,a2,b2,points,events_per_point,*dets):
    """ Scan the motor from a to b (in user coordinates) """ 
    ## take care of the detectors
    dets=self.__check_dets(dets)
    ## take care of the motor first; if we send a real motor
    m1 = self.__check_mot(m1)
    m2 = self.__check_mot(m2)
    mot_and_pos = [ (m1,m1.wm()), (m2,m2.wm()) ]
    pos=[]
    for cycle in range(points+1):
      p1 = (b1-a1)*cycle/float(points) + a1 
      p2 = (b2-a2)*cycle/float(points) + a2 
      pos.append( (p1,p2) )
    try:
      self.__ascan((m1,m2),pos,events_per_point,dets)
    except KeyboardInterrupt:
      self.cleanup(mot_and_pos=mot_and_pos)
    finally:
      self.cleanup(mot_and_pos=mot_and_pos)

  def a3scan(self,m1,a1,b1,m2,a2,b2,m3,a3,b3,points,events_per_point,*dets):
    """ Scan the motor from a to b (in user coordinates) """ 
    ## take care of the detectors
    dets=self.__check_dets(dets)
    ## take care of the motor first; if we send a real motor
    m1 = self.__check_mot(m1)
    m2 = self.__check_mot(m2)
    m3 = self.__check_mot(m3)
    mot_and_pos = [ (m1,m1.wm()), (m2,m2.wm()), (m3,m3.wm()) ]
    pos=[]
    for cycle in range(points+1):
      p1 = (b1-a1)*cycle/float(points) + a1 
      p2 = (b2-a2)*cycle/float(points) + a2 
      p3 = (b3-a3)*cycle/float(points) + a3 
      pos.append( (p1,p2,p3) )
    try:
      self.__ascan((m1,m2,m3),pos,events_per_point,dets)
    except KeyboardInterrupt:
      self.cleanup(mot_and_pos=mot_and_pos)
    finally:
      self.cleanup(mot_and_pos=mot_and_pos)

  def dscan(self,mot,r1,r2,points,events_per_point,*dets):
    """ Scan the motor from a to b (in user coordinates) """ 
    ## take care of the detectors
    ## take care of the motor first
    # if we send a real motor
    mot = self.__check_mot(mot); mot.wait(); p = mot.wm()
    self.ascan(mot,p+r1,p+r2,points,events_per_point,dets)

  def d2scan(self,m1,r11,r12,m2,r21,r22,points,events_per_point,*dets):
    """ Scan the motor from a to b (in user coordinates) """ 
    ## take care of the detectors
    ## take care of the motor first
    # if we send a real motor
    m1 = self.__check_mot(m1); m1.wait(); p1 = m1.wm()
    m2 = self.__check_mot(m2); m2.wait(); p2 = m2.wm()
    self.a2scan(m1,p1+r11,p1+r12,m2,p2+r21,p2+r22,points,events_per_point,dets)

  def d3scan(self,m1,r11,r12,m2,r21,r22,m3,r31,r32,points,events_per_point,*dets):
    """ Scan the motor from a to b (in user coordinates) """ 
    ## take care of the detectors
    ## take care of the motor first
    # if we send a real motor
    m1 = self.__check_mot(m1); m1.wait(); p1 = m1.wm()
    m2 = self.__check_mot(m2); m2.wait(); p2 = m2.wm()
    m3 = self.__check_mot(m3); m3.wait(); p3 = m3.wm()
    self.a3scan(m1,p1+r11,p1+r12,m2,p2+r21,p2+r22,m3,p3+r31,p3+r32,points,events_per_point,dets)


  def mesh2D(self,m1,a1,b1,n1,m2,a2,b2,n2,events_per_point,*dets):
    ## take care of the detectors
    dets=self.__check_dets(dets)
    ## take care of the motor first; if we send a real motor
    m1 = self.__check_mot(m1)
    m2 = self.__check_mot(m2)
    mot_and_pos = [ (m1,m1.wm()), (m2,m2.wm()) ]
    p1=[] 
    p2=[]
    for cycle in range(n1+1): p1.append( (b1-a1)*cycle/float(n1) + a1 )
    for cycle in range(n2+1): p2.append( (b2-a2)*cycle/float(n2) + a2 )
    pos = self.__make_mesh_motors_pos( (p1,p2) )
    try:
      self.__ascan((m1,m2),pos,events_per_point,dets)
    except KeyboardInterrupt:
      self.cleanup(mot_and_pos=mot_and_pos)
    finally:
      self.cleanup(mot_and_pos=mot_and_pos)

  def mesh3D(self,m1,a1,b1,n1,m2,a2,b2,n2,m3,a3,b3,n3,events_per_point,*dets):
    ## take care of the detectors
    dets=self.__check_dets(dets)
    ## take care of the motor first; if we send a real motor
    m1 = self.__check_mot(m1)
    m2 = self.__check_mot(m2)
    m3 = self.__check_mot(m3)
    mot_and_pos = [ (m1,m1.wm()), (m2,m2.wm()),(m3,m3.wm()) ]
    p1=[] 
    p2=[]
    p3=[]
    for cycle in range(n1+1): p1.append( (b1-a1)*cycle/float(n1) + a1 )
    for cycle in range(n2+1): p2.append( (b2-a2)*cycle/float(n2) + a2 )
    for cycle in range(n3+1): p3.append( (b3-a3)*cycle/float(n3) + a3 )
    pos = self.__make_mesh_motors_pos( (p1,p2,p3) )
    try:
      self.__ascan((m1,m2,m3),pos,events_per_point,dets)
    except KeyboardInterrupt:
      self.cleanup(mot_and_pos=mot_and_pos)
    finally:
      self.cleanup(mot_and_pos=mot_and_pos)


  def __make_mesh_motors_pos(self,tPos):
    pos = []
    if len(tPos)==1:
      for p0 in tPos[0]:
        pos.append( [p0] )
    elif len(tPos)==2:
      for p0 in tPos[0]:
        for p1 in tPos[1]:
          pos.append( [p0,p1] )
    elif len(tPos)==3:
      for p0 in tPos[0]:
        for p1 in tPos[1]:
          for p2 in tPos[2]:
            pos.append( [p0,p1,p2] )
    return pos


  def savetxt(self,fname):
    str = "# xpppython scan #\n"
    if ( self.__monitor is None ):
      str += "# Not normalized\n"
    else:
      str += "# normalization monitor: %s\n" % self.__monitor.name
      str += "# readings (except for monitor) are normalized\n"
    str += self.__scanstr.replace("|"," ")
    f=open(fname,"w")
    f.write(str)
    f.close()

  def restartDAQ(self):
    answer=raw_input("Sure ?\n")
    if (answer[0].lower()=="y"):
      os.system('source /reg/g/pcds/dist/pds/xpp/scripts/restart_xpp_daq.csh')

  def bringup(self):
    os.system('/reg/neh/operator/xppopr/bin/xpp_cleanup_windows_daq')

