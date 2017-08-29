import numpy
import pypsepics
from pyca import pyexc
import utilities
import sys
import os
from pypslog import logprint
from time import sleep


motor_params = {
   'acceleration':    ('ACCL', 'acceleration time'),
   'back_accel':      ('BACC', 'backlash acceleration time'),
   'backlash':        ('BDST', 'backlash distance'),
   'back_speed':      ('BVEL', 'backlash speed'),
   'card':            ('CARD', 'Card Number '),
   'dial_high_limit': ('DHLM', 'Dial High Limit '),
   'direction':       ('DIR',  'User Direction '),
   'dial_low_limit':  ('DLLM', 'Dial Low Limit '),
   'settle_time':     ('DLY',  'Readback settle time (s) '),
   'done_moving':     ('DMOV', 'Done moving to value'),
   'dial_readback':   ('DRBV', 'Dial Readback Value'),
   'description':     ('DESC', 'Description'),
   'dial_drive':      ('DVAL', 'Dial Desired Value'),
   'units':           ('EGU',  'Engineering Units '),
   'encoder_step':    ('ERES', 'Encoder Step Size '),
   'freeze_offset':   ('FOFF', 'Offset-Freeze Switch '),
   'move_fraction':   ('FRAC', 'Move Fraction'),
   'hi_severity':     ('HHSV', 'Hihi Severity '),
   'hi_alarm':        ('HIGH', 'High Alarm Limit '),
   'hihi_alarm':      ('HIHI', 'Hihi Alarm Limit '),
   'high_limit':      ('HLM',  'User High Limit  '),
   'high_limit_set':  ('HLS',  'High Limit Switch  '),
   'hw_limit':        ('HLSV', 'HW Lim. Violation Svr '),
   'home_forward':    ('HOMF', 'Home Forward  '),
   'home_reverse':    ('HOMR', 'Home Reverse  '),
   'high_op_range':   ('HOPR', 'High Operating Range'),
   'high_severity':   ('HSV',  'High Severity '),
   'integral_gain':   ('ICOF', 'Integral Gain '),
   'jog_accel':       ('JAR',  'Jog Acceleration (EGU/s^2) '),
   'jog_forward':     ('JOGF', 'Jog motor Forward '),
   'jog_reverse':     ('JOGR', 'Jog motor Reverse'),
   'jog_speed':       ('JVEL', 'Jog Velocity '),
   'last_dial_val':   ('LDVL', 'Last Dial Des Val '),
   'low_limit':       ('LLM',  'User Low Limit  '),
   'low_limit_set':   ('LLS',  'At Low Limit Switch'),
   'lo_severity':     ('LLSV', 'Lolo Severity  '),
   'lolo_alarm':      ('LOLO', 'Lolo Alarm Limit  '),
   'low_op_range':    ('LOPR', 'Low Operating Range '),
   'low_alarm':       ('LOW', ' Low Alarm Limit '),
   'last_rel_val':    ('LRLV', 'Last Rel Value  '),
   'last_dial_drive': ('LRVL', 'Last Raw Des Val  '),
   'last_SPMG':       ('LSPG', 'Last SPMG  '),
   'low_severity':    ('LSV',  'Low Severity  '),
   'last_drive':      ('LVAL', 'Last User Des Val'),
   'soft_limit':      ('LVIO', 'Limit violation  '),
   'in_progress':     ('MIP',  'Motion In Progress '),
   'missed':          ('MISS', 'Ran out of retries '),
   'moving':          ('MOVN', 'Motor is moving  '),
   'resolution':      ('MRES', 'Motor Step Size (EGU)'),
   'motor_status':    ('MSTA', 'Motor Status  '),
   'offset':          ('OFF',  'User Offset (EGU) '),
   'output_mode':     ('OMSL', 'Output Mode Select  '),
   'output':          ('OUT',  'Output Specification '),
   'power_up':        ('PU',   'Power Cycled '),
   'prop_gain':       ('PCOF', 'Proportional Gain '),
   'precision':       ('PREC', 'Display Precision '),
   'readback':        ('RBV',  'User Readback Value '),
   'retry_max':       ('RTRY', 'Max retry count    '),
   'retry_count':     ('RCNT', 'Retry count  '),
   'retry_deadband':  ('RDBD', 'Retry Deadband (EGU)'),
   'dial_difference': ('RDIF', 'Difference rval-rrbv '),
   'raw_encoder_pos': ('REP',  'Raw Encoder Position '),
   'raw_high_limit':  ('RHLS', 'Raw High Limit Switch'),
   'raw_low_limit':   ('RLLS', 'Raw Low Limit Switch'),
   'relative_value':  ('RLV',  'Relative Value    '),
   'raw_motor_pos':   ('RMP',  'Raw Motor Position '),
   'raw_readback':    ('RRBV', 'Raw Readback Value '),
   'readback_res':    ('RRES', 'Readback Step Size (EGU)'),
   'raw_drive':       ('RVAL', 'Raw Desired Value  '),
   'run_current':     ('RC',   'Run Current  '),  
   'dial_speed':      ('RVEL', 'Raw Velocity '),
   's_speed':         ('S',    'Speed (RPS)  '),
   's_back_speed':    ('SBAK', 'Backlash Speed (RPS)  '),
   's_base_speed':    ('SBAS', 'Base Speed (RPS)'),
   's_max_speed':     ('SMAX', 'Max Velocity (RPS)'),
   'set':             ('SET',  'Set/Use Switch '),
   'stop_go':         ('SPMG', 'Stop/Pause/Move/Go '),
   's_revolutions':   ('SREV', 'Steps per Revolution '),
   'stop':            ('STOP', 'Stop  '),
   't_direction':     ('TDIR', 'Direction of Travel '),
   'tweak_forward':   ('TWF',  'Tweak motor Forward '),
   'tweak_reverse':   ('TWR',  'Tweak motor Reverse '),
   'tweak_val':       ('TWV',  'Tweak Step Size (EGU) '),
   'use_encoder':     ('UEIP', 'Use Encoder If Present'),
   'u_revolutions':   ('UREV', 'EGU per Revolution  '),
   'use_rdbl':        ('URIP', 'Use RDBL Link If Present'),
   'drive':           ('VAL',  'User Desired Value'),
   'base_speed':      ('VBAS', 'Base Velocity (EGU/s)'),
   'slew_speed':      ('VELO', 'Velocity (EGU/s) '),
   'version':         ('VERS', 'Code Version '),
   'max_speed':       ('VMAX', 'Max Velocity (EGU/s)'),
   'use_home':        ('ATHM', 'uses the Home switch'),
   'deriv_gain':      ('DCOF', 'Derivative Gain '),
   'use_torque':      ('CNEN', 'Enable torque control '),
   'device_type':     ('DTYP', 'Device Type'),
   'record_type':     ('RTYP', 'Record Type'),
   'status':          ('STAT', 'Status')
}

