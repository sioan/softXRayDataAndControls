from device import Device
import sxrmotors

pvBase = None
sxrmotors = sxrmotors.SXRMotors()
class USER(Device):
    def __init__(self,
                 specphi = sxrmotors.user_mmn_01,
                 specx = sxrmotors.user_mmn_02,
                 speczoom = sxrmotors.user_dumb_32,
                 specfocus = sxrmotors.user_dumb_31,
                 objName = "IH_Yiping_2013_07",
                 presetsfile = "/reg/neh/operator/sxropr/sxrpython_data/IH_Yiping_2013_07_presets.py"):
        Device.__init__(self,objName,pvBase,presetsfile)
        self.specphi=specphi
	self.specx = specx
        self.speczoom=speczoom
        self.specfocus=specfocus

        self.motors = {
            "specphi": specphi,
	    "specx" : specx,	
            "speczoom": speczoom,
            "specfocus": specfocus
            }
        pass

    pass

