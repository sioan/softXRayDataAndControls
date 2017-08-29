""" Utilities to perfrom various calculations """

import pypsepics
import numpy as n
import scipy as s
import xraylib
import periodictable.formulas
from matplotlib.pyplot import *
from scipy import integrate


def lam(E,o=0):
    """ Computes photon wavelength in m
        E is photon energy in eV or keV
        set o to 0 if working at sub-100 eV energies
    """
    if o:
      E=E
    else:
      E=eV(E)
    lam=(12398.4/E)*1e-10
    return lam

def lam2E(l):
    """ Computes photon energy in eV
        l is photon wavelength in m
    """
    E=12398.4/(l*u['ang'])
    return E

def lam2f(l):
    """ Computes the photon frequency in Hz
        l is photon wavelength in m
    """
    f=c['c']/l
    return f
    
def f2lam(f):
    """ Computes the photon wavelength in m
        f is the photon frequency in Hz
    """
    l=c['c']/f
    return l
 
def f2E(f):
    """ Computes the photon in energy in eV
        f is the photon frequency in Hz
    """
    E=c['h']*f*u['eV']
    return E
 
def E2f(E):
    """ Computes the photon frequency in Hz
        E is photon energy in eV or keV
    """
    f=E/c['h']/u['eV']
    return f

def eV(E):
    """ Returns photon energy in eV if specified in eV or keV """
    if E < 100:
      E=E*1000.0;
    return E*1.0

def TimeBandwidth(dl,l=800e-9):
    """Returns the transform limit of a Gaussian pulse
       dl is the bandwidth in m
       l is the center wavelength in m (default is 800 nm)
    """
    BW=dl*c['c']/l**2
    PD=0.44/BW
    return PD


def nPhotons(J,E=None):
    """ Prints the number of photons 
        J is the pulse energy in Joules
        E is photon energy in eV or keV (default is LCLS value)
    """
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")
    E=eV(E)
    N=J/(E/u['eV']) 
    print '%1.2e' %N

def sind(A):
    """ Sin of an angle specified in degrees """
    Arad = n.deg2rad(A)
    x = n.sin(Arad) 
    return x
 
def cosd(A):
    """ Cos of an angle specified in degrees """
    Arad = n.deg2rad(A)
    x = n.cos(Arad) 
    return x

def tand(A):
    """ Tan of an angle specified in degrees """
    Arad = n.deg2rad(A)
    x = n.tan(Arad) 
    return x
 
def asind(x):
    """ Arcsin in degrees """
    A = n.arcsin(x)
    A = n.rad2deg(A) 
    return A
 
def acosd(x):
    """ Arccos in degrees """
    A = n.arccos(x)
    A = n.rad2deg(A) 
    return A

def atand(x):
    """ Arctan in degrees """
    A = n.arctan(x)
    A = n.rad2deg(A) 
    return A
 
def Q(twotheta,E=None):
    """ Computes Q in Ang^-1
        twotheta is the scattering angle in degrees
        E is photon energy in eV or keV (default is LCLS value)
    """
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")
    E=eV(E)
    l = lam(E)
    q=4*n.pi*sind(twotheta/2)/l/u['ang']
    return q

def Q2TwoTheta(q,E=None):
    """ Computes the scattering angle in degrees for a specified Q
        Q is the reciprocal space value in ang^-1
        E is photon energy in eV or keV (default is LCLS value)
    """
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")
    E=eV(E)
    l = lam(E)
    twotheta  = asind(q*u['ang']*l/4/n.pi)*2
    return twotheta

def checkID(ID):
    """ Checks to see if you are using an alias. Returns the chemical formula"""
    try:
      return alias[ID]
    except:
      return ID

def Transmission(ID,t,E=None,density=None):
    """ Computes the transmission of a solid (photoabsoption and Compton cross sections) 
        ID is chemical fomula : 'Si'
        t is the material thickness in m
        E is photon energy in eV or keV (default is LCLS value)
        density is the material density in g/cm^3
        If no density is specified will use default value
    """
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000.
    E=eV(E)/1000.
    ID=checkID(ID)
    attlength=attenuationLength(ID,E,density)
    trans=n.exp(-t/attlength)
    return trans

def Transmission_noCompton(ID,t,E=None,density=None):
    """ Computes the transmission of a solid (photoabsoption cross section) 
        ID is chemical fomula : 'Si'
        t is the material thickness in m
        E is photon energy in eV or keV (default is LCLS value)
        density is the material density in g/cm^3
        If no density is specified will use default value
    """
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000.
    E=eV(E)/1000.
    ID=checkID(ID)
    attlength=attenuationLength_noCompton(ID,E,density)
    trans=n.exp(-t/attlength)
    return trans

def TransmissionPlotFixedE(ID,t1,t2,E=None,density=None,N=100):
    """ Plots the transmission of a solid (photoabsoption and Compton cross sections) as a function of thickness
        ID is chemical fomula : 'Si'
        t1,t2 is the material thickness range in m
        E is photon energy in eV or keV (default is LCLS value)
        density is the material density in g/cm^3
        If no density is specified will use default value
        N is the number of data points (default is 100)
    """
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    E=eV(E)/1000.
    ID=checkID(ID)
    attlength=attenuationLength(ID,E,density)
    t=n.linspace(t1,t2,N)
    trans=n.exp(-t/attlength)
    tstr="%s at %.4f keV" % (ID,E) 
    fig=figure()
    plot(t*u['mm'],trans,'b.-')
    ax=fig.add_subplot(111)
    ylabel('Transmission')
    xlabel('Thickness (mm)')
    suptitle('Transmission Plot')
    title(tstr)
    autoscale(tight=True)
    att_len=attlength*u['um']
    text(0.65,0.92,'Att. Length = %3.3f um' %att_len,transform=ax.transAxes,bbox={'facecolor':'white','pad':15})
    grid(True)

def TransmissionPlotFixedT(ID,t,E1,E2,density=None,N=100):
    """ Plots the transmission of a solid (photoabsoption and Compton cross sections) as a function of photon energy
        ID is chemical fomula : 'Si'
        t is the material thickness in m
        E1,E2 is photon energy in eV or keV 
        density is the material density in g/cm^3
        If no density is specified will use default value
        N is the number of data points (default is 100)
    """
    E1=eV(E1)/1000.
    E2=eV(E2)/1000.
    ID=checkID(ID)
    E=n.linspace(E1,E2,N)
    trans=n.zeros(N)
    ii=0
    for i in E:
      trans[ii]=Transmission(ID,t,i,density)
      ii+=1
    t_mm=t*u['mm']
    tstr="%3.3f mm of %s" % (t_mm,ID) 
    fig=figure()
    plot(E,trans,'b.-')
    ax=fig.add_subplot(111)
    ylabel('Transmission')
    xlabel('Photon Energy (keV)')
    suptitle('Transmission Plot')
    title(tstr)
    autoscale(tight=True)
    grid(True)

def gasTransmissionPlotFixedT(ID,t,E1,E2,P=760,T=295,N=100):
    """ Plots the gas transmission (photoabsoption and Compton cross sections) as a function of photon energy
        ID is chemical fomula : 'N2'
        t is the  in distance in m
        E1,E2 is photon energy in eV or keV 
        P is the gas pressure in Torr (default is atmospheric pressure)
        T is the gas temperature in K (default is room temp)
        N is the number of data points (default is 100)
        NOTE: Assumes ideal gas
   """
    MoleculesPerV=P/u['Torr']/c['k']/T
    density=MoleculesPerV/u['cm']**3*MolecularMass(ID)/c['NA']
    E1=eV(E1)/1000.
    E2=eV(E2)/1000.
    ID=checkID(ID)
    E=n.linspace(E1,E2,N)
    trans=n.zeros(N)
    ii=0
    for i in E:
      trans[ii]=gasTransmission(ID,t,i,P,T)
      ii+=1
    tstr="%3.3f m of %s" % (t,ID) 
    fig=figure()
    plot(E,trans,'b.-')
    ax=fig.add_subplot(111)
    ylabel('Transmission')
    xlabel('Photon Energy (keV)')
    suptitle('Transmission Plot')
    title(tstr)
    autoscale(tight=True)
    grid(True)


def gasTransmissionPlotFixedE(ID,t1,t2,E=None,P=760,T=295,N=100):
    """ Plots the gas transmission (photoabsoption and Compton cross sections) as a function of distance
        ID is chemical fomula : 'N2'
        t is the  in distance in m
        E is photon energy in eV or keV (default is LCLS value)
        P is the gas pressure in Torr (default is atmospheric pressure)
        T is the gas temperature in K (default is room temp)
        N is the number of data points (default is 100)
        NOTE: Assumes ideal gas
   """
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    E=eV(E)/1000.
    ID=checkID(ID)
    MoleculesPerV=P/u['Torr']/c['k']/T
    density=MoleculesPerV/u['cm']**3*MolecularMass(ID)/c['NA']
    attlength=attenuationLength(ID,E,density)
    t=n.linspace(t1,t2,N)
    trans=n.exp(-t/attlength)
    tstr="%s at %.4f keV, %3.1f Torr, %3.0f Kelvin" % (ID,E,P,T) 
    fig=figure()
    plot(t*u['mm'],trans,'b.-')
    ax=fig.add_subplot(111)
    ylabel('Transmission')
    xlabel('Path Length (mm)')
    suptitle('Transmission Plot')
    title(tstr)
    autoscale(tight=True)
    text(0.65,0.92,'Att. Length = %3.3f m' %attlength,transform=ax.transAxes,bbox={'facecolor':'white','pad':15})
    grid(True)

   
def gasTransmission(ID,t,E=None,P=760,T=295):
    """ Computes the gas transmission (photoabsorption and Compton CS)
        ID is chemical fomula : 'Si'
        t is the  in distance in m
        E is photon energy in eV or keV (default is LCLS value)
        P is the gas pressure in Torr (default is atmospheric pressure)
        T is the gas temperature in K (default is room temp)
        NOTE: Assumes ideal gas
    """
    ID=checkID(ID)
    MoleculesPerV=P/u['Torr']/c['k']/T
    density=MoleculesPerV/u['cm']**3*MolecularMass(ID)/c['NA']
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    E=eV(E)/1000.
    attlength=attenuationLength(ID,E,density)
    trans=n.exp(-t/attlength)
    return trans

    
def attenuationLength(ID,E=None,density=None):
    """ Computes the attenuation length of a solid in m (photoabsoption and Compton cross sections) 
        ID is chemical fomula : 'Si'
        E is photon energy in eV or keV (default is LCLS value)
        density is the material density in g/cm^3
        If no density is specified will use default value
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    E=eV(E)/1000.
    if density==None:
      density=Density[ID]
    mu_Rho=c['NA']*(CS_Photo(ID,E)+CS_Compt(ID,E))/MolecularMass(ID)*density*u['cm']**3
    attL=1.0/mu_Rho
    return attL

def attenuationLength_noCompton(ID,E=None,density=None):
    """ Computes the attenuation length of a solid in m (photoabsoption cross section) 
        ID is chemical fomula : 'Si'
        E is photon energy in eV or keV (default is LCLS value)
        density is the material density in g/cm^3
        If no density is specified will use default value
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000.
    E=eV(E)/1000
    if density==None:
      density=Density[ID]
    mu_Rho=c['NA']*CS_Photo(ID,E)/MolecularMass(ID)*density*u['cm']**3
    attL=1/mu_Rho
    return attL



