import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt


def main(data):#data is a 1-D array
	'''
	assume incoming data is a 1-D array for each monochrometer position. 
	this function will sort the data for each monochrometer
	position. It will not compare positions. I will do that separately.
	''' 
	
	medFilt = med_filter(data)
	deriv1 = deriv(medFilt)
	sort_deriv = sortDeriv(deriv1)
	top_25 = pruned(sort_deriv)
	avg = averag(top_25)
	return avg
 

def med_filter(data):

    return medfilt(data)

def deriv(la):

    new = []
    
    lo = np.gradient(la)
    for loo in lo:
        new.append(abs(loo))

    return new
    
def sortDeriv(deriv):
    
    la = sorted(deriv)
    la.reverse()
    return la
        
def pruned(sorted_deriv):
    tops = []
    leng = len(sorted_deriv)
    #    leng = 0.25*leng
    leng = 0.25*leng
    leng = int(leng)
    lst = range(leng)
    
    for n in lst:
        tops.append(sorted_deriv[n])
    return tops
        
def averag(lst):
    return np.mean(lst)
        


