#!/usr/bin/python
# This module provides operation of valves
# 
# Author:         Daniel Flath (SLAC)
# Created:        July 7, 2011

import numpy as n
import sys
from utilities import estr
import pypsepics
from pypslog import logprint

class DiagnosticStopper:
  def __init__(self, basePV):
    self.__basePV = basePV
    self.__positionPV = self.basePV + ":POSITION"
    self.__statePV    = self.basePV + ":_STATE"
    self.__openStatusPV = self.basePV + ":CLOSE"
    self.__closeStatusPV = self.basePV + ":OPEN"
    self.__cmdPV = self.basePV + ":CMD"
    self.__positionMap = {"out": 1, "in": 0}
    self.__stateMap = {0: "Moving", 1: "Open", 2: "Closed", 3: "Stuck"}

  def __getPV(suffix):
    return self.__basePV + suffix

  def __getPosition():
    return pypsepics.get(self.__positionPV)

  def __getState():
    return pypsepics.get(self.__statePV)

  def state(self):
    print "%s\n" % (self.__getPosition())

  def open(self):
    self.move("out")
    
  def close(self):
    self.move("in")

  def move(self, position):
    if position in self.__positionMap:
      curpos = self.__getPosition()
      if curpos == positoin:
        print "WARNING: Stopper is already %s\n" % (position)
      else:
        pypsepics.put(self.__getPV(self.__cmdPV), position)
    else:
      print "ERROR: '%s' is not a valid position, please use one of: %s\n" % (position,__positionMap.keys())
