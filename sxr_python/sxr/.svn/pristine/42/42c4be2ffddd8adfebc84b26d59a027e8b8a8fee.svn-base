import pyca
from caget import caget

sxr_beamline = ["SPS","TSS","MON","EXS","FLX","KBO","DFP","LIN","MNT","EXP"]
#amo_beamline = ["SAS","KBO","LMP","PPL"]

for dev in sxr_beamline :
    for mnt in range(1,50) :
        basepv = "SXR:%s:MMS:%02d"%(dev,mnt)
        sn_pv = basepv + ".SN"
        pn_pv = basepv + ".PN"
        
        try:
            sn = caget(sn_pv)
            pn = caget(pn_pv)
            print basepv,"MODEL:",pn," SERIAL NUMBER:",sn
        except pyca.pyexc, e:
            print basepv," --> DOES NOT EXIST"
        except pyca.caexc, e:
            print basepv," --> CHANNEL ACCESS ERROR"

        