def MolecularMass(ID):
    """Returns the molecular mass of a chemical formula in g"""
    ID=checkID(ID)
    form=periodictable.formulas.parse_formula(ID)
    mass=0
    for i in range(len(form)):
      id=str(form[i][1])
      atoms=form[i][0]
      mass+=AtomicMass[id]*atoms
    return mass

def nAtoms(ID):
    """Returns the number of atoms in a chemical formula"""
    ID=checkID(ID)
    form=periodictable.formulas.parse_formula(ID)
    atoms=0
    for i in range(len(form)):
      a=form[i][0]
      atoms+=a
    return atoms

def Dose(ID,FWHM,J=None,E=None,CS_ph=None):
    """ Computes the absorbed dose in a solid in eV/atom (photoabsoption cross sections) 
        ID is chemical fomula : 'Si'
        FWHM is the FEL spot size
        J is the LCLS pulse energy in Joules (default is LCLS value)
        E is photon energy in eV or keV (default is LCLS value)
        If no density is specified will use default value
        CS_ph is photoelectron cross section in m^2. Default is xraylib value.
        !!!!!  WARNING -- Can underestimate dose by 10x on a resonance !!!!!
        !!!!!  Check to make sure photoelectron cross section is correct !!!!
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    E=eV(E)/1000
#    if J==None:
#      J=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    wo=FWHM/1.18
    if CS_ph==None:
      CS_ph=CS_Photo(ID,E)
    dose=2*J*CS_ph*u['eV']/n.pi/wo**2/nAtoms(ID)
    return dose 


def DoseMaxEnergy(ID,FWHM,dose,E=None,CS_ph=None):
    """ Computes the photon pulse energy to reach the specified dose (in Joules)
        ID is chemical fomula : 'Si'
        FWHM is the FEL spot size
        dose is in eV/atom
        E is photon energy in eV or keV (default is LCLS value)
        CS_ph is photoelectron cross section in m^2. Default is xraylib value.
        !!!!!  WARNING -- Can overestimate Energy by 10x on a resonance !!!!!
        !!!!!  Check to make sure photoelectron cross section is correct !!!!
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    E=eV(E)/1000
    wo=FWHM/1.18
    if CS_ph==None:
      CS_ph=CS_Photo(ID,E)
    J=dose/(2*CS_ph*u['eV']/n.pi/wo**2/nAtoms(ID))
    return J    

def DoseMaxEnergyPlot(ID,FWHM,dose,E1,E2,N=100,CS=None):
    """ Computes the photon pulse energy to reach the specified dose (in Joules)
        ID is chemical fomula : 'Si'
        FWHM is the FEL spot size
        dose is in eV/atom
        E is photon energy in eV or keV (default is LCLS value)
        !!!!!  WARNING -- Can overestimate Energy by 10x on a resonance !!!!!
        !!!!!  Check to make sure photoelectron cross section is correct !!!!
    """
    ID=checkID(ID)
    E1=eV(E1)/1000
    E2=eV(E2)/1000
    E=n.linspace(E1,E2,N)
    J=n.zeros(N)
    ii=0
    for i in E:
      J[ii]=DoseMaxEnergy(ID,FWHM,dose,i,CS)
      ii+=1
    tstr="Pulse energy to reach %3.3f eV/atom in %s" % (dose,ID) 
    FWHMum=FWHM*u['um']
    lstr="%4.1f um FWHM" % FWHMum 
    fig=figure()
    plot(E,J*u['mJ'],'b.-',label=lstr)
    ax=fig.add_subplot(111)
    ylabel('Pulse Energy (mJ)')
    xlabel('Photon Energy (keV)')
    title(tstr)
    legend(loc=2)
    autoscale(tight=True)
    grid(True)

def Celsius2Kelvin(temp):
    """ Converts from Celsius to Kelvin """
    T=temp+273.15
    return T
 
def Kelvin2Celsius(temp):
    """ Converts from Kelvin to Celsius """
    T=temp-273.15
    return T
 
def Celsius2Fahrenheit(temp):
    """ Converts from Celsius to Fahrenheit """
    T=temp*9./5+32
    return T
 
def Fahrenheit2Celsius(temp):
    """ Converts from Fahrenheit to Celsius """
    T=(temp-32)*5./9
    return T
 
def Kelvin2Fahrenheit(temp):
    """ Converts from Celsius to Fahrenheit """
    T=temp*9./5-459.67
    return T
 
def Fahrenheit2Kelvin(temp):
    """ Converts from Fahrenheit to Celsius """
    T=(temp+459.67)*5./9
    return T
 
def mirrorReflectivity(Angle,E=None,ID='Si',SurfRoughness=0):
    """Computes the mirror reflectivity (assumes s-polarization)
       Angle is the x-ray incidence angle in degrees
       E is photon energy in eV or keV (default is LCLS value)
       ID is mirror chemical fomula : 'Si' -- default is 'Si'
       SurfRoughness is the high spatial frequency roughness in m
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    E=eV(E)/1000
    l=lam(E)
    ki=2*n.pi*sind(Angle)/l
    kt=2*n.pi*(index(ID,E)**2-cosd(Angle)**2)**0.5/l
    R=(n.abs((ki-kt)/(ki+kt)*n.exp(-2*ki*kt*SurfRoughness**2)))**2
    return R

def mirrorReflectivityPlotFixedA(E1,E2,Angle,ID='Si',SurfRoughness=0,N=100):
    """Plots the mirror reflectivity (assumes s-polarization) as a function of photon energy
       Angle is the x-ray incidence angle in degrees
       E1,E2 is photon energy range in eV or keV 
       ID is mirror chemical fomula : 'Si' -- default is 'Si'
       SurfRoughness is the high spatial frequency roughness in m
       N is the number of data points (default is 100)
    """
    ID=checkID(ID)
    E1=eV(E1)/1000
    E2=eV(E2)/1000
    E=n.linspace(E1,E2,N)
    R=n.zeros(N)
    ii=0
    for i in E:
      R[ii]=mirrorReflectivity(Angle,i,ID,SurfRoughness)
      ii+=1
    surfR=SurfRoughness*u['nm']
    tstr="%s reflectivity at %3.3f deg with %3.3f nm rougness" % (ID,Angle,surfR) 
    fig=figure()
    plot(E,R,'b.-')
    ax=fig.add_subplot(111)
    ylabel('Reflectivity')
    xlabel('Photon Energy (keV)')
    suptitle('Mirror Reflectivity Plot')
    title(tstr)
    autoscale(tight=True)
    grid(True)

def mirrorReflectivityPlotFixedE(A1,A2,E=None,ID='Si',SurfRoughness=0,N=100):
    """Plots the mirror reflectivity (assumes s-polarization) as a function of angle
       A1,A2 is the x-ray incidence angle range in degrees
       E is photon energy in eV or keV 
       ID is mirror chemical fomula : 'Si' -- default is 'Si'
       SurfRoughness is the high spatial frequency roughness in m
       N is the number of data points (default is 100)
    """
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    E=eV(E)/1000
    ID=checkID(ID)
    A=n.linspace(A1,A2,N)
    R=n.zeros(N)
    ii=0
    for i in A:
      R[ii]=mirrorReflectivity(i,E,ID,SurfRoughness)
      ii+=1
    surfR=SurfRoughness*u['nm']
    tstr="%s reflectivity at %3.3f keV with %3.3f nm rougness" % (ID,E,surfR) 
    fig=figure()
    plot(A,R,'b.-')
    ax=fig.add_subplot(111)
    ylabel('Reflectivity')
    xlabel('Incidence Angle (deg)')
    suptitle('Mirror Reflectivity Plot')
    title(tstr)
    autoscale(tight=True)
    grid(True)

def mirrorRejection(Angle,E=None,ID='Si',SurfRoughness=0):
    """Computes the 3rd harmonic rejection factor of a single mirror bounce
       Angle is the x-ray incidence angle in degrees
       E is photon energy in eV or keV (default is LCLS value)
       ID is mirror chemical fomula : 'Si' -- default is 'Si'
       SurfRoughness is the high spatial frequency roughness in m
    """
    ID=checkID(ID)
    Rej=mirrorReflectivity(Angle,3*E,ID,SurfRoughness)/mirrorReflectivity(Angle,E,ID,SurfRoughness)   
    return Rej


def dSpace(ID,hkl):
    """ Computes the d spacing (m) of the specified material and reflection 
        ID is chemical fomula : 'Si'
        hkl is the reflection : (1,1,1)
    """
    ID=checkID(ID)
    h=hkl[0]
    k=hkl[1]
    l=hkl[2]

    lp=latticeParameters[ID]
    a=lp[0]/u['ang']
    b=lp[1]/u['ang']
    c=lp[2]/u['ang']
    alpha=lp[3]
    beta=lp[4]
    gamma=lp[5]

    ca=cosd(alpha)
    cb=cosd(beta)
    cg=cosd(gamma)
    sa=sind(alpha)
    sb=sind(beta)
    sg=sind(gamma)

    invdsqr=1/(1+2*ca*cb*cg-ca**2-cb**2-cg**2)*(h**2*sa**2/a**2 + k**2*sb**2/b**2 + l**2*sg**2/c**2 +
      2*h*k*(ca*cb-cg)/a/b+2*k*l*(cb*cg-ca)/b/c+2*h*l*(ca*cg-cb)/a/c)
      
    d=invdsqr**-0.5
    return d


def BraggAnglePlot(ID,hkl,E1,E2,N=100):
    """ Plots the Bragg angle (deg) of the specified material, reflection as a function of photon energy 
        ID is chemical fomula : 'Si'
        hkl is the reflection : (1,1,1)
        E1,E2 is photon energy range in eV or keV 
        N is the number of data points (default is 100)
    """
    ID=checkID(ID)
    d=dSpace(ID,hkl)
    E1=eV(E1)/1000
    E2=eV(E2)/1000
    E=n.linspace(E1,E2,N)
    theta=n.zeros(N)
    ii=0
    for i in E:
      theta[ii] = asind(lam(i)/2/d)
      ii+=1
    tstr="%s %s" % (ID,hkl) 
    fig=figure()
    plot(E,theta,'b.-')
    ax=fig.add_subplot(111)
    ylabel('Bragg Angle (deg)')
    xlabel('Photon Energy (keV)')
    suptitle('Bragg Angle')
    title(tstr)
    autoscale(tight=True)
    grid(True)

   
def BraggAngle(ID,hkl,E=None):
    """ Computes the Bragg angle (deg) of the specified material, reflection and photon energy 
        ID is chemical fomula : 'Si'
        hkl is the reflection : (1,1,1)
        E is photon energy in eV or keV (default is LCLS value)
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")
    d=dSpace(ID,hkl)
    theta = asind(lam(E)/2/d)
    return theta


