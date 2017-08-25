# these two lines for example purposes only, to allow user to write
# calibration information to local directory called "calib"
# should be deleted for real analysis.
import psana
psana.setOption('psana.calib-dir','calib')

from xtcav.GenerateDarkBackground import *
GDB=GenerateDarkBackground();
GDB.experiment='xpptut15'
GDB.runs='300'
GDB.maxshots=1000
GDB.SetValidityRange(300,302) # delete second run number argument to have the validity range be open-ended ("end")
GDB.Generate();
