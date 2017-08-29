#This program will collect the raw data, run it thru my algorithm, and store two lists: the sharpness values and the motor positions. I will run this program several times to collect all the data points.

# This will also be a good exercise in writing functions for data collection

import working_algorithm
import os #new
import matplotlib.pyplot as plt
import numpy as np
#import scipy as sp
#from scipy import *
#from scipy.optimize import curve_fit
import psana


def main():

	#ds = psana.DataSource("exp=SXR/sxri0214:run=139:idx")
	#src = psana.Source("DetInfo(SxrBeamline.0:Opal1000.1)")
	#epics = ds.env().epicsStore()
	res_vs_pos = get_sharpness_vs_position()
	pruned = get_rid_of_outliers(res_vs_pos)
	save_file(pruned)


def get_sharpness_vs_position():
	'''
	This is one function because I could not figure out how to get it to work as separate functions
	'''
	ds = psana.DataSource("exp=SXR/sxri0214:run=139:idx")
	src = psana.Source("DetInfo(SxrBeamline.0:Opal1000.1)")
	epics = ds.env().epicsStore()
	m1_positions = []
	sharp_vals = []
	print ds.runs()
	for run in ds.runs():#new #maybe there is only one run? It prints in a
   	 #way I don't understand
    		print run
    		times = run.times()
    		#inxs = []
    		#indx = 0
    		for tm in times[0:120000]:
			print tm
        		evt = run.event(tm)
        		camera = evt.get(psana.Camera.FrameV1,src)
        		projection = np.sum(camera.data16(),axis=1)
        		a_val = working_algorithm.main(projection)
			sharp_vals.append(a_val)
			#if a_val < 100:
        		#	inxs.append(indx)
			position = epics.value('SXR:MON:MMS:05.RBV')
			m1_positions.append(position)
			#indx += 1
	
	ar = np.array([sharp_vals, m1_positions])
	print ar
	return ar

				


def get_rid_of_outliers(data_array):


	'''
	This function gets rid of the values near 80
	'''

	print data_array
	res = data_array[0,:]
	pos = data_array[1,:]
	indxs = []
	new_alg = []
	new_locs = []
	for n in range(len(res)):
		if res[n] < 100:
			indxs.append(n)
	for n in range(len(res)):
		if n not in indxs:
			new_alg.append(res[n])
			new_locs.append(pos[n])
	#new_alg = []
	#new_locs = []

	if len(new_alg) != len(new_locs):
		print "Something's wrong!"
		print len(new_alg)
		print len(new_locs)

	ar = np.array([new_alg, new_locs])
	
	return ar


def save_file(array):
	'''
	This function saves a file with two lists. It should perhaps convert the lists to strings so I can save the lists as text.
	'''
	print "ARRAY SHAPE"
	print array.shape
	str1 = ' '	
	for val in array[0,:]:
		str1+=',' + str(val)

	str2 = ' '
	for val in array[1,:]:
		str2 += ',' + str(val)

	#strng = ' '
	#for lst in array: #there shld be two
	#	strng += "Start"
	#	for n in strng:
	#		n = str(n)
	#		strng += n	
	strng = str1 + "start" + str2	
	print "PRINTING STRING:"	
	print strng
	la = 0
	nam = "just_data0"
	while os.path.exists(nam+".txt"):
		la +=1
		nam = "just_data%d" %la
	straw = nam + ".txt"
	fil = open(straw, "w")
	fil.write(strng)
	fil.close()
'''
####
def get_projections(ds, src):

	#This function takes (???) as input and outputs a list of the
	#projection values (so a list of lists, right?)
	

	projs = []
	for run in ds.runs():
		times = run.times()

		for tm in times[0:120000:100]:
			evt = run.event(tm)
        		camera = evt.get(psana.Camera.FrameV1,src)
			projection = np.sum(camera.data16(),axis=1)
			projs.append(projection)

	return projs



def get_mirror_positions(ds, src, epics):
	
	#This function takes (???) as input and returns a list of mirror positions
	

	positions = []
	print "GOING"
	#print ds.runs()
	for run in ds.runs():
		print run
		times =run.times()
		print "STILL GOING"
		for tm in times[0:120000:10]: # put this in main or something
			#so I don't have to repeat myself
			print tm
			position = epics.value('SXR:MON:MMS:05.RBV')
			print position
			positions.append(position)
	return positions


def algorithm(projs):
	
	#This function takes list of lists as input and returns a list of floats
	
	vals = []
	for each in projs:
		sharpness_val = working_algorithm.main(each)
		vals.append(sharpness_val)
	return vals

####
'''



main()
