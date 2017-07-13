# these two lines for example purposes only, to allow user to write
# calibration information to local directory called "calib"
# should be deleted for real analysis.
import psana
psana.setOption('psana.calib-dir','calib')

from xtcav.GenerateLasingOffReference import *
GLOC=GenerateLasingOffReference();
GLOC.experiment='xpptut15'
GLOC.runs='301'
GLOC.maxshots=1400
GLOC.nb=1
GLOC.islandsplitmethod = 'scipyLabel'       # see confluence documentation for how to set this parameter
GLOC.groupsize=40             # see confluence documentation for how to set this parameter
GLOC.SetValidityRange(300,302) # delete second run number argument to have the validity range be open-ended ("end")
GLOC.Generate();