def BraggEnergy(ID,hkl,twotheta):
    """ Computes the photon energy that satisfies the Bragg condition of the specified material, reflection and twotheta angle 
        ID is chemical fomula : 'Si'
        hkl is the reflection : (1,1,1)
        twotheta is the scattering angle in degrees
    """
    ID=checkID(ID)
    d=dSpace(ID,hkl)
    l=2*d*sind(twotheta/2.0)
    E=lam2E(l)
    return E

def StructureFactor(ID,f,hkl,z=None):
    """ Computes the structure factor
        ID is chemical fomula : 'Si'
        f is the atomic form factor
        hkl is the reflection : (1,1,1)
        z is the rhombohedral lattice parameter
    """
    ID=checkID(ID)
    i=complex(0,1)
    h=hkl[0]
    k=hkl[1]
    l=hkl[2] 
    L=latticeType[ID]
    if L=='fcc':
      F=f*(1+n.exp(-i*n.pi*(k+l))+n.exp(-i*n.pi*(h+l))+n.exp(-i*n.pi*(h+k)))
    elif L=='bcc':
      F=f*(1+n.exp(-i*n.pi*(h+k+l)))  
    elif L=='cubic':
        F=f;
    elif L=='diamond':
        F=f*(1+n.exp(-i*n.pi*(k+l))+n.exp(-i*n.pi*(h+l))+n.exp(-i*n.pi*(h+k)))*(1+n.exp(-i*2*n.pi*(h/4.0+k/4.0+l/4.0)))
    elif L=='rhomb':
        z=latticeParamRhomb[ID]
        F=f*(1+n.exp(2*i*n.pi*(h+k+l)*z)) 
    elif L=='tetr':
        F=f;
    elif L=='hcp':
        F=f*(1+n.exp(2*i*n.pi*(h/3.0+2*k/3.0+l/2.0)))
    return F

def UnitCellVolume(ID):
    """ Returns the unit cell volume in m^3
        ID is chemical fomula : 'Si'
    """   
    ID=checkID(ID)
    lp=latticeParameters[ID]
    a=lp[0]/u['ang']
    b=lp[1]/u['ang']
    c=lp[2]/u['ang']
    alpha=lp[3]
    beta=lp[4]
    gamma=lp[5]
    L=latticeType[ID]
    ca=cosd(alpha)
    cb=cosd(beta)
    cg=cosd(gamma)
    V=a*b*c*n.sqrt(1-ca**2-cb**2-cg**2+2*ca*cb*cg)
    return V

def DebyeWallerFactor(ID,hkl,T=293,E=None):
    """ Computes the Debye Waller factor for a specified reflection
        ID is chemical fomula : 'Si'
        T is the crystal temperature in Kelvin (default is 293)
        E is photon energy in eV or keV (default is LCLS value)
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")
    theta=BraggAngle(ID,hkl,E)
    l=lam(E)*u['ang']
    T_Debye=debyeTemp[ID]
    mass=MolecularMass(ID)
    y=lambda x: x/(n.exp(x)-1)
    ratio=T_Debye/float(T)
    intgrl,err=s.integrate.quad(y,1e-9,ratio)
    phi=intgrl*T/T_Debye    
    B=11492*T*phi/(mass*T_Debye**2)+2873/(mass*T_Debye)
    M=B*(sind(theta)/l)**2
    DWfactor=n.exp(-M)
    return DWfactor

def DarwinWidth(ID,hkl,E=None,T=293):
    """ Computes the Darwin width for a specified crystal reflection (degrees)
        ID is chemical fomula : 'Si'
        hkl is the reflection : (1,1,1)
        E is photon energy in eV or keV (default is LCLS value)
        T is the crystal temperature in Kelvin (default is 293)
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")
    theta=BraggAngle(ID,hkl,E)
    l=lam(E)
    f=FF(ID,2*theta,E)
    F=StructureFactor(ID,f,hkl)
    V=UnitCellVolume(ID)
    dw=(2*c['eRad']*l**2*n.abs(F))/(n.pi*V*sind(2*theta))/u['rad']
    return dw

def XtalParams(ID,hkl,E=None,T=293):
    """ Prints the Xtal parameters for the specified reflection
        ID is chemical fomula : 'Si'
        hkl is the reflection : (1,1,1)
        E is photon energy in eV or keV (default is LCLS value)
        T is the crystal temperature in Kelvin (default is 293)
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")
    theta=BraggAngle(ID,hkl,E)
    l=lam(E)*u['ang']
    L=latticeType[ID]
    d=dSpace(ID,hkl)*u['ang']
    f=n.abs(FF(ID,2*theta,E))
    F=n.abs(StructureFactor(ID,f,hkl))
    V=UnitCellVolume(ID)
    DWfactor=DebyeWallerFactor(ID,hkl,T,E)
    pFactor=cosd(theta*2)**2
    dw=DarwinWidth(ID,hkl,E,T)
    DeltaEoE=1/tand(theta)*dw*u['rad']
    dw_mdeg=dw*u['mdeg']
    dw=dw*u['asec']
    DeltaE=DeltaEoE*E*1000
    str ='     Crystal = %s \n' % ID
    str+='     Lattice = %s \n' % L
    str+='  Wavelength = %3.3f Ang \n' % l
    str+='   d spacing = %3.3f Ang \n' % d
    str+=' Bragg Angle = %3.3f deg \n' % theta
    str+='           f = %3.2f  \n' % f
    str+='           F = %3.2f  \n' % F
    str+='Debye Waller = %3.3f  \n' % DWfactor
    str+=' Pol. Factor = %3.3f  \n' % pFactor
    str+='Darwin Width = %3.2f arcsec  (%3.3f mdeg) \n' % (dw,dw_mdeg)
    str+='    DeltaE/E = %1.3g  \n' % DeltaEoE
    str+='      DeltaE = %3.3f eV \n' % DeltaE
    print str 

 
def LOMparams(E=None):
    """ Prints the LOM parameters for the specificed photon energy (default is LCLS value) """
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")
    th1=BraggAngle('Si',(1,1,1),E)
    z1=0.3/tand(2*th1)*u['mm']
    app1=4.8e-3*sind(th1)
    pFac1=(cosd(2*th1))**4*100

    th2=BraggAngle('Si',(2,2,0),E)
    z2=0.3/tand(2*th2)*u['mm']
    app2=4.8e-3*sind(th2)
    pFac2=(cosd(2*th2))**4*100

    str='\n******* Si (111) *********\n'
    str+='   Theta = %3.5f deg \n' % th1
    str+='       Z = %3.3f mm \n' % z1
    str+='Aperture = %3.2f mm \n' % app1
    str+=' pFactor = %3.2f %% \n' % pFac1
    str+='\n'
    str+='\n******* Si (220) *********\n'
    str+='   Theta = %3.5f deg \n' % th2
    str+='       Z = %3.3f mm \n' % z2
    str+='Aperture = %3.2f mm \n' % app2
    str+=' pFactor = %3.2f %% \n' % pFac2
    print str


def GaussianFocus(FWHM0,l,f):
    """ Prints the focal properties of a Gaussain beam 
        FWHM0 is the incident FWHM beam size in m
        l is the optical wavelength in m
        f is the lens focal length in m
    """
    w0=0.8493218*FWHM0
    w=l*f/n.pi/w0/(1+(l*f/n.pi/w0**2)**2)**0.5
    RR=n.pi*w**2/l*u['mm']
    FWHM=w/0.8493218*u['mm']
    DOF=2*0.32*n.pi*w**2/l*u['mm']
    str='\n'
    str+='FWHM = %3.4f mm \n' % FWHM
    str+='  RR = %3.4f mm \n' % RR
    str+=' DOF = %3.4f mm \n' % DOF
    print str

def GaussianPropagation(FWHM0,l,z):
    """ Computes the spot size of a Gaussian beam 
        FWHM0 is the incident diffraction limited beam size in m 
        l is the optical wavelength in m
        z is the distance from the source waist in m
    """
    w0=0.8493218*FWHM0
    w=n.sqrt(w0**2+(l*z/n.pi/w0)**2)
    FWHM=w/0.8493218
    return FWHM

def GaussianSpotSize(FWHM0,l,f,df=0):
    """ Computes the spot size of a Gaussian beam 
        FWHM0 is the incident FWHM beam size in m
        l is the optical wavelength in m
        f is the lens focal length in m
        df is the distance from the waist in m
    """
    w0=0.8493218*FWHM0
    ww=l*f/n.pi/w0/(1+(l*f/n.pi/w0**2)**2)**0.5
    w=ww*(1+(l*df/n.pi/ww**2)**2)**0.5
    FWHM=w/0.8493218
    return FWHM


def TTfactor(ID,t,J,FWHM=500e-6,E=None):
    """ Computes the time tool quality factor
        ID is chemical fomula : 'Si'
        t is the target thickness in m
        J is the FEL pulse energy in J
        FWHM is the beam size at the target (default is 500um)
        E is photon energy in eV or keV (default is LCLS value)
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")
    Trans=Transmission_noCompton(ID,t,E)
    TTf=J*(1-Trans)/FWHM**2
    TTf0=1e-3*(1-Transmission('Si3N4',2e-6,9))/(500e-6)**2
    QF=TTf/TTf0
    Ds=Dose(ID,FWHM,J,E)
    str='\n'
    str+='            TT Factor = %3.2f\n' % QF
    str+='  Target Transmission = %3.3f \n' % Trans
    str+='          Target Dose = %3.3f eV/atom \n' % Ds
    try: 
      str+='     Target Melt Dose = %3.3f eV/atom \n' % meltDose[ID] 
      print str
    except:
      print str

def Fluence(J,FWHM,R=0,Angle=90):
    """Returns the absorbed laser fluence in mJ/cm^2
       J is the laser pulse energy in J
       FWHM is the incident laser sport size in m
       R is the sample reflectivity (default is 0)
       Angle in the laser/sample incidence angle (defauly is 90 - normal)
    """
    IF=J/FWHM**2
    F=IF*sind(Angle)*(1-R)*u['mJ']/u['cm']**2
    return F 

def BeamlineTransmission(Air=0,f=None,E=None,LOM=0,CCM=0):
  """Estimates the XPP beamline transmission
     Air is the air path length in meters
     f is the CRL focal length
     E is photon energy in eV or keV (default is LCLS value)
     LOM is a flag if LOM is used (set to 1 if using LOM)
     CCM is a flag if CCM is used (set to 1 if using CCM)
  """
  if f==None:
    LensTrans=1
  else:
    r=LensRadius(f,E,ID='Be') 
    LensTrans=LensTransmission(r,500e-6,1,E)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  T=0.7*Transmission('C',100e-6,E)*gasTransmission('Air',Air,E)*LensTrans*Transmission('Si3N4',4e-6,E)*Transmission('Kapton',75e-6,E)
  if LOM:
    th1=BraggAngle('Si',(1,1,1),E)
    pFac1=(cosd(2*th1))**4
    T=T*pFac1/100
  elif CCM:
    T=T/100
  return T

