from sxrbeamline import *
from common.device import Device
import sxrmotors
import math
import time
from common import virtualmotor
from common.smartactpiezo import SaPiezo
from common import pypsepics

pvBase = None
sxrmotors = sxrmotors.SXRMotors()
class USER(Device):
    def __init__(self,
                 elog=None,
                 cspad_x = sxrmotors.user_mmn_10,
		 pi_x = sxrmotors.user_mmn_09,
		 yag_zoom = sxrmotors.user_dumb_32,
                 sam_x = sxrmotors.user_mmn_08,
                 att = sxrmotors.user_mmn_01,
                 yag_focus = sxrmotors.user_dumb_31,
		 yag_x = sxrmotors.user_mmn_02,
		 yag_y = sxrmotors.user_mmn_03,
                 objName = "IH_sikorski_1_2013",
                 presetsfile = "/reg/neh/operator/sxropr/sxr_python/modules/experiments/presets/IH_sikorski_10_2013_presets.py"):
        Device.__init__(self,objName,pvBase,presetsfile)
        self.elog = elog
        self.sam_x = sam_x
        self.att = att
	self.pi_x = pi_x
        self.cspad_x = cspad_x
	self.yag_zoom = yag_zoom
	self.yag_focus = yag_focus
	self.yag_x = yag_x
	self.yag_y = yag_y

        self.motors = {
            "sam_x": self.sam_x,
            "att": self.att,
            "yag_x": yag_x,
            "yag_y": yag_y,
            "cspad_x": self.cspad_x,
	    "pi_x": self.pi_x,
	    "yag_zoom": self.yag_zoom,
            "yag_focus": self.yag_focus
    
	}
        pass
    def HRM(self):
	s = '\n' + "Harmonic rejection mirrors:" + '\n'
	s += hrm.m1y.status() + 'n'
	s += hrm.m2y.status() + 'n'
	s += hrm.m1r.status() + 'n'
	s += hrm.m2r.status() + 'n'
	return s
    def status_Elog(self):
        s =  "Status of the IH_Sikorski from "
	s += self.status() + '\n'
	s += diff.status() + "\n"
	s += crl2.status() + "\n"
	s += self.HRM() + "\n"
	s += ipm2.status() + "\n"
	s += ipmmono.status() + "\n"
	s += ipm4.status() + "\n"
	s += ipm5.status() + "\n"
	s += ladm.status() + "\n"
	s += sxrdet.status() + '\n'
	s += slits(None,None,fast=0, elog =1) + "\n" 
	s += "Fee att:" + "\n"
	s += feeatt.status() + "\n"
	s += "SXR att:" + "\n"
	s += sxratt.status() + "\n"
        return s

    def cspads_in(self):
	sxrdet.y.umv(12)
    def cspads_out(self):
	sxrdet.y.umv(272.0)
	
	
    def Elog(self,comment=""):
        if (comment != ""): comment += "\n"
        sxrElog.submit(comment+self.status_Elog())

