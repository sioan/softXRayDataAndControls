""" Utilities to perfrom various laser calculations """

import numpy as n
import scipy as s
import periodictable
from matplotlib.pyplot import *
from utilitiesCalc import *


def OpticalReflectivity(ID,Ang,l=800e-9,n1=1.0,pol='p'):
  """ Computes the surface reflectivity
      ID is the material ID
      Ang is the incidence angle wrt surface normal
      l is the wavelength in m (default is 800nm)
      pol is the polarization (default is 'p')
      n1 is the incident medium index (default is 1.0)
  """
  n2=OpticalIndex(ID,l)
  if pol=='s':
    R=((n1*cosd(Ang)-n2*n.sqrt(1-(n1*sind(Ang)/n2)**2))/(n1*cosd(Ang)+n2*n.sqrt(1-(n1*sind(Ang)/n2)**2)))**2
  elif pol=='p':
    R=((n1*n.sqrt(1-(n1*sind(Ang)/n2)**2)-n2*cosd(Ang))/(n1*n.sqrt(1-(n1*sind(Ang)/n2)**2)+n2*cosd(Ang)))**2
  return R

def OpticalReflectivityPlotFixedLambda(ID,l=800e-9,A1=None,A2=None,p=100,n1=1.0):
    """ Plots the optical reflectivity as a function of wavelength
        ID is the material ID
        l is the wavelength in m (default is 800nm)
        A1,A2 is the angle range (default is 0 to 90)
        p is the number of data points (default is 100)
        n1 is the index of the incident medium
    """
    if A1==None:
      Ang=n.linspace(0,90,p)
    else:
      Ang=n.linspace(A1,A2,p)
    N=OpticalIndex(ID,l)
    RS=OpticalReflectivity(ID,Ang,l,n1,pol='s')
    RP=OpticalReflectivity(ID,Ang,l,n1,pol='p')
    l=l*u['um']
    tstr="%s Reflectivity at %3.3f um" % (ID,l) 
    fig=figure()
    plot(Ang,RS,'b.-',Ang,RP,'r.-')
    ax=fig.add_subplot(111)
    ylabel('Reflectivity')
    xlabel('Incidence Angle (deg)')
    title(tstr)
    autoscale(tight=True)
    grid(True)
    legend(['s-pol','p-pol'],loc=2) 

def OpticalReflectivityPlotFixedAngle(ID,Ang=0,l1=None,l2=None,p=100,n1=1.0):
    """ Plots the optical reflectivity as a function of wavelength
        ID is the material ID
        Ang is the incidence angle in degrees (default is normal incidence)
        l1,l2 is the wavelength range (default is the database limits)
        p is the number of data points (default is 100)
        n1 is the index of the incident medium
    """
    if l1==None:
      l=n.linspace(SellmeierValidityRange[ID][0],SellmeierValidityRange[ID][1],p)
    else:
      l=n.linspace(l1,l2,p)
    N=OpticalIndex(ID,l)
    RS=OpticalReflectivity(ID,Ang,l,n1,pol='s')
    RP=OpticalReflectivity(ID,Ang,l,n1,pol='p')
    l=l*u['um']
    tstr="%s Reflectivity at %3.1f deg" % (ID,Ang) 
    fig=figure()
    plot(l*u['um'],RS,'b.-',l*u['um'],RP,'r.-')
    ax=fig.add_subplot(111)
    ylabel('Reflectivity')
    xlabel('Wavelength (um)')
    title(tstr)
    autoscale(tight=True)
    grid(True)
    legend(['s-pol','p-pol'],loc=2) 


def BrewstersAngle(ID,l=800e-9,n1=1.0):
  """ Computes Brewster's angle (angle wrt surface normal)
      ID is the material ID
      l is the wavelength in m (default is 800nm)
      n1 is the incident medium index (default is 1.0)
  """
  n2=OpticalIndex(ID,l)
  BA=atand(n2/n1)
  return BA

