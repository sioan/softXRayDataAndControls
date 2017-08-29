from sxrbeamline import *
from common.utilitiesCalc import *
import numpy as n
from scipy import signal
from matplotlib.pyplot import *

class macros:
    def __init__(self):
        pass

    def __repr__(self):
        return self.status()

    def Elog(self,comment=""):
    	if (comment != ""): comment += "\n"
    	sxrElog.submit(comment+self.status())
    def lens_in(self, n):
	if (n >3) or (n<1):
		print("Wrong stack number!!!!!!!!!")
                return -1
	lens_y = [18.5889,36.0,55.34]
	lens_z = [200.0,196.0,196.0]
	lens_x = 0.6129
	lens_y = lens_y[n-1]
	lens_z = lens_z[n-1]
	pypsepics.put("HFX:DG2:STP:01:CMD",0)# close shutter on DG2
	while not pypsepics.get("HFX:DG2:STP:01:CLOSE"):
		pass
	crl2.y(lens_y) 
	crl2.z(lens_z)
	crl2.x(lens_x)
	print("Inserting stack #" + str(n) +"\n")
	while crl2.y.ismoving() or crl2.z.ismoving() or crl2.x.ismoving():
		pass
	pypsepics.put("HFX:DG2:STP:01:CMD",1)# open shutter on DG2
    def lens_out(self):
	pypsepics.put("HFX:DG2:STP:01:CMD",0)# close shutter on DG2
        while not pypsepics.get("HFX:DG2:STP:01:CLOSE"):
                pass
        crl2.y(100) # out position
        print("Removing lenses." +"\n")
        while crl2.y.ismoving():
                pass    
        pypsepics.put("HFX:DG2:STP:01:CMD",1)# open shutter on DG2
	
    def status(self):
	ipm = [ipm2, ipmmono, ipm4, ipm5]
	s = "Beamline configuration for " + user.objName +"\n"
	for i in ipm:
		s += i.status()
	s += crl2.status()+ "\n"
	s += diff.status()+ "\n"
	s += user.status() + "\n"
	s += "FEE ATT \n"
	s += feeatt.status()+ "\n"
	s += "SXR ATT \n"
	s += sxratt.status() + "\n"
	s += str(slits(None,None,0,1)) + "\n"
	return s

 