class Motor(object):
  """ 
  motor module
  define a new motor as 
  mymot = motor("XPP:SB2:MMS:10",name="mymotname")
 
  Usage example:

  -> ASK POSITION  <-
  mymot.wm();        # returns current user position
  mymot.wm_string(); # returns current user position as string
  mymot.wm_dial();   # returns current dial position
  mymot.wm_raw();    # returns current motor number of steps

  -> MOVE ABSOLUTE (user value) <-
  mymot.move(3);
  mymot.mv(3);           # as above
  mymot.move_silent(3);  # don't write anything to terminal, good for macros
  mymot.update_move(3);  # show changing postion
  mymot.umv(3);          # show changing postion

  -> MOVE RELATIVE (user value) <-
  mymot.move_relative(2);
  mymot.mvr(2);                  # as above
  mymot.update_move_relative(2); # show changing position
  mymot.umvr(2)                  # show changing position

  -> ASK/CHANGE STATUS <-
  mymot.set(4)          # call current position 4 in user coordinates
  mymot.set_dial(4)     # call current dial position 4 leaving the .OFF unaltered
  mymot.ismoving();     # True if moving
  mymot.stop();         # Send a stop command
  mymot.[get/set]_speed # to change or retrieve current speed (in EGU/s)
    
  """
  def __init__(self,pvname,name=None,readbackpv="default",home="low",writepv=None):
    self.__name__   = "xpp motor class"
    self.pvname     = pvname
    if (name is None): name = self.get_par("description")
    self.name       = name
    if (home is None): home = ""
    self.__home = home
    self.__writepv = writepv
    if (readbackpv is None):
      self.readback   = pvname
    elif (readbackpv == "default"):
      self.__readbackpv   = pvname + ".RBV"
    else:
      self.__readbackpv   = readbackpv
    self.__dialpv       = pvname + ".DVAL"
    # keep local copy of .VAL to avoid slow IOC not updating fast enough
    self.__user_desidered_pos = None;

  def expert_screen(self):
    """ Opens Epics motor expert screen for resetting motor after e.g. stalling"""
    os.system('~sxropr/bin/motor-expert-screen.sh '+self.pvname)
    

  def home(self,ask=True,move_motor_back=True):
    if (self.__home != ("low" or "high")):
      print "no home position defined for motor %s (pv %s), returning" % (self.name,self.pvname)
      return
    orig_user_pos = self.wm()
    orig_speed    = self.get_speed()
    dial_offset = 100; # in EGU
    move_away   = 5000; # in motor steps
    resolution = self.get_par("resolution")
    if (self.__home == "low"):
      set_dial_f  = self.set_dial_lowlim
      diallim   = self.get_dial_lowlim()
      sign = -1
    elif (self.__home == "high"):
      set_dial_f  = self.set_dial_highlim
      diallim   = self.get_dial_highlim()
      sign = 1
    else:
      print "inconsistent state in home, aborting"
      return
    try:
      set_dial_f(diallim+sign*dial_offset)
      self.move_dial(diallim+sign*0.99*dial_offset)
      lim = self.wait_for_switch()
      dial_at_lim = self.wm_dial()
      if (lim != self.__home):
          print "Asked for %s limit switch, got %s, aborting" % (self.__home,lim)
          return
      print "Reached %s limit switch, current dial %f" % (self.__home,dial_at_lim)
      raw_input()
      self.move_dial(dial_at_lim-sign*move_away*resolution); # move a bit away from limit
      self.wait()
      self.set_speed(self.get_par("base_speed")); # use base speed as low speed option
      raw_input()
      self.move_dial(dial_at_lim+sign*2*move_away*resolution); # move back to limit switch
      raw_input()
      lim = self.wait_for_switch()
      raw_input()
      dial_at_lim = self.wm_dial()
      print "Reached %s limit switch, current dial %f" % (self.__home,dial_at_lim)
      if (ask):
        repl = raw_input("Motor %s (pv %s) is now at %s limit switch, want to set the dial to zero ? [y/n]\n" % (self.name,self.pvname,self.__home))
        if (repl.lower()[0] == "y"):
          self.set_dial(0)
        else:
          print "exiting living the motor at limit switch (setting soflimit to zero here)"
          set_dial_f(0)
          return
      set_dial_f(0)
      print "homing procedure for motor %s (pv %s) finished" % (self.name,self.pvname)
    finally:
      self.set_speed(orig_speed)
      if (move_motor_back):
        self.move(orig_user_pos)
        print "moving motor back to original position (%f)" % self.wm()
        
   
  def wait_for_switch(self):
    lim = self.check_limit_switches()[0]
    while (self.check_limit_switches()[0] == "ok"):
      utilities.notice("waiting for limit seitch of motor %s (pv %s)" % (self.name,self.pvname))
      sleep(0.2)
    return self.check_limit_switches()[0]
    

  def __call__(self,value):
    """ Shortcut for move, for example: m.gonx(4) """
    self.move(value)

  def __repr__(self):
    return self.status()

  def status(self):
    """ return info for the current motor"""
    str  = "%s\n\tpv %s\n" % (self.name,self.pvname)
    str += "\tcurrent position (user,dial): %f,%f" % (self.wm(),self.wm_dial())
    return str