def OpticalIndex(ID,l):
  """ Computes the index of refraction using the Sellmeier equation 
      ID is the material ID
      l is the wavelength in m
  """
  ID=checkOpticalID(ID)
  Range=SellmeierValidityRange[ID]
  C=SellmeierCoeffs[ID]
  l=n.array(l)
  if (l<Range[0]).any(): 
    print 'Wavelength out of Sellmeier formula validity range'
    return
  elif (l>Range[1]).any():
    print 'Wavelength out of Sellmeier formula validity range'
    return
  else:
    l=l*u['um']
    if C[0]=='Type1':
      N=n.sqrt(1 + C[1]*l**2/(l**2-C[2]) + C[3]*l**2/(l**2-C[4]) + C[5]*l**2/(l**2-C[6]))
      return N 
    if C[0]=='Type11':
      N=n.sqrt(1 + C[1]*l**2/(l**2-C[2]) + C[3]*l**2/(l**2-C[4]))
      return N 
    if C[0]=='Type2':
      N=n.sqrt(1+C[1]*l**2/(l**2-C[2]**2) + C[3]*l**2/(l**2-C[4]**2) + C[5]*l**2/(l**2-C[6]**2))
      return N
    if C[0]=='Type3':
      N=n.sqrt(C[1] + C[2]*l**2/(l**2-C[3]) + C[4]*l**2/(l**2-C[5]))
      return N
    if C[0]=='Type4':
      N=n.sqrt(1+C[1]*l**2/(l**2-C[2]**2) + C[3]*l**2/(l**2-C[4]**2))
      return N
    if C[0]=='Type5':
      N=n.sqrt(C[1] + C[2]*l**2/(l**2-C[3]**2) + C[4]*l**2/(l**2-C[5]**2) + C[6]*l**2/(l**2-C[7]**2) + C[8]*l**2/(l**2-C[9]**2) + C[10]*l**2/(l**2-C[11]**2))
      return N
    if C[0]=='Type6':
      N=n.sqrt(1+C[1]*l**2/(l**2-C[2]**2))
      return N
    if C[0]=='Type7':
      N=n.sqrt(C[1] + C[2]*l**2/(l**2-C[3]**2) + C[4]*l**2/(l**2-C[5]**2))
      return N
    if C[0]=='Type8':
      N=n.sqrt(1 + C[1]*l**2/(l**2-C[2]) + C[3]*l**2/(l**2-C[4]) + C[5]*l**2/(l**2-C[6]) + C[7]*l**2/(l**2-C[8]))
      return N
    if C[0]=='Type9':
      N=n.sqrt(C[1] + C[2]/l**2 + C[3]/l**4)
      return N
    if C[0]=='Type10':
      N=n.sqrt(1 + C[1]*l**2/(l**2-C[2]**2) + C[3]*l**2/(l**2-C[4]**2) + C[5]*l**2/(l**2-C[6]**2) + C[7]*l**2/(l**2-C[8]**2))
      return N
    if C[0]=='Air':
      N = 1 + C[1]/(C[2]-l**-2) + C[3]/(C[4]-l**-2)
      return N
 
def OpticalIndexPlot(ID,l1=None,l2=None,p=100):
    """ Plots the optical index of refraction as a function of wavelength
        ID is the material ID
        p is the number of data points (default is 100)
        l1,l2 are the wavelength range (default is Sellmeier validity range
    """
    ID=checkOpticalID(ID)
    Range=SellmeierValidityRange[ID]
    if l1==None:
      l=n.linspace(Range[0],Range[1],p)
    else:
      l=n.linspace(l1,l2,p)
    N=OpticalIndex(ID,l)
    l*u['nm']
    tstr="%s Index of Refraction" % ID 
    fig=figure()
    plot(l*u['um'],N,'b.-')
    ax=fig.add_subplot(111)
    ylabel('n')
    xlabel('Wavelength (um)')
    title(tstr)
    autoscale(tight=True)
    grid(True)

        