def BeamlineTransmissionPlot(E1,E2,Air=0,f=None,LOM=0,CCM=0,N=20):
  """Plots the estimated XPP beamline transmission
     E1 and E2 is the photon energy range
     Air is the air path length in meters
     f is the CRL focal length
     LOM is a flag if LOM is used (set to 1 if using LOM)
     N is the number of points
     CCM is a flag if CCM is used (set to 1 if using CCM)
  """
  E1=eV(E1)/1000
  E2=eV(E2)/1000
  E=n.linspace(E1,E2,N)
  T=n.zeros(N)
#  TT=n.zeros(N)
  ii=0
  for i in E:
    T[ii]=BeamlineTransmission(Air,f,i,LOM,CCM)
#    TT[ii]=BeamlineTransmission(Air,4.5,i,LOM,CCM)
    ii+=1
  if LOM:
    tstr="Beamline Transmission with %3.2f m air, %3.1f m lens, and LODCM" % (Air,f) 
  elif CCM:
    tstr="Beamline Transmission with %3.2f m air, %3.1f m lens, and CCM" % (Air,f) 
  else:
    tstr="Beamline Transmission with %3.2f m air, %3.1f m lens" % (Air,f) 
  figure(10)
  clf()
  plot(E,T,'b.-')
#  plot(E,T,'b.-',E,TT,'r.-')
  xlabel('Photon Energy (eV)')
  ylabel('Beamline Transmission')
#  legend(('100 um','50 um'),loc='upper left')
  title(tstr)
  grid(True)


def LensEffectiveR(R,N=1):
    """Returns the effective single lens radius 
       R is the Radius of curvature (100e-6, 200e-6)
       N is the number of each curvature (3,1)
       Examples:
         LensEffectiveR((200,100),(3,1)) -- 200x3 + 100x1
         LensEffectiveR(200,3) -- 200x3 
         LensEffectiveR((200,100)) -- 200x1 + 100x1
         LensEffectiveR((200,100),3) -- 200x3 + 100x3
    """
    R=n.array(R,dtype=float)
    N=n.array(N,dtype=float)
    try:
      r=1./sum(N/R)
    except:
      R=float(R)
      r=1./(N/R)
    return r

def LensFocalLength(r,E=None,ID='Be'):
  """Returns the CRL focal length
     r is the effective radius of curvature
     E is the photon energy (default us current LCLS value)
     ID is the lens material (default is Be)
  """
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  d=Density[ID]
  n_real=xraylib.Refractive_Index_Re(ID,E,d)
  delta=1-n_real
  f=r/2/delta
  return f

def LensRadius(f,E=None,ID='Be'):
  """Returns the CRL radius required to achieve the specified focal length
     f is the focal length in meters
     E is the photon energy (default us current LCLS value)
     ID is the lens material (default is Be)
  """
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  d=Density[ID]
  n_real=xraylib.Refractive_Index_Re(ID,E,d)
  delta=1-n_real
  r=2*delta*f
  return r


def CRLplot(E=None):
  """Plots to spot size of the XPP CRLs
     E is the photon energy (default us current LCLS value)
  """
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  R=n.zeros(3)
  R[0]=LensEffectiveR((100e-6,200e-6),(1,1))
  R[1]=LensEffectiveR((200e-6,500e-6),(2,4))
  #R[2]=LensEffectiveR(100e-6,3)
  R[2]=LensEffectiveR((300e-6,200e-6),(7,2))
  f=n.zeros(3)
  d=n.linspace(3,5,1000)
  df=n.zeros((3,1000))
  FWHM=df
  for i in range(0,3):
    f[i]=LensFocalLength(R[i],E)
    df[i,:]=f[i]-d
    FWHM[i][:]=GaussianSpotSize(500e-6,lam(E),f[i],df[i])*u['um']
  tstr="X-ray Spot Size at %3.3f keV" % (E) 
  figure(10)
  clf()
  plot(d,FWHM[0][:],d,FWHM[1][:],d,FWHM[2][:])
  ylabel('FWHM Spot Size (um)')
  xlabel('Distance from CRLs (m)')
  title(tstr)
  grid(True)
  legend(('Lens Pack 1','Lens Pack 2','Lens Pack 3'),loc='best')


def LensTransmission(r,FWHM,N=1,E=None,ID='IF1'):
  """Returns the CRL lens transmission
     r is the effective radius of curvature
     FWHM is the incident beam size on the lens in meters
     N is the number of lenses in the stack
     E is the photon energy (default us current LCLS value)
     ID is the lens material (default is IF1)
  """
  lthick=30e-6
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  Waist=2*FWHM/2.36
  X=n.linspace(-2*FWHM,2*FWHM,101)
  Y=X
  Intensity=n.zeros((len(X),len(Y)))
  Thickness=n.zeros((len(X),len(Y))) 
  for i in range(len(X)):
    for j in range(len(Y)):
      Intensity[i,j]=n.abs(n.exp(-2*(X[i]**2+Y[j]**2)/Waist**2))*2/Waist**2/n.pi*(X[2]-X[1])**2
      Thickness[i,j]=(X[i]**2+Y[j]**2)/r+N*lthick
  attLength=attenuationLength(ID,E)
  TransIntensity=Intensity*n.exp(-Thickness/attLength)
  trans=n.sum(TransIntensity)
  return trans

def BlackBody(A,W,T0=292):
  """Function that computes the equilibrium temperature rise of a pure black body
     A is the object surface area in m^2
     W is the absorbed power in the sample in Watts
     T0 is the initial sample temperature in Kelvin
  """
  T=(W/A/c['S-B']+T0**4)**0.25-T0
  return T

def BlackBodyPlot(A,W,T0=292,N=100):
  """Function that plots the equilibrium temperature rise of a pure black body
     A is the object surface area in m^2
     W is the absorbed power in the sample in Watts
     T0 is the initial sample temperature in Kelvin
     N is the number of data points
  """
  P=n.linspace(0,W,N)
  T=BlackBody(A,P,T0)
  Acm=A*u['cm']**2
  tstr="Equilibrium temp of a pure black body with %3.1f cm$^2$ area, %3.0f K T$_o$ " % (Acm,T0) 
  figure(10)
  clf()
  plot(P,T,'b.-')
  xlabel('Deposited Power (W)')
  ylabel('Temperature Rise')
  title(tstr)
  grid(True)
  autoscale(tight=True)

def LOMsim(W,T0=298.5,tt=10000,N=300):
  """Simulates the temperature rise of the LOM thick xtal
     W is the average incident X-ray heat load
     T0 is the initial xtal temperature in K (default is 298.5)
     tt is time axis duration in seconds
     N is the number of data points (default is 300)
  """
  V=6.12  #lom xtal volume in cm^3 
  A=0.002796  #lom xtal surface area in m^2
  Mass=Density['Si']*V   #thermal mass in g
  t=n.linspace(0,tt,N)
  T=n.zeros(N)
  dt=t[1]-t[0]
  Input=W*dt
  T[0]=T0
  Cp=SpecificHeat('Si',T0)*Mass/MolecularMass('Si')
  T[1]=Input/Cp+T[0]
  for i in n.arange(N-2):
    Output=c['S-B']*A*(T[i+1]**4-T0**4)*dt
    Cp=SpecificHeat('Si',T[i+1])*Mass/MolecularMass('Si')
    T[i+2]=(Input-Output)/Cp+T[i+1]
  Acm=A*u['cm']**2
  tstr="Si crystal temp with %3.3f Watts, %3.1f g mass, %3.1f cm$^2$ area, %3.0f K T$_o$ " % (W,Mass,Acm,T0) 
  figure(10)
  clf()
  t=t*u['min']
  plot(t,T,'b.-')
  xlabel('Time (min)')
  ylabel('Xtal Temperature')
  title(tstr)
  grid(True)
#  autoscale(tight=True)


def index(ID,E=None):
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  d=Density[ID]
  n_real=xraylib.Refractive_Index_Re(ID,E,d)
  n_imag=xraylib.Refractive_Index_Im(ID,E,d)
  n=complex(n_real,n_imag)
  return n

def FF(ID,twotheta,E=None):
  """
  Returns the atomic form factor for Rayleigh scattering
  ID is the element name
  twotheta is the scattering angle in degrees
  E is the photon energy (default us current LCLS value)
  """
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  ID=checkID(ID)
  z=elementZ[ID]
  q=MomentumTransfer(E,twotheta)
  f=xraylib.FF_Rayl(z,q)
  return f

def SF(ID,twotheta,E=None):
  """
  Returns the incoherent scattering factor for Compton scattering
  ID is the element name
  twotheta is the scattering angle in degrees
  E is the photon energy (default us current LCLS value)
  """
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  z=elementZ[ID]
  q=MomentumTransfer(E,twotheta)
  f=xraylib.SF_Compt(z,q)
  return f

def MomentumTransfer(E,twotheta):
  """Returns the momentum transfer in Ang^-1 from xraylib [sin(2theta)/lam]
     E is the photon energy (eV or KeV)
     twotheta is the scattering angle in degrees
  """
  E=eV(E)/1000
  th = n.deg2rad(twotheta)
  p=xraylib.MomentTransf(E,th)
  return p

def Fi(ID,E=None):
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  z=elementZ[ID]
  f=xraylib.Fi(z,E)
  return f

def Fii(ID,E=None):
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  z=elementZ[ID]
  f=xraylib.Fii(z,E)
  return f

def AbsorptionEdges(ID):
  """Prints the absorption edges of a given Atom"""
  z=elementZ[ID]
  n=0
  while xraylib.EdgeEnergy(z,n)>10e-3:
    edge= xraylib.EdgeEnergy(z,n)*1000
    s='%3.1f eV' % edge 
    print s.rjust(11)
    n=n+1

def FlourescenceLines(ID):
  """Prints the Flourescence lines and yield of a given Atom"""
  ID=checkID(ID)
  z=elementZ[ID]
  n=0
  while xraylib.LineEnergy(z,n)>10e-3:
    edge= xraylib.LineEnergy(z,n)*1000
    fyield=xraylib.FluorYield(z,n)
    s='%3.1f eV  %3.5f' % (edge,fyield) 
    print s.rjust(20)
    n=n+1
    if n>3:
      return

def CS_Total(ID,E=None):
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  form=periodictable.formulas.parse_formula(ID)
  CS=0
  for i in range(len(form)):
    id=str(form[i][1])
    atoms=form[i][0]
    CS+=xraylib.CS_Total(elementZ[id],E)*atoms*AtomicMass[id]/c['NA']/u['cm']**2
  return CS


def CS_Photo(ID,E=None):
  """Returns the total photoabsorption cross section in m^2
     ID is the element symbol
     E is the photon energy (default is current LCLS value)
     NOTE: This is per molecule if chemical formula given
  """
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  form=periodictable.formulas.parse_formula(ID)
  CS=0
  for i in range(len(form)):
    id=str(form[i][1])
    atoms=form[i][0]
    CS+=xraylib.CS_Photo(elementZ[id],E)*atoms*AtomicMass[id]/c['NA']/u['cm']**2
  return CS

