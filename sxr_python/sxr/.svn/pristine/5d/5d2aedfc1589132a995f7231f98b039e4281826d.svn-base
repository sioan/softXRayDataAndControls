from string import punctuation
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy import *
from scipy.optimize import curve_fit
import math
import random

def main():
	'''
	This program needs to take a text file and turn it into two
	lists and plot the lists against each other and fit a fifth
	order polynomial. So this main() will call a function that
	opens the file, a function that reads the file and separates
	it into 2 lists, a function that plots the two lists, and a
	function that fits a curve and then plots it with the plotting
	function.
	'''

	'''
	for n in range(3):	
		for number in range(0, 1000, 10):
			varName = "poss%d" % n
			varname = []
			fil = '/Users/RachelFlaherman/Desktop/SLAC/just_data15.txt'
			ar = array1(fil, number)
			fit = fitCoef(ar)
			print "here's the fit"
			print fit
			fitLst = fitList(ar, fit) #newly uncommented
			#plot = plot2things(ar, fitLst)#newly uncommented
			print "FIT:"
			print fit
			mirrorPos = get_optimal_mirror_position(fitLst)
			print "THIS IS THE END OF THE PROGRAM:"
		
			print mirrorPos
			miPo = abs(-0.4165 - mirrorPos)
			poss.append(miPo)
	plt.plot(range(0,10000,10), poss0, "x", range(0,10000,10), "o", range(0,10000,10), "rx")
	plt.show()
	'''
	#want to plot len(flts) vs poss[n]-0.4165
	fil = '/Users/RachelFlaherman/Desktop/SLAC/just_data15.txt'
	ar = array1(fil, number)
	print "SIZE"
	print ar.size
	fit = fitCoef(ar)
	print "here's the fit"
	print fit
	fitLst = fitList(ar, fit) #newly uncommented
	plot = plot2things(ar, fitLst)#newly uncommented
	print "FIT:"
	print fit
	mirrorPos = get_optimal_mirror_position(fitLst)
	print "THIS IS THE END OF THE PROGRAM:"
	
	print mirrorPos

	
def array1(filename, numba):
	'''
	input: filename(string)
	output: array (2,:) - sharpness value (from working_algorithm) is ar(0,:) and   mirror position (M1) is ar(1,:)

	'''
	numba = 1 ###
	text = open(filename, "r")
	for lin in text:
		print type(lin)
		print "OK!"
		spl_lin = lin.split(',')
	print "HERE WE ARE"
	print spl_lin
	print type(spl_lin)
	print len(spl_lin) #this is a problem. It is an odd number.
	spl_lin = spl_lin[1:]
	flts = []
	print "ok"
	print spl_lin[0]
	print "ok"
	n = 2
	indxs = []
	half = (len(spl_lin))/2
	spl_lin = np.array(spl_lin)
	print type(spl_lin)
	print spl_lin.size
	print spl_lin.shape

	resVals = spl_lin[0:half]
	mirPos = spl_lin[half:]
	print type(resVals)
	print resVals.size
	print resVals.shape
	while n < (len(spl_lin))/2:
		nm = float(spl_lin[n])
		flts.append(nm)
		indxs.append(n)
		n += numba
		y = random.randrange(0,3)
		n +=y

	for n in indxs:
		flts.append(float(mirPos[n]))
	'''
	for num in spl_lin:
		nm = float(num)
		flts.append(nm)
		#print "working"
	'''
	print "FLOATS:"
	print flts
	res = []
	
	locs = []
	indx = 0
	while flts[indx] > 0.0:
		res.append(flts[indx])
		indx +=1
	for n in range(indx, len(flts)):
		locs.append(flts[n])

	ar = np.array([res, locs])
	return ar
		

def fitCoef(anArray):
	'''
	argument: (2,:) array where array(0,:) is the sharpness value and array(1,:) is the mirror position.
	returns: a coefficient matrix for a 5th order polynomial	'''

	#return np.polyfit(anArray[1,:], anArray[0,:], 3, full = True) # figure out how to index and interpret this
	def gaus(x, a, x0, sigma):
    		return a*exp(-(x-x0)**2/(2*sigma**2))

	p = math.pi

	def lorentzian(x, g, x0):
		return g*1/((2*p)*((x-x0)**2+(g/2)**2))

	return np.polyfit(anArray[1,:], anArray[0,:], 5)
	#popt, pcov = sp.optimize.curve_fit(lorentzian, anArray[1,:], anArray[0,:])
	#print "THIS IS POPT:", popt
	#return popt

def fitList(theArray, coefficients):
	print "starting"
	print coefficients
	p = math.pi
	print p
	locs = theArray[1,:]
	ordered = sort(locs)
	mn = ordered[0]
	mx = ordered[-1]
	
	xs = []
	ys = []
	while mn < mx:
		x = mn
		xs.append(mn)
		y = coefficients[0]*x**5 + coefficients[1]*x**4 + coefficients[2]*x**3 + coefficients[3]*x**2 +coefficients[4]*x +coefficients[5]
		#y = (coefficients[0])/((2*p)*((x-coefficients[1])**2+((coefficients[0])/2)**2))
		ys.append(y)
		mn += 0.0001
		
	ar = np.array([ys, xs])
	print ar
	return ar
		


def plot2things(theData, theFit):
	print 'data type:',
	print type(theData)
	print "fit type"
	print type(theFit)
	print len(theFit[1,:])
	print len(theFit[0,:])
	print theFit[0,:][:20]
	plt.plot(theData[1,:], theData[0,:], "o", theFit[1,:], theFit[0,:], lw = 5)
	plt.show()

def get_optimal_mirror_position(theFit):
	print len(theFit[0,:]) # make this its own function 
	la = np.argmax(theFit[0,:])
	print la
	mirrorVal = theFit[1,:][la]
	print "Mirror Value:" , mirrorVal
	return mirrorVal

main()