#  def __repr__(self):
#    """ return info for the current motor, useful to use as: m.gonx (+Enter)"""
#    return self.status()

  def __str__(self):
    """ short string representation of motor """
    return "%s @ user %s" % (self.name,self.wm_string())

  # functions for user position
  def wm_desired_user(self):
    if (self.__user_desidered_pos is None):
      return self.get_par("drive")
    else:
      return self.__user_desidered_pos

  def wm(self):
    """ returns readback position as float number"""
    return pypsepics.get(self.__readbackpv)
  def wm_offset(self):
    """ returns .OFF PV"""
    return self.get_par("offset")

  def wm_string(self):
    """ returns readback position as string with the right number of decimals"""
    prec = int(self.get_par("precision"))
    format = "%%0.%df" % prec
    return format % self.wm()

  def move_silent(self,value):
    return self.move(value)

  def move(self,value):
    self.__user_desidered_pos = value
    if (numpy.isnan(value)):
      logprint("Problem interpreting requested position for motor %s (pv %s)... not continuing" % (self.name,self.pvname), print_screen=1)
      return self.wm()
    if ( (value<self.get_lowlim()) or (value>self.get_hilim()) ):
      logprint("Asked to move %s (pv %s) outside limit, aborting" % (self.name,self.pvname),print_screen=1)
      return self.wm()
    (status,msg) = self.check_limit_switches()
    if ( (status == "high") and (value>self.wm() ) ):
      logprint(msg+",aborting",print_screen=1)
      return self.wm()
    elif ( (status == "low") and (value<self.wm() ) ):
      logprint(msg+",aborting",print_screen=1)
      return self.wm()
    logprint("moving %s (pv %s) to %f, previous position: %f" % (self.name,self.pvname,value,self.wm()))
    if self.__writepv is not None:
      return pypsepics.put(self.__writepv,value)
    else:
      return pypsepics.put(self.pvname,value)

  def check_limit_switches(self):
    if self.get_par("low_limit_set"):
      return ("low","low limit switch for motor %s (pv %s) activated" % (self.name,self.pvname))
    elif (self.get_par("high_limit_set")):
      return ("high","high limit switch for motor %s (pv %s) activated" % (self.name,self.pvname))
    else:
      return ("ok","")