def CS_PhotoPlot(ID,E1,E2,N=100):
    """ Plots the xraylib photoabsorbtion cross section in megabarns
        ID is element symbol
        E1 and E2 are the photon energy ranges in eV or keV
        N is the number of data points (default is 100)
        NOTE: This is per molecule if chemical formula given
    """
    E1=eV(E1)/1000
    E2=eV(E2)/1000
    E=n.linspace(E1,E2,N)
    CS_ph=n.zeros(N)
    ii=0
    for i in E:
      CS_ph[ii]=CS_Photo(ID,E[ii])
      ii+=1
    tstr="%s" % (ID) 
    fig=figure()
    plot(E,CS_ph*u['Mbarn'],'b.-')
    ax=fig.add_subplot(111)
    ylabel('Cross Section (Mb)')
    xlabel('Photon Energy (keV)')
    suptitle('Photoabsorption Cross section Plot')
    title(tstr)
    autoscale(tight=True)
    grid(True)


def CS_Rayl(ID,E=None):
  """Returns the total Rayleigh (elastic) cross section in m^2
     ID is the element symbol
     E is the photon energy (default is current LCLS value)
  """
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  form=periodictable.formulas.parse_formula(ID)
  CS=0
  for i in range(len(form)):
    id=str(form[i][1])
    atoms=form[i][0]
    CS+=xraylib.CS_Rayl(elementZ[id],E)*atoms*AtomicMass[id]/c['NA']/u['cm']**2
  return CS


def CS_Compt(ID,E=None):
  """Returns the total Compton (inelastic) cross section in m^2
     ID is the element symbol
     E is the photon energy (default is current LCLS value)
  """
  ID=checkID(ID)
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  form=periodictable.formulas.parse_formula(ID)
  CS=0
  for i in range(len(form)):
    id=str(form[i][1])
    atoms=form[i][0]
    CS+=xraylib.CS_Compt(elementZ[id],E)*atoms*AtomicMass[id]/c['NA']/u['cm']**2
  return CS


def CS_KN(E=None):
  """Returns the total Klein-Nishina cross section in m^2
     E is the photon energy (default is current LCLS value)
  """  
  if E==None:
    E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
  E=eV(E)/1000
  CS=xraylib.CS_KN(E)/u['barn']
  return CS

def TempRise(ID,FWHM,J,E=None,T=298):
    """ Computes the temperature rise in condensed matter in K (photoabsoption cross sections) 
        ID is chemical fomula : 'Si'
        FWHM is the FEL spot size
        J is the LCLS pulse energy in Joules 
        E is photon energy in eV or keV (default is LCLS value)
	T is the inital sample temperature in K (default is 298)
    """
    ID=checkID(ID)
    if E==None:
      E=pypsepics.get("SIOC:SYS0:ML00:AO627")/1000
    E=eV(E)/1000
    dose=Dose(ID,FWHM,J,E)*nAtoms(ID)/u['eV']  #domputes the peak abosrbed energy in J/molecule
    Cp=SpecificHeat(ID,T)
    temp=dose*c['NA']/Cp
    return temp 

def TempRisePlot(ID,FWHM,J,E1,E2,T=298,N=100):
    """ Plots the temperature rise in a solid as a function of photon energy
        ID is element symbol
        FWHM is the FEL spot size
        J is the LCLS pulse energy in Joules 
        E1 and E2 are the photon energy ranges in eV or keV
	T is the inital sample temperature in K (default is 298)
        N is the number of data points (default is 100)
    """
    E1=eV(E1)/1000
    E2=eV(E2)/1000
    E=n.linspace(E1,E2,N)
    temp=n.zeros(N)
    ii=0
    for i in E:
      temp[ii]=TempRise(ID,FWHM,J,E[ii],T)
      ii+=1
    tstr="%s at %3.1f K, %3.1f FWHM beam size, %2.1f mJ pulse energy" % (ID,T,FWHM*u['um'],J*u['mJ']) 
    fig=figure()
    plot(E,temp,'b.-')
    ax=fig.add_subplot(111)
    ylabel('Temperature Rise (K)')
    xlabel('Photon Energy (keV)')
    suptitle('Single Pulse Temperature Rise Plot')
    title(tstr)
    autoscale(tight=True)
    grid(True)



def SpecificHeat(ID,T):
  """ Returns the specific heat capacity (J/mol/K) at constant pressure
      T is the material temperature in K
  """
  ID=checkID(ID)
  A=specificHeatParams[ID]
  T=T/1000.  #shomate equation in kiloKelvin
  Cp=A[0]+A[1]*T+A[2]*T**2+A[3]*T**3+A[4]*T**-2
  return Cp

def SpecificHeatPlot(ID,N=100):
  """ Plots the solid phase specific heat capacity (J/mol/K) at constant pressure from 200 K to the melt temp"""
  ID=checkID(ID)
  T=n.linspace(200,meltPoint[ID],N)
  TT=T/1000.
  A=specificHeatParams[ID]
  Cp=A[0]+A[1]*TT+A[2]*TT**2+A[3]*TT**3+A[4]*TT**-2
  tstr="%s" % ID 
  fig=figure()
  plot(T,Cp,'b.-')
  ax=fig.add_subplot(111)
  ylabel('C$_p$ ( J/mol/K )')
  xlabel('Temperature (K)')
  suptitle('Specific Heat')
  title(tstr)
  autoscale(tight=True)
  grid(True)


#define units and constants
u = {'fm': 1e15,
     'pm': 1e12,
     'ang': 1e10,
     'nm': 1e9,
     'um': 1e6,
     'mm': 1e3,
     'cm': 1e2,
     'km': 1e-3,
     'kHz':1e-3,
     'MHz':1e-6,
     'GHz':1e-9,
     'THz':1e-12,
     'PHz':1e-15,
     'inch':39.370079,
     'mile':0.000621,
     'ft':3.28084,
     'yard':1.093613,
     'mil':39.370079*1000,
     'barn':1e28,  
     'Mbarn':1e22,  
     'fs':1e15,
     'ps':1e12,
     'ns':1e9,
     'us':1e6,
     'ms':1e3,
     'min':1/60.,
     'hour':1/3600.,
     'day':1/(3600*24.),
     'mdeg':1e3,
     'udeg':1e6,
     'ndeg':1e9,
     'rad':n.pi/180,
     'mrad':n.pi/180*1e3,
     'urad':n.pi/180*1e6,
     'nrad':n.pi/180*1e9,
     'asec':3600,
     'amin':60,
     'g':1e3,
     'eV':6.2415e+18,
     'erg':1e7,
     'cal':0.239,
     'mJ':1e3,
     'uJ':1e6,
     'nJ':1e9,
     'pJ':1e9,
     'Torr':7.5006e-3
}


# Constants in MKS units
#    NA : Avagadro Constant
#  eRad : Classical electron radius
#     e : electron charge in Coulombs
#     c : speed of light in m
#     h : Plank constant in Js
#  hbar : reduced Plank constant in Js
# emass : electron mass in kg
# pmass : proton mass in kg
#     k : Boltzman constant in J/K
#    mu : Permeability of free space in N/A^2
#    eo : Permittivity of free space in F/m
#   S-B : Stefan-Boltzmann constant
 
c = {'NA': 6.02212e23,
     'eRad':2.81794e-15,  
     'e':1.602176e-19,
     'c':2.99792458e8,  
     'h':6.62606896e-34,
     'hbar':1.054571628e-34,
     'emass':9.10938215e-31, 
     'pmass':1.672621637e-27, 
     'k':1.3806504e-23,
     'mu':12.566370614e-7,  
     'eo':8.854187817e-12,
     'S-B':5.670373e-8,
}

# Element Name
elementName = {'H' :'Hydrogen',
     'He':'Helium',
     'Li':'Lithium',
     'Be':'Beryllium',
     'B':'Boron',
     'C':'Carbon',
     'N':'Nitrogen',
     'O':'Oxygen',
     'F':'Fluorine',
     'Ne':'Neon',
     'Na':'Sodium',
     'Mg':'Magnesium',
     'Al':'Aluminium',
     'Si':'Silicon',
     'P':'Phosphorus',
     'S':'Sulfur',
     'Cl':'Chlorine',
     'Ar':'Argon',
     'K':'Potassium',
     'Ca':'Calcium',
     'Sc':'Scandium',
     'Ti':'Titanium',
     'V':'Vanadium',
     'Cr':'Chromium',
     'Mn':'Manganese',
     'Fe':'Iron',
     'Co':'Cobalt',
     'Ni':'Nickel',
     'Cu':'Copper',
     'Zn':'Zinc',
     'Ga':'Gallium',
     'Ge':'Germanium',
     'As':'Arsenic',
     'Se':'Selenium',
     'Br':'Bromine',
     'Kr':'Krypton',
     'Rb':'Rubidium',
     'Sr':'Strontium',
     'Y':'Yttrium',
     'Zr':'Zirconium',
     'Nb':'Niobium',
     'Mo':'Molybdenum',
     'Tc':'Technetium',
     'Ru':'Ruthenium',
     'Rh':'Rhodium',
     'Pd':'Palladium',
     'Ag':'Silver',
     'Cd':'Cadmium',
     'In':'Indium',
     'Sn':'Tin',
     'Sb':'Antimony',
     'Te':'Tellurium',
     'I':'Iodine',
     'Xe':'Xenon',
     'Cs':'Caesium',
     'Ba':'Barium',
     'La':'Lanthanum',
     'Ce':'Cerium',
     'Pr':'Praseodymium',
     'Nd':'Neodymium',
     'Pm':'Promethium',
     'Sm':'Samarium',
     'Eu':'Europium',
     'Gd':'Gadolinium',
     'Tb':'Terbium',
     'Dy':'Dysprosium',
     'Ho':'Holmium',
     'Er':'Erbium',
     'Tm':'Thulium',
     'Yb':'Ytterbium',
     'Lu':'Lutetium',
     'Hf':'Hafnium',
     'Ta':'Tantalum',
     'W':'Tungsten',
     'Re':'Rhenium',
     'Os':'Osmium',
     'Ir':'Iridium',
     'Pt':'Platinum',
     'Au':'Gold',
     'Hg':'Mercury',
     'Tl':'Thallium',
     'Pb':'Lead',
     'Bi':'Bismuth',
     'Po':'Polonium',
     'At':'Astatine',
     'Rn':'Radon',
     'Fr':'Francium',
     'Ra':'Radium',
     'Ac':'Actinium',
     'Th':'Thorium',
     'Pa':'Protactinium',
     'U':'Uranium',
     'Np':'Neptunium',
     'Pu':'Plutonium'
}


