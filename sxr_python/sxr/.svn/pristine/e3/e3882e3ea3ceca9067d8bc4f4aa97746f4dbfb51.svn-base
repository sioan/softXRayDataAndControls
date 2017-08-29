#! /usr/bin/env ipython 
import sys
import os
os.environ['PYPS_INTERACTIVE']='TRUE'
from sxrbeamline import *
from experiments.current_macros import macros as exp_macros
import sxrMacros as macros
from sxr_tools import knife_edge_scan
import sxrPrinceton
from sxrPrinceton import ccdtake
import common.burstScan as burst
from common.utilitiesCalc import *
from common.utilitiesLaser import *
from common.utilitiesDispersion import *

# make prompt reactive
sys.stdout.flush()


scanlogdir="/reg/neh/operator/sxropr/scanlog/"
scanlogfile_f=scanlogdir+"CURRENT_LOG_FILE"

m = sxrmotors
daq = sxrdaq

x = exp_macros()

def knife_edge(y_det=0,algorithm=[1,1],fig_no=2):
  knife_edge_scan(daq.scan_pos(0),daq.scan_data(y_det),algorithm,fig_no)
  pass