#  user = property(wm,move)
  def mv(self,value): self.move(value)

  def update_move(self,value):
    """ move motor to value while displaying motor position
        Crtl + C stops motor """
    self.move(value)
    sleep(0.1)
    try:
      while ( not self.__isthere() ):
        s = "motor position: %s" % self.wm_string()
        utilities.notice(s)
        sleep(0.05)
    except KeyboardInterrupt:
      print "Ctrl + C pressed. Stopping motor"
      self.stop()
      sleep(1)
    s = "motor position: %s" % self.wm_string()
    utilities.notice(s)
    print ""

  def umv(self,value): self.update_move(value)

  # courtesy of XPP
  def mv_ginput(self,ElogQuestion=True):
    from pylab import ginput
    oldpos = self.wm()
    print "Select x-position in current plot by mouseclick\n"
    pos = ginput(1)[0][0]
    print "...moving %s to %g" %(self.name,pos)
    self.umv(pos)
    if ElogQuestion:
      if raw_input('Would you like to send this move to the logbook? (y/n)\n') is 'y':
        elogStr = "Moved %s from %g by %g to %g." %(self.name,oldpos,pos-oldpos,pos)
        config.Elog.submit(elogStr)

  # courtesy of XPP
  def mv_elog(self,value,ElogQuestion=True):
    oldpos = self.wm()
    print "...moving %s to %g" %(self.name,value)
    self.umv(value)
    if ElogQuestion:
      if raw_input('Would you like to send this move to the logbook? (y/n)\n') is 'y':
        elogStr = "Moved %s from %g by %g to %g." %(self.name,oldpos,value-oldpos,value)
        config.Elog.submit(elogStr)

  # courtesy of XPP
  def mvr_elog(self,value,ElogQuestion=True):
    oldpos = self.wm()
    print "...moving %s to %g" %(self.name,value)
    self.umvr(value)
    newpos = self.wm()
    if ElogQuestion:
      if raw_input('Would you like to send this move to the logbook? (y/n)\n') is 'y':
        elogStr = "Moved %s from %g by %g to %g." %(self.name,oldpos,value,newpos)
        config.Elog.submit(elogStr)


  

  # limits functions
  def get_hilim(self):
    return self.get_par("high_limit")
  def set_hilim(self,value):
    self.put_par("high_limit",value)
  def get_lowlim(self):
    return self.get_par("low_limit")
  def set_lowlim(self,value):
    self.put_par("low_limit",value)
  def get_dial_hilim(self):
    return self.get_par("dial_high_limit")
  def set_dial_hilim(self,value):
    self.put_par("dial_high_limit",value)
  def get_dial_lowlim(self):
    return self.get_par("dial_low_limit")
  def set_dial_lowlim(self,value):
    self.put_par("dial_low_limit",value)

  # functions for dial position
  def wm_desired_dial(self):
    return self.get_par("dial_drive")
  def wm_dial(self):
    return self.get_par("dial_readback")

  def move_dial(self,value):
    try:
      if ( (value<self.get_dial_lowlim()) or (value>self.get_dial_hilim()) ):
        logprint("Asked to move %s (pv %s) outside limit, aborting" % (self.name,self.pvname),print_screen=1)
        return self.wm_dial()
      (status,msg) = self.check_limit_switches()
      if ( (status == "high") and (value>self.wm_dial() ) ):
        logprint(msg,print_screen=1)
        return self.wm_dial()
      elif ( (status == "low") and (value<self.wm_dial() ) ):
        logprint(msg,print_screen=1)
        return self.wm_dial()
    except:
      pass
    return pypsepics.put(self.__dialpv,value)