def checkOpticalID(ID):
    """ Checks to see if you are using an alias. Returns the chemical formula"""
    try:
      return OpticalAlias[ID]
    except:
      return ID


# Material name alias'
OpticalAlias={'FS':'FusedSilica',
	'fusedSilica':'FusedSilica',
	'fs':'FusedSilica',
	'fusedsilica':'FusedSilica',
	'fused silica':'FusedSilica',
	'Fused Silica':'FusedSilica',
	'quartz':'SiO2',
	'Quartz':'SiO2',
	'Silica':'SiO2',
	'silica':'SiO2',
	'Germanium':'Ge',
	'bk7':'BK7',
        'sf10':'SF10',
        'sf11':'SF11',
        'air':'Air',
        'water':'H2O',
        'Water':'H2O',
        'Toluene':'C6H5CH3',
        'toluene':'C6H5CH3',
        'Calcite':'CaCO3',
        'calcite':'CaCO3',
	'CalciumFlouride':'CaF2',
	'calciumflouride':'CaF2',
	'Diamond':'C*',
	'diamond':'C*',
	'Sapphire':'Al2O3',
	'sapphire':'Al2O3',
	'LithiumFlouride':'LiF',
	'lithiumFlouride':'LiF',
	'Lithiumflouride':'LiF',
	'lithiumflouride':'LiF',
        'GGG':'Gd3Ga5O12',
        'ggg':'Gd3Ga5O12',
	'YAG':'Y3Al5O12',
	'yag':'Y3Al5O12',
}

