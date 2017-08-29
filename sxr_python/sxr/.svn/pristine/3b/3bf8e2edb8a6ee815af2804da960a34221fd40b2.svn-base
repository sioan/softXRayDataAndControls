""" Module that handles logging:
    usage is very simple:
    from pypslog import logprint
    logprint("this is what I want to log")
    logprint takes three optional (bolean) parameters
    date=True/False (add date and time in fonrt of the string)
    print_screen=True/False print also to the screen
    newline=True/False print also to the screen

    DATA:
    gFilename:  current filename
    gLogfolder: current path to logfile
    gLogf:      file object (open in append mode); it is defined by guessFilename
"""
import sys
import config
import utilities
import socket; # to get hostname
import os
import time

import os
PYPS_INTERACTIVE = os.getenv('PYPS_INTERACTIVE',"FALSE").lower()=='true'

gFilename  = None
gLogf      = None
gLogfolder = None

def checkFolder():
  """ returns (and set global variable) for folder to use for logfile
  most of the time it will be ~operator/pyps/log/"""
  beamline = utilities.guessBeamline()
  user     = "%sopr" % beamline
  base_folder   = os.path.expanduser("~%s" % user)
  # test writing permission
  can_write = os.access(base_folder,os.W_OK)
  if (can_write):
    folder = base_folder + "/pyps/log/"
  else:
    folder = os.path.expanduser("~") + "/pyps/log/"
  if ( not os.path.exists(folder) ): os.makedirs(folder)
  globals()["gLogfolder"] = folder
  return folder

def guessFilename():
  """ returns (and set global variable) for filename to use
  if automatically sets it to for example 2011-04-19_pyps.log"""
  if (gLogfolder is None): checkFolder()
  date = utilities.today()
  fname = date + "_pyps.log"
  globals()["gFilename"] = fname
  fname_complete = gLogfolder+"/"+fname
  globals()["gLogf"] = open(fname_complete,"a")
  print "setting logfile to %s" % fname_complete
  return fname_complete

def logprint(text,date=True,print_screen=None,newline=True):
  """ appends `text` to the logfile.
  Optional (booleans):
  date: put time stamp (with millisecond resolution in front of the string)
  print_screen: write also to screen
  newline: terminate with newline the string"""
  if not PYPS_INTERACTIVE:
    print "WARNING: pypselog.logpring, not in interactive mode, not logging"
    return

  if ( (gLogf is None) or (gFilename.startswith(utilities.today()) != True) ): guessFilename()
  if (config.PRINT_DATE & date):
    text = "%s %s" % (utilities.now(),text)
  if (newline): text += "\n"
  if (print_screen is None): print_screen = config.LOGFILE_print_screen
  if (print_screen):
    sys.stdout.write(text)
    sys.stdout.flush()
  gLogf.write(text)
  gLogf.flush()
