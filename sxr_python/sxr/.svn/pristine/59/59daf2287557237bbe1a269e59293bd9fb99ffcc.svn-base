from sxrbeamline import *
from utilitiesCalc import *
import numpy as n
from scipy import signal
from matplotlib.pyplot import *


class L729Macros:
    def __init__(self):
        pass

    def __repr__(self):
        return self.status()

    def Elog(self,comment=""):
    	if (comment != ""): comment += "\n"
    	sxrElog.submit(comment+self.status())
    def lens_in(self, n = 1):
	if n == 1:
		crl2.y(17.2266) # top stack (10 microns beamsize)
		print("Inserting top stack\n")
		print("Expected beam size = ?? microns")
	elif n == 2:
		crl2.y(36.2793) # middle stack (40 microns beamsize)
		print("Inserting middle stack\n")
                print("Expected beam size = ?? microns")

#	elif n == 3:
#		crl2.y(55.3491)  # bottom stack (90 microns beamsize)
	
#	print("Inserting bottom stack\n")
 #               print("Expected beam size = 90 microns")

	else:
		print("Wrong stack number!!!!!!!!!")
	crl2.x(1.5093)
	crl2.z(276.9922)

    def status(self):
	s = crl2.status()+ "\n"
	s += diff.status()+ "\n"
	s += madsen.status() + "\n"
	s += feeatt.status()+ "\n"
	s += sxratt.status() + "\n"
	s += ladm.status() + "\n"
	#s += slits() + "\n"
	return s