# Chemical Formula Aliases
alias={'Air':'N1.562O.42C.0003Ar.0094',
       'air':'N1.562O.42C.0003Ar.0094',
       'C*':'C',
       'mylar':'C10H8O4',
       'Mylar':'C10H8O4',
       'polyimide':'C22H10N2O5',
       'Polyimide':'C22H10N2O5',
       'kapton':'C22H10N2O5',
       'Kapton':'C22H10N2O5',
       '304SS':'Fe.68Cr.2Ni.1Mn.02',
       'Acetone':'C3H6O',
       'acetone':'C3H6O',
       'PMMA':'C5H8O2',
       'Teflon':'C2F4',
       'teflon':'C2F4',
       'Toluene':'C7H8',
       'toluene':'C7H8',
       'FS':'SiO2',
       'GGG':'Gd3Ga5O12',
       'quartz':'SiO2',
       'Quartz':'SiO2',
       'Silica':'SiO2',
       'silica':'SiO2',
       'water':'H2O',
       'Water':'H2O',
       'Calcite':'CaCO3',
       'calcite':'CaCO3',
       'YAG':'Y3Al5O12',
       'yag':'Y3Al5O12',
       'Sapphire':'Al2O3',
       'sapphire':'Al2O3',
       'Blood':'CHN.3O7.6',
       'LMSO':'La0.7Sr0.3MnO3',
       'blood':'CHN.3O7.6',
       'Bone':'C1.5H0.3O4.3N0.4PCa2.2',
       'bone':'C1.5H0.3O4.3N0.4PCa2.2',
       'IF1':'Be0.9983O0.0003Al0.0001Ca0.0002C0.0003Cr0.000035Co0.000005Cu0.00005Fe0.0003Pb0.000005Mg0.00006Mn0.00003Mo0.00001Ni0.0002Si0.0001Ag0.000005Ti0.00001Zn0.0001',
       'PF60':'Be.994O.004Al.0005B.000003Cd.0000002Ca.0001C.0006Cr.0001Co.00001Cu.0001Fe.0008Pb.00002Li.000003Mg.00049Mn.0001Mo.00002Ni.0002N.0003Si.0004Ag.00001'
}



# Atomic Number
elementZ = {'H' :1,
     'He':2,
     'Li':3,
     'Be':4,
     'B':5,
     'C':6,
     'N':7,
     'O':8,
     'F':9,
     'Ne':10,
     'Na':11,
     'Mg':12,
     'Al':13,
     'Si':14,
     'P':15,
     'S':16,
     'Cl':17,
     'Ar':18,
     'K':19,
     'Ca':20,
     'Sc':21,
     'Ti':22,
     'V':23,
     'Cr':24,
     'Mn':25,
     'Fe':26,
     'Co':27,
     'Ni':28,
     'Cu':29,
     'Zn':30,
     'Ga':31,
     'Ge':32,
     'As':33,
     'Se':34,
     'Br':35,
     'Kr':36,
     'Rb':37,
     'Sr':38,
     'Y':39,
     'Zr':40,
     'Nb':41,
     'Mo':42,
     'Tc':43,
     'Ru':44,
     'Rh':45,
     'Pd':46,
     'Ag':47,
     'Cd':48,
     'In':49,
     'Sn':50,
     'Sb':51,
     'Te':52,
     'I':53,
     'Xe':54,
     'Cs':55,
     'Ba':56,
     'La':57,
     'Ce':58,
     'Pr':59,
     'Nd':60,
     'Pm':61,
     'Sm':62,
     'Eu':63,
     'Gd':64,
     'Tb':65,
     'Dy':66,
     'Ho':67,
     'Er':68,
     'Tm':69,
     'Yb':70,
     'Lu':71,
     'Hf':72,
     'Ta':73,
     'W':74,
     'Re':75,
     'Os':76,
     'Ir':77,
     'Pt':78,
     'Au':79,
     'Hg':80,
     'Tl':81,
     'Pb':82,
     'Bi':83,
     'Po':84,
     'At':85,
     'Rn':86,
     'Fr':87,
     'Ra':88,
     'Ac':89,
     'Th':90,
     'Pa':91,
     'U':92,
     'Np':93,
     'Pu':94
}


# Atomic Weight, unit are amu
AtomicMass = {'H' :1.00794,
     'He':4.002602,
     'Li':6.941,
     'Be':9.012182,
     'B':10.811,
     'C':12.0107,
     'N':14.0067,
     'O':15.9994,
     'F':18.9984032,
     'Ne':20.1797,
     'Na':22.98976928,
     'Mg':24.3050,
     'Al':26.9815386,
     'Si':28.0855,
     'P':30.973762,
     'S':32.065,
     'Cl':35.453,
     'Ar':39.948,
     'K':39.0983,
     'Ca':40.078,
     'Sc':44.955912,
     'Ti':47.867,
     'V':50.9415,
     'Cr':51.9961,
     'Mn':54.938045,
     'Fe':55.845,
     'Co':58.933195,
     'Ni':58.6934,
     'Cu':63.546,
     'Zn':65.38,
     'Ga':69.723,
     'Ge':72.64,
     'As':74.92160,
     'Se':78.96,
     'Br':79.904,
     'Kr':83.798,
     'Rb':85.4678,
     'Sr':87.62,
     'Y':88.90585,
     'Zr':91.224,
     'Nb':92.90638,
     'Mo':95.96,
     'Tc':98,
     'Ru':101.07,
     'Rh':102.90550,
     'Pd':106.42,
     'Ag':107.8682,
     'Cd':112.411,
     'In':114.818,
     'Sn':118.710,
     'Sb':121.760,
     'Te':127.60,
     'I':126.9044,
     'Xe':131.293,
     'Cs':132.9054519,
     'Ba':137.327,
     'La':138.90547,
     'Ce':140.116,
     'Pr':140.90765,
     'Nd':144.242,
     'Pm':145,
     'Sm':150.36,
     'Eu':151.964,
     'Gd':157.25,
     'Tb':158.92535,
     'Dy':162.500,
     'Ho':164.93032,
     'Er':167.259,
     'Tm':168.93421,
     'Yb':173.054,
     'Lu':174.9668,
     'Hf':178.49,
     'Ta':180.94788,
     'W':183.84,
     'Re':186.207,
     'Os':190.23,
     'Ir':192.217,
     'Pt':195.084,
     'Au':196.966569,
     'Hg':200.59,
     'Tl':204.3833,
     'Pb':207.2,
     'Bi':208.9804,
     'Po':210,
     'At':210,
     'Rn':222,
     'Fr':223,
     'Ra':226,
     'Ac':227,
     'Th':232.03806,
     'Pa':231.03588,
     'U':238.02891,
     'Np':237,
     'Pu':244
}


# Material density in g/cm^3
Density = {'H' :0.00008988,
     'He':0.0001785,
     'Li':0.543,
     'Be':1.85,
     'B':2.34,
     'C':3.5,
     'N':0.0012506,
     'O':0.001429,
     'F':0.001696,
     'Ne':0.0008999,
     'Na':0.971,
     'Mg':1.738,
     'Al':2.698,
     'Si':2.3296,
     'P':1.82,
     'S':2.067,
     'Cl':0.003214,
     'Ar':0.0017837,
     'K':0.862,
     'Ca':1.54,
     'Sc':2.989,
     'Ti':4.54,
     'V':6.11,
     'Cr':7.15,
     'Mn':7.44,
     'Fe':7.874,
     'Co':8.86,
     'Ni':8.912,
     'Cu':8.96,
     'Zn':7.134,
     'Ga':5.907,
     'Ge':5.323,
     'As':5.776,
     'Se':4.809,
     'Br':3.122,
     'Kr':0.003733,
     'Rb':1.532,
     'Sr':2.64,
     'Y':4.469,
     'Zr':6.506,
     'Nb':8.57,
     'Mo':10.22,
     'Tc':11.5,
     'Ru':12.37,
     'Rh':12.41,
     'Pd':12.02,
     'Ag':10.501,
     'Cd':8.69,
     'In':7.31,
     'Sn':7.287,
     'Sb':6.685,
     'Te':6.232,
     'I':4.93,
     'Xe':0.005887,
     'Cs':1.873,
     'Ba':3.594,
     'La':6.145,
     'Ce':6.77,
     'Pr':6.773,
     'Nd':7.007,
     'Pm':7.26,
     'Sm':7.52,
     'Eu':5.243,
     'Gd':7.895,
     'Tb':8.229,
     'Dy':8.55,
     'Ho':8.795,
     'Er':9.066,
     'Tm':9.321,
     'Yb':6.965,
     'Lu':9.84,
     'Hf':13.31,
     'Ta':16.654,
     'W':19.25,
     'Re':21.02,
     'Os':22.61,
     'Ir':22.56,
     'Pt':21.46,
     'Au':19.282,
     'Hg':13.5336,
     'Tl':11.85,
     'Pb':11.342,
     'Bi':9.807,
     'Po':9.32,
     'At':7,
     'Rn':0.00973,
     'Fr':1.87,
     'Ra':5.5,
     'Ac':10.07,
     'Th':11.72,
     'Pa':15.37,
     'U':18.95,
     'Np':20.45,
     'Pu':19.84,
     'H2O':1.0,
     'B4C':2.52,
     'SiC':3.217,
     'SiO2':2.2,
     'Al2O3':3.97,
     'ZnSe':5.42,
     'ZnTe':6.34,
     'CdS':6.749,
     'CdSe':7.01,
     'CdTe':7.47,
     'BN':3.49,
     'GaSb':5.619,
     'GaAs':5.316,
     'GaMnAs':5.316,
     'GaP':4.13,
     'InP':4.787,
     'InAs':5.66,
     'InSb':5.775,
     'TaC':13.9,
     'TiB2':4.52,
     'YAG':4.55,
     'CuBe':8.96,
     'ZnO':5.606,
     'SiC2':3.217,
     'AlN':3.3,
     'Si3N4':3.44,
     'CaF2':3.18,
     'LiF':2.635,
     'KF':2.48,
     'PbF2':8.24,
     'SrF2':4.24,
     'KBr':2.75,
     'ZrO2':5.6,
     'Gd3Ga5O12':7.08,
     'CaSiO5':2.4,
     'LaMnO3':5.7,
     'LaAlO3':6.52,
     'La0.7Sr0.3MnO3':6.17,
     'La0.5Ca0.5MnO3':6.3,
     'Fe.68Cr.2Ni.1Mn.02':8.03,
     'CaSO4H4O2':2.32,
     'C10H8O4':1.4,
     'C22H10N2O5':1.43,
     'C3H6O':0.79,
     'C5H8O2':1.19,
     'C2F4':2.2,
     'C7H8':0.867,
     'Y3Al5O12':4.56,
     'CHN.3O7.6':1.06,
     'C1.5H0.3O4.3N0.4PCa2.2':1.92,
     'Be0.9983O0.0003Al0.0001Ca0.0002C0.0003Cr0.000035Co0.000005Cu0.00005Fe0.0003Pb0.000005Mg0.00006Mn0.00003Mo0.00001Ni0.0002Si0.0001Ag0.000005Ti0.00001Zn0.0001':1.85,
     'Be.994O.004Al.0005B.000003Cd.0000002Ca.0001C.0006Cr.0001Co.00001Cu.0001Fe.0008Pb.00002Li.000003Mg.00049Mn.0001Mo.00002Ni.0002N.0003Si.0004Ag.00001':1.85
}


 
# Melting point in K
meltPoint = {'H' :14.175,
     'He':None,
     'Li':453.85,
     'Be':1560,
     'B':2573,
     'C':3948,
     'N':63.29,
     'O':50.5,
     'F':53.65,
     'Ne':24.703,
     'Na':371,
     'Mg':923,
     'Al':933.4,
     'Si':1683,
     'P':317.25,
     'S':388.51,
     'Cl':172.25,
     'Ar':83.96,
     'K':336.5,
     'Ca':1112,
     'Sc':1812,
     'Ti':1933,
     'V':2175,
     'Cr':2130,
     'Mn':1519,
     'Fe':1808,
     'Co':1768,
     'Ni':1726,
     'Cu':1357.75,
     'Zn':692.88,
     'Ga':302.91,
     'Ge':1211.45,
     'As':1090,
     'Se':494,
     'Br':266.05,
     'Kr':115.93,
     'Rb':312.79,
     'Sr':1042,
     'Y':1799,
     'Zr':2125,
     'Nb':2741,
     'Mo':2890,
     'Tc':2473,
     'Ru':2523,
     'Rh':2239,
     'Pd':1825,
     'Ag':1234,
     'Cd':594.33,
     'In':429.91,
     'Sn':505.21,
     'Sb':904.05,
     'Te':722.8,
     'I':386.65,
     'Xe':161.45,
     'Cs':301.7,
     'Ba':1002,
     'La':1193,
     'Ce':1071,
     'Pr':1204,
     'Nd':1289,
     'Pm':1204,
     'Sm':1345,
     'Eu':1095,
     'Gd':1585,
     'Tb':1630,
     'Dy':1680,
     'Ho':1743,
     'Er':1795,
     'Tm':1818,
     'Yb':1097,
     'Lu':1936,
     'Hf':2500,
     'Ta':3269,
     'W':3680,
     'Re':3453,
     'Os':3300,
     'Ir':2716,
     'Pt':2045,
     'Au':1337.73,
     'Hg':234.43,
     'Tl':577,
     'Pb':600.75,
     'Bi':544.67,
     'Po':527,
     'At':575,
     'Rn':202,
     'Fr':300,
     'Ra':973,
     'Ac':1323,
     'Th':2028,
     'Pa':1873,
     'U':1405,
     'Np':913,
     'Pu':913,
     'SiO2':1995,
     'Gd3Ga5O12':2023,
     'LaMnO3':523,  # 523 K phase trans, melt point is 2170 K
     'La0.5Ca0.5MnO3':1300,  
     'La0.7Sr0.3MnO3':370, # ferro to para magnetic phase transition
     'LaAlO3':708      # 708 K phase trans, melt point is 2350 K
}