# Sellmeier Coefficients
# Various equation types
# Type 11: n**2 - 1 = C1*l**2/(l**2-C2) + C3*l**2/(l**2-C4)
# Type 1:  n**2 - 1 = C1*l**2/(l**2-C2) + C3*l**2/(l**2-C4) + C5*l**2/(l**2-C6)
# Type 8:  n**2 - 1 = C1*l**2/(l**2-C2) + C3*l**2/(l**2-C4) + C5*l**2/(l**2-C6) + C7*l**2/(l**2-C8)
# Type 6:  n**2 - 1 = C1*l**2/(l**2-C2**2)
# Type 4:  n**2 - 1 = C1*l**2/(l**2-C2**2) + C3*l**2/(l**2-C4**2)
# Type 2:  n**2 - 1 = C1*l**2/(l**2-C2**2) + C3*l**2/(l**2-C4**2) + C5*l**2/(l**2-C6**2)
# Type 10: n**2 - 1 = C1*l**2/(l**2-C2**2) + C3*l**2/(l**2-C4**2) + C5*l**2/(l**2-C6**2) + C7*l**2/(l**2-C8**2)
# Type 3: n**2 = C1 + C2*l**2/(l**2-C3) + C4*l**2/(l**2-C5)
# Type 7: n**2 = C1 + C2*l**2/(l**2-C3**2) + C4*l**2/(l**2-C5**2)
# Type 5: n**2 = C1 + C2*l**2/(l**2-C3**2) + C4*l**2/(l**2-C5**2) + C6*l**2/(l**2-C7**2+ C8*l**2/(l**2-C9**2+ C10*l**2/(l**2-C11**2)
# Type 9: n**2 = C1 + C2/l**2 + C3/l**4
# Typei Air: n = 1 + C1*l**2/(C2*l**2-1) + C3*l**2/(C4*l**2-1) 
SellmeierCoeffs = {'BK7' :('Type1',1.03961212,0.0060006986,0.231792344,0.0200179144,1.01046945,103.560653),
     'FusedSilica':('Type2',0.6961663,0.0684043,0.4079426,0.1162414,0.8974794,9.896161),
     'SF10':('Type1',1.62153902,0.0122241457,0.256287842,0.0595736775,1.64447552,147.468793),
     'SF11':('Type1',1.73759695,0.013188707,0.313747346,0.0623068142,1.89878101,155.23629),
     'Ge':('Type3',9.28156,6.72880,0.44105,0.21307,3870.1),
     'KBr':('Type5',1.39408,0.79221,0.146,0.01981,0.173,0.15587,0.187,0.17673,60.61,2.06217,87.72),
     'Si':('Type2',10.6684293,0.301516485,0.003043475,1.13475115,1.54133408,1104.0),
     'ZnSe':('Type2',4.2980149,0.1920630,0.62776557,0.37878260,2.8955633,46.994595),
     'Si3N4':('Type6',2.8939,139.67e-3),
     'InAs':('Type7',11.1,0.71,2.551,2.75,45.66),
     'Air':('Air',5792105e-8,238.0185,167917e-8,57.362),
     'H2O':('Type8',5.684027565e-1,5.101829712e-3,1.726177391e-1,1.821153936e-2,2.086189578e-2,2.620722293e-2,1.130748688e-1,1.069792721e1), #at 20 degrees C
     'C6H5CH3':('Type9',2.175132,20.4682e-3,7.31e-4),
     'SiO2':('Type3',1.28604141,1.07044083,1.00585997e-2,1.10202242,100), #extraordinary values
     'CaCO3':('Type3',1.73358749,0.96464345,1.94325203e-2,1.82831454,120), #ordinary values
     'CaF2':('Type2',0.5675888,0.050263605,0.4710914,0.1003909,3.8484723,34.649040),
     'C*':('Type4',4.3356,0.1060,0.3306,0.1750),
     'Al2O3':('Type2',1.4313493,0.0726631,0.65054713,0.1193242,5.3414021,18.028251),
     'LiF':('Type4',0.92549,0.07376,6.96747,32.79),
     'KF':('Type7',1.55083,0.29162,0.126,3.60001,51.55),
     'PbF2':('Type10',0.66959342,0.00034911,1.3086319,0.17144455,0.01670641,0.28125513,2007.8865,796.67469),
     'SrF2':('Type2',0.67805894,0.05628989,0.37140533,0.10801027,3.8484723,34.649040),
     'Y3Al5O12':('Type11',2.282,0.01185,3.27644,282.734),
     'Gd3Ga5O12':('Type2',1.7727,0.1567,0.9767,0.01375,4.9668,22.715),
}



# Sellmeier formula validity range (lambda low, lambda high)
SellmeierValidityRange = {'BK7':(300e-9,2.5e-6),
     'FusedSilica':(210e-9,3.71e-6),
     'SF10':(380e-9,2.5e-6),
     'SF11':(375e-9,2.5e-6),
     'Ge':(2e-6,12e-6),
     'C':(225e-9,100-6),   
     'KBr':(0.2e-6,40e-6),
     'Si':(1.36e-6,11e-6),
     'ZnSe':(0.55e-6,18e-6),
     'Si3N4':(0.207e-6,1.24e-6),
     'InAs':(3.7e-6,31.3e-6),
     'Air':(0.23e-6,1.69e-6),
     'H2O':(0.18e-6,1.13e-6),
     'C6H5CH3':(0.3e-6,2.5e-6),
     'SiO2':(0.198e-6,2.0531e-6),
     'CaCO3':(0.204e-6,2.172e-6),
     'CaF2':(0.23e-6,9.7e-6),
     'C*':(0.225e-6,100e-6),
     'Al2O3':(0.2e-6,5.5e-6),
     'LiF':(0.1e-6,11e-6),
     'KF':(0.15e-6,22e-6),
     'PbF2':(0.3e-6,11.9e-6),
     'SrF2':(0.21e-6,11.5e-6),
     'Y3Al5O12':(0.4e-6,5.5e-6),
     'Gd3Ga5O12':(0.35e-6,8e-6),
}

 
        
