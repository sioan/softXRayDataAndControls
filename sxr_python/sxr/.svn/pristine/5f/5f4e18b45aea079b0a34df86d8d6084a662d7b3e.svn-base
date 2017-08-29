from sxrbeamline import *
from utilitiesCalc import *
import numpy as n
from scipy import signal
from matplotlib.pyplot import *


class L637Macros:
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
		print("Expected beam size = 10 microns")
	elif n == 2:
		crl2.y(36.2793) # middle stack (40 microns beamsize)
		print("Inserting middle stack\n")
                print("Expected beam size = 40 microns")

	elif n == 3:
		crl2.y(55.3491)  # bottom stack (90 microns beamsize)
		print("Inserting bottom stack\n")
                print("Expected beam size = 90 microns")

	else:
		print("Wrong stack number!!!!!!!!!")
	crl2.x(1.5093)
	crl2.z(276.9922)

    def status(self):
	s = crl2.status()+ "\n"
	s += diff.status()+ "\n"
	s += g2.status()+ "\n"
	s += sample.status() + "\n"
	s += feeatt.status()+ "\n"
	s += sxratt.status()+ "\n"
	return s

    def fluence(self,J,FWHM,Angle=90):
        """Returns the incident x-ray fluence in mJ/cm^2
           J is the laser pulse energy in J
           FWHM is the incident x-ray sport size in m
           Angle in the laser/sample incidence angle (defauly is 90 - normal)
        """
        IF=J/FWHM**2
        F=IF*sind(Angle)*u['mJ']/u['cm']**2
        return F

    def BiMaxEplot(self,E=None,N=100):
        """Plots the pulse energy to reach the Bi melting point vs. spot size
           E is the photon energy in eV or keV (default is LCLS value)
           N is the number of data points (default is 100)
        """
        if E==None:
            E=pypsepics.get("SIOC:SYS0:ML00:AO627")
        E=eV(E)
        FWHM=n.linspace(10e-6,100e-6,N)
        dose=meltDose['Bi']
        BA=BraggAngle('Bi',(1,1,1),E)
        skinDepth=20e-9  #800 nm penetration depth
        J=n.zeros(N)
        F=n.zeros(N)
        ii=0
        for i in FWHM:
            J[ii]=DoseMaxEnergy('Bi',i,dose,E)
#            F[ii]=u['cm']**2/u['mJ']*i**2/sind(BA)*attenuationLength('Bi',E)/skinDepth
            ii+=1
        tstr="Pulse energy to reach %3.3f eV/atom in Bi" % (dose)
        FWHMum=FWHM*u['um']
        lstr="%4.1f eV" % E
        fig=figure()
#        plot(FWHMum,J*u['uJ'],'b.-',FWHMum,F*u['uJ'],'r.-',label=lstr)
        plot(FWHMum,J*u['uJ'],'b.-',label=lstr)
        ax=fig.add_subplot(111)
        ylabel('Pulse Energy (uJ)')
        xlabel('FWHM Spot Size (um)')
        title(tstr)
#        legend(('Melt point','1 mJ/cm2 equivalent'),loc=2)
        autoscale(tight=True)
        grid(True)
     
    def BiSim(self):
        """Simulates the x-ray pump/x-ray probe data on bismuth
           t is the time delay of the probe pulses in S - t=(0,20e-15,40e-15)
        """
        t=n.array([0,19.3,43.8,77.3,122.3,175.2,243.3,316.9,394.3,489,595.4,714.4,833.2,970.1,1119.5,1276.9])/u['fs']
        #create dummy function until we can grab real bismuth data
	tt=n.array([-0.330218,-0.305296,-0.280374,-0.255452,-0.23053,-0.205607,-0.180685,-0.155763,-0.130841,-0.105919,-0.0809969,-0.0560748,-0.0311526,-0.00623053,0.0186916,0.0436137,0.0685358,0.0934579,0.11838,0.143302,0.168224,0.193146 ,0.218069 ,0.242991 ,0.267913 ,0.292835 ,0.317757 ,0.342679 ,0.367601 ,0.392523 ,0.417445 ,0.442368 ,0.46729 ,0.492212 ,0.517134 ,0.542056 ,0.566978 ,0.5919 ,0.616822 ,0.641745 ,0.666667 ,0.691589 ,0.716511 ,0.741433 ,0.766355 ,0.791277 ,0.816199 ,0.841121 ,0.866044 ,0.890966 ,0.915888 ,0.965732 ,0.990654 ,1.01558 ,1.0405 ,1.06542 ,1.09034 ,1.11526 ,1.14019 ,1.16511 ,1.19003 ,1.21495 ,1.23988 ,1.2648 ,1.28972 ,1.31464 ,1.33956 ,1.36449 ,1.38941 ,1.41433 ,1.43925 ,1.46417 ,1.4891 ,1.51402 ,1.53894 ,1.56386 ,1.58879 ,1.61371 ,1.63863 ,1.66355 ,1.68847 ,1.7134 ,1.73832 ,1.76324 ,1.78816 ,1.81308 ,1.83801 ,1.86293 ,1.88785 ,1.91277 ,1.93769 ,1.96262 ,1.98754])/u['ps']
        yy=n.array([0.363887,0.362213,0.368271,0.365699,0.363504,0.364192,0.357994,0.365464,0.362127,0.360477,0.361498,0.361881,0.361597,0.362697,0.35972,0.356912,0.355711,0.35503,0.349882,0.342697,0.333422,0.330846,0.323082,0.319786,0.316527,0.303467,0.303305,0.300128,0.300139,0.302561,0.302725,0.306546,0.318684,0.315627,0.319177,0.320543,0.317974,0.3165,0.314424,0.307271,0.308091,0.305324,0.300032,0.302897,0.301629,0.313487,0.309671,0.314254,0.309217,0.316701,0.322415,0.322324,0.317647,0.321105,0.313967,0.310901,0.307442,0.309598,0.31416,0.306223,0.309237,0.311738,0.308734,0.315338,0.315389,0.314715,0.314772,0.314434,0.313873,0.305349,0.310495,0.31437,0.310681,0.312453,0.311064,0.313162,0.307312,0.309903,0.315762,0.315853,0.319646,0.316934,0.323306,0.315671,0.315524,0.312877,0.307967,0.312367,0.31145,0.310954,0.315918,0.315136,0.323878])
        io=n.mean(yy[0:14])
        yy=yy/io
        #tt=n.linspace(-0.2e-12,1.5e-12,300)
        #yy=n.sin(2*n.pi*tt/360e-15)
        ##########################################################
        # now interpolate time points onto real data   ###
        data=n.interp(t,tt,yy)
        fig=figure(12,figsize=(12,5))
        clf()

        subplot(121)
        plot(tt*u['ps'],yy,'b-',t*u['ps'],data,'ro')
        ax=fig.add_subplot(121)
        ylabel('Signal (a.u.)')
        xlabel('Time (ps)')
        title('Bismuth Simulation')
        #legend(('Melt point','1 mJ/cm2 equivalent'),loc=2)
        autoscale(tight=True)
        grid(True)
        
        subplot(122)
        plot(t*u['ps'],data,'ro')
        ax=fig.add_subplot(122)
        ylabel('Signal (a.u.)')
        xlabel('Time (ps)')
        title('Bismuth Simulation')
        #legend(('Melt point','1 mJ/cm2 equivalent'),loc=2)
        autoscale(tight=True)
        grid(True)
 

    pass