# Boiling point in K 
boilingPoint = {'H':20.28,
     'He':4.22,
     'Li':1615,
     'Be':2742,
     'B':4200,
     'C':4300,
     'N':77.36,
     'O':90.20,
     'F':85.03,
     'Ne':27.07,
     'Na':1156,
     'Mg':1363,
     'Al':2792,
     'Si':3538,
     'P':553,
     'S':717.8,
     'Cl':239.11,
     'Ar':87.30,
     'K':1032,
     'Ca':1757,
     'Sc':3109,
     'Ti':3560,
     'V':3680,
     'Cr':2944,
     'Mn':2334,
     'Fe':3134,
     'Co':3200,
     'Ni':3186,
     'Cu':2835,
     'Zn':1180,
     'Ga':2477,
     'Ge':3106,
     'As':887,
     'Se':958,
     'Br':332,
     'Kr':119.93,
     'Rb':961,
     'Sr':1655,
     'Y':3609,
     'Zr':4682,
     'Nb':5017,
     'Mo':4912,
     'Tc':5150,
     'Ru':4423,
     'Rh':3928,
     'Pd':3236,
     'Ag':2435,
     'Cd':1040,
     'In':2345,
     'Sn':2875,
     'Sb':1860,
     'Te':1261,
     'I':457.4,
     'Xe':165.03,
     'Cs':944,
     'Ba':2170,
     'La':3737,
     'Ce':3716,
     'Pr':3793,
     'Nd':3347,
     'Pm':3273,
     'Sm':2067,
     'Eu':1802,
     'Gd':3546,
     'Tb':3503,
     'Dy':2840,
     'Ho':2993,
     'Er':3503,
     'Tm':2223,
     'Yb':1469,
     'Lu':3675,
     'Hf':4876,
     'Ta':5731,
     'W':5828,
     'Re':5869,
     'Os':5285,
     'Ir':4701,
     'Pt':4098,
     'Au':3129,
     'Hg':630,
     'Tl':1746,
     'Pb':2022,
     'Bi':1837,
     'Po':1235,
     'At':610,
     'Rn':211.3,
     'Fr':950,
     'Ra':2010,
     'Ac':3471,
     'Th':5061,
     'Pa':4300,
     'U':4404,
     'Np':4273,
     'Pu':3501
}

# Dose to reach melting point in eV/atom
meltDose = {'Li':0.043,
     'Be':0.342,
     'B':0.542,
     'C':0.23,
     'Na':0.022,
     'Mg':0.184,
     'Al':0.186,
     'Si':0.3736,
     'Ti':0.504,
     'Cr':0.734,
     'Mn':0.445,
     'Fe':0.514,
     'Co':0.554,
     'Ni':0.495,
     'Cu':0.308,
     'Zn':0.112,
     'Ga':0.0014,
     'Ge':0.2211,
     'Se':0.0407,
     'Rb':0.0046,
     'Sr':0.2388,
     'Zr':0.5611,
     'Nb':0.7986,
     'Mo':0.9321,
     'Ru':0.583,
     'Rh':0.5,
     'Ag':0.2462,
     'Cd':0.0798,
     'Te':0.1133,
     'Cs':0.0013,
     'Ba':0.2848,
     'Hf':0.7962,
     'Ta':0.9845,
     'W':1.2376,
     'Pt':0.4675,
     'Au':0.2736,
     'Pb':0.0883,
     'Bi':0.0653,
     'B4C':0.6344,
     'SiC':1.006,
     'Al2O3':0.5282,
     'ZnSe':0.3781,
     'ZnTe':0.335,
     'CdS':0.359,
     'CdSe':0.307,
     'CdTe':0.272,
     'BN':0.306,
     'GaSb':0.217,
     'GaAs':0.318,
     'GaP':0.326,
     'InP':0.217,
     'InAs':0.242,
     'InSb':0.088,
     'TaC':1.252,
     'TiB2':0.871,
     'YAG':0.449,
     'Y3Al5O12':0.449,
     'CuBe':0.308,
     'ZnO':0.405,
     'SiC2':1.006,
     'SiO2':1.22,
     'AlN':0.213,
     'Si3N4':0.187,
     'ZrO2':0.257,
     'CaSiO5':0.3,
     '304SS':0.28,
     'CaSO4H4O2':0.581,
} 


# Debye temperature in K
debyeTemp = {
     'Li':344,
     'Be':1440,
     'C':2230,
     'Ne':75,
     'Na':158,
     'Mg':400,
     'Al':428,
     'Si':645,
     'Ar':92,
     'K':91,
     'Ca':230,
     'Sc':360,
     'Ti':420,
     'V':380,
     'Cr':630,
     'Mn':410,
     'Fe':470,
     'Co':445,
     'Ni':450,
     'Cu':343,
     'Zn':327,
     'Ga':320,
     'Ge':374,
     'As':282,
     'Se':90,
     'Kr':72,
     'Rb':56,
     'Sr':147,
     'Y':280,
     'Zr':291,
     'Nb':275,
     'Mo':450,
     'Ru':600,
     'Rh':480,
     'Pd':274,
     'Ag':225,
     'Cd':209,
     'In':108,
     'Sn':200,
     'Sb':211,
     'Te':153,
     'Xe':64,
     'Cs':38,
     'Ba':110,
     'La':142,
     'Gd':200,
     'Dy':210,
     'Yb':120,
     'Lu':210,
     'Hf':252,
     'Ta':240,
     'W':400,
     'Re':430,
     'Os':500,
     'Ir':420,
     'Pt':240,
     'Au':165,
     'Hg':71.9,
     'Tl':78.5,
     'Pb':105,
     'Bi':119,
     'Th':163,
     'U':207,
     'ZnSe':400,
     'ZnTe':223,
     'CdS':219,
     'CdSe':181,
     'CdTe':200,
     'BN':1900,
     'GaSb':265,
     'GaAs':344,
     'GaP':446,
     'InP':321,
     'InAs':249,
     'InSb':202,
     'LaAlO3':720,
     'LaMnO3':500,
}


# Crytal Lattice type
# cubic = cubic
# bcc = body centered cubic
# fcc = face centered cubic
# diamond = diamond
# hcp = hexaganol closed packed
# hex = hexagonal
# rhomb = rhombohedral
# zinc = zinc blende
latticeType = {'H' :'hcp',
     'He':'hcp',
     'Li':'bcc',
     'Be':'hcp',
     'B':'rhomb',
     'C':'diamond',
     'N':'cubic',
     'Ne':'fcc',
     'Na':'bcc',
     'Mg':'hcp',
     'Al':'fcc',
     'Si':'diamond',
     'Ar':'fcc',
     'K':'bcc',
     'Ca':'fcc',
     'Sc':'hcp',
     'Ti':'hcp',
     'V':'bcc',
     'Cr':'bcc',
     'Mn':'cubic',
     'Fe':'bcc',
     'Co':'hcp',
     'Ni':'fcc',
     'Cu':'fcc',
     'Zn':'hcp',
     'Ge':'diamond',
     'As':'rhomb',
     'Se':'hex',
     'Kr':'fcc',
     'Rb':'bcc',
     'Sr':'fcc',
     'Y':'hcp',
     'Zr':'hcp',
     'Nb':'bcc',
     'Mo':'bcc',
     'Tc':'hcp',
     'Ru':'hcp',
     'Rh':'fcc',
     'Pd':'fcc',
     'Ag':'fcc',
     'Cd':'hcp',
     'In':'tetr',
     'Sn':'diamond',
     'Sb':'rhomb',
     'Te':'hex',
     'Xe':'fcc',
     'Cs':'bcc',
     'Ba':'bcc',
     'La':'hex',
     'Ce':'fcc',
     'Pr':'hex',
     'Nd':'hex',
     'Eu':'bcc',
     'Gd':'hcp',
     'Tb':'hcp',
     'Dy':'hcp',
     'Ho':'hcp',
     'Er':'hcp',
     'Tm':'hcp',
     'Yb':'fcc',
     'Lu':'hcp',
     'Hf':'hcp',
     'Ta':'bcc',
     'W':'bcc',
     'Re':'hcp',
     'Os':'fcc',
     'Ir':'fcc',
     'Pt':'fcc',
     'Au':'fcc',
     'Hg':'rhomb',
     'Tl':'hcp',
     'Pb':'fcc',
     'Bi':'rhomb',
     'Po':'cubic',
     'Ac':'fcc',
     'Th':'fcc',
     'Pa':'tetr',
     'ZnSe':'zinc',
     'ZnTe':'zinc',
     'CdS':'zinc',
     'CdSe':'zinc',
     'CdTe':'zinc',
     'BN':'zinc',
     'GaSb':'zinc',
     'GaAs':'zinc',
     'GaMnAs':'zinc',
     'GaP':'zinc',
     'Gd3Ga5O12':'cubic',
     'InP':'zinc',
     'InAs':'zinc',
     'InSb':'zinc',
     'LaMnO3':'ortho',
     'LaAlO3':'rhomb',
     'LaAlO3':'rhomb',
     'La0.7Sr0.3MnO3':'rhomb',
     'GGG':'cubic'
}


