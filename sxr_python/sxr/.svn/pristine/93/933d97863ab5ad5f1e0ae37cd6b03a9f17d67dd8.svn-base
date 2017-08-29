""" Utilities to handle strings, guess which beamline are you running from,
    time/date, etc"""

import sys
import time
import datetime
import re
import socket
import numpy as np

def parse_cnf_file(beamline="xpp",field="configdb_path"):
  beamline=beamline.strip()
  fname = "/reg/g/pcds/dist/pds/%s/scripts/%s.cnf" % (beamline,beamline)
  f=open(fname,"r")
  lines = f.readlines()
  match = None
  for l in lines:
    ls = l.strip()
    ls = ls.replace(" ","")
    ls = ls.replace("\t","")
    # == 0 means that is not commented out
    if (ls.find(field) == 0):
      match = ls.replace('"',"")
      match = ls.replace("'","")
  if (match is not None):
    return match.split("=")[1]
  else:
    return None
  

def guessBeamline():
  """ Guess beamline from hostname xpp-daq -> xpp"""
  host = socket.gethostname(); # returns for example xpp-daq
  return host.split("-")[0];   # returns xpp

#def guessExpname():
#  """ TO BE REWRITTEN USING NEW APPROACH .... """
#  conffile = "/reg/g/pcds/dist/pds/xpp/scripts/xpp.cnf"
#  r=re.compile("(^\s*expname\s*=\s*')(\w+)(')")
#  f = open(conffile,"r");
#  lines = f.readlines()
#  expname = None
#  for l in lines:
#    a = r.search(l)
#    if (a is not None):
#      expname = a.group(2)
#      break
#  return expname

def cartesian_to_spherical(x,y,z):
    az = np.rad2deg( np.arctan2(x,z) )
    el = np.rad2deg( np.arctan2(y,np.sqrt(z**2+x**2)) )
    ra = np.sqrt ( x**2 + y**2 + z**2 )
    return (ra,az,el)

def now():
  """ returns string with current date and time (with millisecond resolution)"""
  now = datetime.datetime.now()
  return "%04d-%02d-%02d %02d:%02d:%02d.%03d" % ( now.year, now.month,now.day,
                     now.hour,now.minute,now.second,int(now.microsecond/1e3))

def today():
  """ returns string with current date"""
  now = datetime.datetime.now()
  return "%04d-%02d-%02d" % ( now.year, now.month,now.day)

def estr(string,color="red",type="bold"):
  """ returns an enhanced string, current colors defined: red|green,
                                  current type defined: bold"""
  str = ""
  if ( color == "red" ):
    str += "\x1b[31m"
  if ( color == "green" ):
    str += "\x1b[32m"
  if (type == "bold"):
    str += "\x1b[1m"
  str += string
  str += "\x1b[0m"; # reset color
  return str

def dec2bin(n):
    """converts denary integer n to binary string (used for lusiatt)"""
    bStr = ''
    if n < 0:  raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return bStr

def time_to_text(t):
  """converts floating number as string like 3s 004ms 024us 134ns 003ps 104fs"""
  t="%0.15f" % t
  idx = t.index(".")
  s  = int( t[0      : idx    ])
  ms = int( t[idx+1  : idx+4  ])
  us = int( t[idx+4  : idx+7  ])
  ns = int( t[idx+7  : idx+10 ])
  ps = int( t[idx+10 : idx+13 ])
  fs = int( t[idx+13 : idx+16 ])
  text = "%ss %03dms %03dus %03dns %03dps %03dfs" % (s,ms,us,ns,ps,fs)
  return text

def printnow(s):
  print s,
  sys.stdout.flush()

def terminal_size():
  """returns a tuple with (nrows,ncols) of current terminal"""
  import termios, fcntl, struct, sys
  s = struct.pack("HHHH", 0, 0, 0, 0)
  fd_stdout = sys.stdout.fileno()
  x = fcntl.ioctl(fd_stdout, termios.TIOCGWINSZ, s)
  (rows,cols,xpixel,ypixel)=  struct.unpack("HHHH", x)
  return (rows,cols)

def notice(string):
  """prints a string starting from the beginning of the line and spanning the
  entire terminal columns, useful for updating values ...
  notice("this is the first value 1.2"); sleep(1); notice("this is the second one 1.4 that will mask the first...")
  """
  (nrows,ncols)=terminal_size()
  format = "\r%%-%ds" % ncols
  sys.stdout.write( format % string)
  sys.stdout.flush()

def write_array_to_file(a,fname):
  f=file(fname,"w")
  for l in a:
    f.write("%s\n" % l)
  f.close()

def array_string_to_float(a):
  c=[]
  for e in a:
    c.append(float(e))
  return c

def eventcode_to_time(eventcode):
  eventcode=int(eventcode)
  e = {}
  e[9]  = 12900 
  e[10] = 12951 
  e[11] = 12961 
  e[12] = 12971 
  e[13] = 12981 
  e[14] = 12991 
  e[15] = 13001 
  e[16] = 13011 
  e[40] = 12954 
  e[41] = 12964 
  e[42] = 12974 
  e[43] = 12984 
  e[44] = 12994 
  e[45] = 13004 
  e[46] = 13014 
  e[140]= 11850 
  e[162]= 11840
  if (eventcode in e):
    ticks = e[eventcode]
  elif (eventcode >= 67 and eventcode<= 98):
    ticks = e[140]+eventcode
  elif (eventcode>140 and eventcode<=159):
    ticks = e[140]+(eventcode-140)
  else:
    ticks = 0
  return ticks/119e6


def eventcode_time_from140(eventcode):
  return eventcode_to_time(eventcode)-eventcode_to_time(140)