#  dial = property(wmdial,move_dial)

  # functions for raw position
  def wm_raw(self):
    return self.get_par("raw_drive")
  def move_raw(self,value):
    return self.put_par("raw_drive",value)
#  raw = property(get_raw,set_raw)

  # functions for speed
  def get_speed(self):
    """ return the speed (.VELO) in EGU/s """
    return self.get_par("slew_speed")

  def set_speed(self,value):
    """ set the speed (.VELO) in EGU/s """
    return self.put_par("slew_speed",value)
#  speed = property(get_speed,set_speed)

  def move_relative(self,howmuch):
    current = self.wm()
    if (numpy.isnan(current)):
      logprint("Problem retreiving current position for motor %s (pv %s)... not continuing" % self.name,self.pvname)
      return None
    else:
      return self.move(current+howmuch)

  def mvr(self,howmuch): self.move_relative(howmuch)

  def update_move_relative(self,howmuch):
    pos = self.wm()
    self.update_move(pos+howmuch)

  def umvr(self,howmuch): self.update_move_relative(howmuch)

  def stop(self):
    self.put_par("stop",1)

  def ismoving(self):
    return (not pypsepics.get(self.pvname + ".DMOV"))

  def __isthere(self):
    deadband = self.get_par("retry_deadband")
    usergoto = self.wm_desired_user()
    delta=abs(usergoto-self.wm())
    return  ( delta<10*deadband and not self.ismoving() )

  def wait(self):
    #print pypsepics.get(self.pvname + ".VAL")
    deadband = self.get_par("retry_deadband")
    usergoto = self.wm_desired_user()
    delta=abs(usergoto-self.wm())
    if (  delta<deadband ): return
    sleep(0.02)
    while ( not self.__isthere() ):
      sleep(0.01)

  def __sign(self):
    dir = self.get_par("direction"); # 1 means inverted
    if (dir == 1):
      return -1
    elif (dir == 0):
      return 1
    else:
      return None

  def set_dial(self,value=0,show_previous=True):
    current_dial = self.wm_dial()
    current_user = self.wm()
    self.put_par("set",1); # go in set mode
    sleep(0.1); # to make sure we are in set mode
    if (self.get_par("set") != 1):
      print "Failed to go in set mode, try again"
      return
    self.put_par("dial_drive",value)
    self.put_par("set",0); # go in use mode
    s = "Resetting dial `%s` (PV: %s) from (dial,user) = (%.4g,%.4g) to (%.4g,%.4g)" % (self.name,self.pvname,current_dial,current_user,value,current_user)
    logprint(s,print_screen=True)


  def set(self,value=0,show_previous=True):
    # EPICS does user = dial + offset
    # offset = value + self.__sign()*self.wm_dial()
    current_dial = self.wm_dial()
    current_user = self.wm()
    offset = value - self.__sign()*current_dial
    if (show_previous):
      s = "Resetting user `%s` (PV: %s) from (dial,user) = (%.4g,%.4g) to (%.4g,%.4g)" % (self.name,self.pvname,current_dial,current_user,current_dial,value)
      logprint(s,print_screen=True)
      self.put_par("offset",offset)
      
  def get_pvname(self,parname,sep="."):
    return self.pvname + sep + motor_params[parname][0]

  def get_par(self,parname,sep="."):
    pv = self.get_pvname(parname,sep)
    return pypsepics.get(pv)

  def get_par_silent(self,parname,sep="."):
    try:
      val = self.get_par(parname,sep)
    except pyexc, e:
      val = numpy.nan
    return val

  def get_pv(self,pvpar,sep="."):
    return pypsepics.get(self.pvname + sep + pvpar)

  def put_par(self,parname,value):
    pv = self.get_pvname(parname)
    return pypsepics.put(pv,value)
