#! /usr/bin/env ipython 
import sys
import os
os.environ['PYPS_INTERACTIVE']='TRUE'

# Create a banner in a similar manner to XPP 
from pyfiglet import Figlet
pf = Figlet(font='speed')
print pf.renderText('SXRpython')

from common.utilities import printnow
printnow("Defining logfile..."),
from common.pypslog import logprint as sxrpythonlogprint
printnow(" done\n")


DAQ_PLATFORM=1
PYPS_INTERACTIVE = os.getenv('PYPS_INTERACTIVE',"FALSE").lower()=='true'

# Set up python elog
printnow("Loading grabber..."),
sxrElog = None
from common import pypsElog
if PYPS_INTERACTIVE:
  sxrElog = pypsElog.pypsElog()
else:
  print "WARNING: non-interactive mode.  NOT Loading grabber."
from common import config
config.Elog = sxrElog
printnow(" done\n")


printnow("Loading daq interface..."),
if PYPS_INTERACTIVE:
  from common import daq
  sxrdaq = daq.Daq(host="sxr-control",platform=DAQ_PLATFORM)
  from common import daq_config
  sxrdaqconfig = daq_config.DaqConfig() #current
#  #sxrdaqconfig = daq_config.DaqConfig(dbpath="/reg/g/pcds/dist/pds/sxr/configd#b/oct17")
else:
  print "WARNING: Not Loading DAQ because not in interactive mode"
  pass
printnow(" done\n")



#from sxrbeamline import *



"""
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

"""