# Crystal Lattice parameters (a, b, c, alpha, beta, gamma)
# a,b,c in angstroms
# alpha, beta, gamma in degrees
latticeParameters = {'H' :(3.75,3.75,6.12,90,90,120),
     'He':(3.57,3.57,5.83,90,90,120),
     'Li':(3.491,3.491,3.491,90,90,90),
     'Be':(2.2866,2.2866,3.5833,90,90,120),
     'B':(5.06,5.06,5.06,58.06,58.06,58.06),
     'C':(3.567,3.567,3.567,90,90,90),
     'N':(5.66,5.66,5.66,90,90,90),
     'Ne':(4.66,4.66,4.66,90,90,90),
     'Na':(4.225,4.225,4.225,90,90,90),
     'Mg':(3.21,3.21,5.21,90,90,120),
     'Al':(4.05,4.05,4.05,90,90,90),
     'Si':(5.4310205,5.4310205,5.4310205,90,90,90),
     'Ar':(5.31,5.31,5.31,90,90,90),
     'K':(5.225,5.225,5.225,90,90,90),
     'Ca':(5.58,5.58,5.58,90,90,90),
     'Sc':(3.31,3.31,5.27,90,90,120),
     'Ti':(2.95,2.95,4.68,90,90,120),
     'V':(3.03,3.03,3.03,90,90,90),
     'Cr':(2.88,2.88,2.88,90,90,90),
     'Fe':(2.87,2.87,2.87,90,90,90),
     'Co':(2.51,2.51,4.07,90,90,120),
     'Ni':(3.52,3.52,3.52,90,90,90),
     'Cu':(3.61,3.61,3.61,90,90,90),
     'Zn':(2.66,2.66,4.95,90,90,120),
     'Ge':(5.658,5.658,5.658,90,90,90),
     'As':(4.1018,4.1018,4.1018,54.554,54.554,54.554),
     'Kr':(5.64,5.64,5.64,90,90,90),
     'Rb':(5.585,5.585,5.585,90,90,90),
     'Sr':(6.08,6.08,6.08,90,90,90),
     'Y':(3.65,3.65,5.73,90,90,120),
     'Zr':(3.23,3.23,5.15,90,90,120),
     'Nb':(3.3,3.3,3.3,90,90,90),
     'Mo':(3.15,3.15,3.15,90,90,90),
     'Tc':(2.74,2.74,4.4,90,90,120),
     'Ru':(2.71,2.71,4.28,90,90,120),
     'Rh':(3.8,3.8,3.8,90,90,90),
     'Pd':(3.89,3.89,3.89,90,90,90),
     'Ag':(4.09,4.09,4.09,90,90,90),
     'Cd':(2.98,2.98,5.62,90,90,120),
     'In':(3.25,3.25,4.95,90,90,90),
     'Sn':(6.49,6.49,6.49,90,90,90),
     'Sb':(4.4898,4.4898,4.4898,57.233,57.233,57.233),
     'Xe':(6.13,6.13,6.13,90,90,90),
     'Cs':(6.045,6.045,6.045,90,90,90),
     'Ba':(5.02,5.02,5.02,90,90,90),
     'Ce':(5.16,5.16,5.16,90,90,90),
     'Eu':(4.58,4.58,4.58,90,90,90),
     'Gd':(3.63,3.63,5.78,90,90,120),
     'Tb':(3.6,3.6,5.7,90,90,120),
     'Dy':(3.59,3.59,5.65,90,90,120),
     'Ho':(3.58,3.58,5.62,90,90,120),
     'Er':(3.56,3.56,5.59,90,90,120),
     'Tm':(3.54,3.54,5.56,90,90,120),
     'Yb':(5.45,5.45,5.45,90,90,90),
     'Lu':(3.5,3.5,5.55,90,90,120),
     'Hf':(3.19,3.19,5.05,90,90,120),
     'Ta':(3.3,3.3,3.3,90,90,90),
     'W':(3.16,3.16,3.16,90,90,90),
     'Re':(2.76,2.76,4.46,90,90,120),
     'Os':(2.74,2.74,4.32,90,90,120),
     'Ir':(3.84,3.84,3.84,90,90,90),
     'Pt':(3.92,3.92,3.92,90,90,90),
     'Au':(4.08,4.08,4.08,90,90,90),
     'Tl':(3.46,3.46,5.52,90,90,120),
     'Pb':(4.95,4.95,4.95,90,90,90),
     'Bi':(4.7236,4.7236,4.7236,57.35,57.35,57.35),
     'Po':(3.34,3.34,3.34,90,90,90),
     'Ac':(5.31,5.31,5.31,90,90,90),
     'Th':(5.08,5.08,5.08,90,90,90),
     'Pa':(3.92,3.92,3.24,90,90,90),
     'ZnSe':(5.6676,5.6676,5.6676,90,90,90),
     'ZnTe':(6.101,6.101,6.101,90,90,90),
     'CdS':(5.832,5.832,5.832,90,90,90),
     'CdSe':(6.05,6.05,6.05,90,90,90),
     'CdTe':(6.477,6.477,6.477,90,90,90),
     'BN':(3.615,3.615,3.615,90,90,90),
     'GaSb':(6.0954,6.0954,6.0954,90,90,90),
     'GaAs':(5.65315,5.65315,5.65315,90,90,90),
     'GaMnAs':(5.65,5.65,5.65,90,90,90),
     'GaP':(5.4505,5.4505,5.4505,90,90,90),
     'InP':(5.86875,5.86875,5.86875,90,90,90),
     'InAs':(6.05838,6.05838,6.05838,90,90,90),
     'InSb':(6.47877,6.47877,6.47877,90,90,90),
     'LaMnO3':(5.531,5.602,7.742,90,90,90),  
     'LaAlO3':(5.377,5.377,5.377,60.13,60.13,60.13),
     'La0.7Sr0.3MnO3':(5.4738,5.4738,5.4738,60.45,60.45,60.45),
     'Gd3Ga5O12':(12.383,12.383,12.383,90,90,90)
}

# Rhombohedral Lattice parameter (z)
#latticeParamsRhomb = {'B' :,
#     'As':,
#     'Sb':,
#     'Hg':,
#     'Bi':,
#     'LaAlO3':
#}
 
# specific heat capacity coefficients
# Shomate equation
# Cp = A + B*T + C*T^2 + D*T^3 + E/T^2

specificHeatParams = {'Li' :(169.552,-882.711,1977.438,-1487.312,-1.609635),
    'Be':(21.20694,5.68819,0.968019,-0.001749,-0.587526),
     'B':(10.18574,29.24415,-18.02137,4.212326,-0.551),
     'C':(6.37,0,0,0,0),
    'Na':(72.63675,-9.491572,-730.9322,1414.518,-1.259377),
    'Mg':(26.54083,-1.533048,8.062443,0.57217,-0.174221),
    'Al':(28.0892,-5.414849,8.560423,3.42737,-0.277375),
    'Si':(22.81719,3.89951,-0.082885,0.042111,-0.354063),
    'Ti':(23.0566,5.541331,-2.055881,1.611745,-0.056075),
    'Cr':(7.489737,71.50498,-91.67562,46.0445,0.138157),
    'Mn':(27.2419,5.23764,7.78316,-2.118501,-0.282113),
    'Fe':(23.97449,8.36775,0.000277,-0.000086,-0.000005),
    'Co':(10.9943,54.375,-55.5132,25.817,0.164533),
    'Ni':(13.6916,82.49509,-174.9548,161.6011,-0.092417),
    'Cu':(17.72891,28.0987,-31.25289,13.97243,0.068611),
    'Zn':(25.60123,-4.405292,20.42206,-7.399697,-0.045801),
    'Ga':(102.3394,-347.5134,603.3621,-360.7047,-1.490304),
    'Ge':(23.3667,0,0,0,0),
    'Se':(25.363,0,0,0,0),
    'Rb':(9.44626,65.31182,45.5123,-26.78961,-0.10773),
    'Sr':(23.88223,9.297351,0.919924,0.035243,0.004934),
    'Zr':(25.3924,0.434236,4.384539,1.017123,-0.065449),
    'Nb':(22.0143,9.88816,-5.64853,1.759691,0.021839),
    'Mo':(24.72736,3.960425,-1.270706,1.153065,-0.170246),
    'Rh':(24.9,0,0,0,0),
    'Ag':(25.35,0,0,0,0),
    'Cd':(26.02,0,0,0,0),
    'Te':(25.73,0,0,0,0),
    'Cs':(57.04424,-50.0034,48.595,-16.72822,-1.223804),
    'Ba':(83.8018,-406.186,915.066,-519.805,-0.191854),
    'Hf':(22.71033,10.86443,-1.901809,0.306368,-0.007587),
    'Ta':(20.69482,17.29992,-15.68987,5.608694,0.061581),
     'W':(23.9593,2.63968,1.25775,-0.254642,-0.048407),
    'Pt':(25.86,0,0,0,0),
    'Au':(25.409,0,0,0,0),
    'Pb':(25.0145,5.441836,4.061367,-1.236214,-0.010657),
    'Bi':(25.52,0,0,0,0),
    'B4C':(95.99853,23.16513,-0.409604,0.081414,-4.395208),
    'SiC':(20.55859,64.57962,-52.98827,16.95813,-0.781847),
    'Al2O3':(102.429,38.7498,-15.9109,2.628181,-3.007551),
    'ZnSe':(48.9,0,0,0,0),
    'ZnTe':(50.95,0,0,0,0),
    'CdS':(47.67,0,0,0,0),
    'CdSe':(48.8,0,0,0,0),
    'CdTe':(49.2,0,0,0,0),
    'BN':(19.68,0,0,0,0),
    'GaSb':(61.3,0,0,0,0),
    'GaAs':(50.6,0,0,0,0),
    'GaP':(43.3,0,0,0,0),
    'InSb':(61.3,0,0,0,0),
    'InAs':(50.9,0,0,0,0),
    'InP':(34,0,0,0,0),
    'TaC':(44.29224,7.673707,-0.091309,0.010861,-0.875548),
    'TiB2':(52.33264,33.69484,-7.909266,0.803989,-1.540905),
    'YAG':(376,0,0,0,0),
    'ZnO':(40.2,0,0,0,0),
    'CaSiO5':(111,0,0,0,0),
    'H2O':(75.327,0,0,0,0),
    'CO2':(36.94,0,0,0,0),
    'Fe.68Cr.2Ni.1Mn.02':(27.553,0,0,0,0),
    'SiO2':(-6.07659,251.6755,-324.796,168.5604,0.002548),
    'LaAlO3':(86.6,0,0,0,0),
    'LaMnO3':(89,0,0,0,0),
    'La0.5Ca0.5MnO3':(89,0,0,0,0),
}


