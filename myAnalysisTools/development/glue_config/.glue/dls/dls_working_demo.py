from glue.viewers.custom.qt import CustomViewer

from glue.core.subset import RoiSubsetState

from matplotlib.colors import LogNorm
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.lines import Line2D
import numpy as np
from lib.analysis_library import vectorized_binned_statistic_dd
from scipy.stats import binned_statistic
import pickle

def t_func(r,median_truncation):
	temp = np.array([pickle.loads(i) for i in r])
	
	x=temp[:,0]
	y=temp[:,1]
	#if len(x)<len(y): y=y[:-1]
	#elif len(x)>len(y): x=x[:-1]
	#elif (len(x)==0): return nan

	#IPython.embed()

	myLength=len(y)
	threshold=median_truncation/400.0
	ySortedIndex = np.argsort(y)
	y = y[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	x = x[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	
	xSortedIndex = np.argsort(x)
	y = y[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	x = x[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]

	#print(str(len(x))+", "+str(len(y))+", "+str(len(r)))
	#print(str(len(x))+", "+str(len(y)))
	
	myCov = np.cov(x,y)
	simple_slope = myCov[0,1]/myCov[0,0]
	
	non_serialized_result = np.array([np.mean(y*1.0/x),np.mean(y)/np.mean(1.0*x),simple_slope])
	#serialized_result = pickle.dumps(non_serialized_result)
	dict_result = {'shot_by_shot_median':np.median(y*1.0/x),'shot_by_shot':np.mean(y*1.0/x),'median':np.median(y)/np.median(1.0*x),'averaged':np.mean(y)/np.mean(1.0*x),'simple_slope':simple_slope}

	#IPython.embed()
	return dict_result

class dls_viewer(CustomViewer):
	name = 'dls_viewer'
	#x = 'att(/GMD)'	#this switch swaps the x and y axes.
	#y = 'att(/acqiris2)'	#need to figure out how to make this programable.  Replaced x and y with pop and viv, then need to rename in glue.
	x = 'att'
	y = 'att'
	bins = (25,300)
	median_truncation = (1,100)
	#more_bins =(-10,10)	#this adds bins 
	z = 'att(/atm_corrected_timing)'
	ephoton = 'att(/ebeam/photon_energy)'
	shot_by_shot = False
	the_slope = False
	modulation_spectroscopy = False
	color = ['Reds', 'Purples']
	#hit = 'att(shot_made)'

	def make_selector(self, roi, x, y):

		state = RoiSubsetState()
		state.roi = roi
		state.xatt = x.id
		state.yatt = y.id

		return state

	def plot_data(self, axes, x, y,z, color, style,bins):
		#myHistogramW=np.histogram(z,bins=np.arange(326.9,347.1,0.075),weights = np.nan_to_num(y*x*1.0/(x**2+1e-12)))
		#myHistogram=np.histogram(z,bins=np.arange(326.9,347.1,0.075))
		#the_dls= myHistogramW[0]/myHistogram[0]
		#the_dls -= np.mean(the_dls)
		#the_dls/=np.std(the_dls)
		#axes.plot(myHistogram[1][:-1],the_dls[::-1],marker='o',linewidth=0)
		temp = 0


	def plot_subset(self, axes, x, y,z, style,bins,shot_by_shot,the_slope,median_truncation,modulation_spectroscopy):
		binSize = (347.1-326.9)/bins
		tEdges = np.arange(326.9,347.1,binSize)
		myHistogramW=np.histogram(z,bins=tEdges,weights = np.nan_to_num(y*x*1.0/(x**2+1e-12)))
		myHistogram=np.histogram(z,bins=tEdges)
		the_dls= myHistogramW[0]/myHistogram[0]
		the_dls -= np.mean(the_dls)
		the_dls/=np.std(the_dls)
		#axes.plot(myHistogram[1][:-1],the_dls[::-1],mec=style.color,mfc=style.color,marker='o',linewidth=0)

		myValues = np.array([x,y]).transpose()
		if(the_slope):
			myStatistic = 'simple_slope'
		elif(shot_by_shot and not the_slope):
			myStatistic = 'shot_by_shot'
		elif(not shot_by_shot and not the_slope):
			myStatistic = 'averaged'

		def t_func_wrapper(r):
			return t_func(r,median_truncation)

		if(len(z)!=0):
			myStats = vectorized_binned_statistic_dd(z,myValues,bins=[tEdges],statistic=t_func_wrapper)	#square brackets around tEdges is important
			myStats[myStatistic]-=np.mean(myStats[myStatistic])
			myStats[myStatistic]/=np.std(myStats[myStatistic])
			if (not modulation_spectroscopy):
				axes.plot(tEdges[:-1],myStats[myStatistic][::-1],c=style.color,marker='.',linewidth=2)
			else:
				axes.plot(tEdges[:-1],np.cumsum(myStats['simple_slope'][::-1]/myStats['averaged'][::-1]),c=style.color,marker='.',linewidth=2)

	def setup(self, axes):
		temp =0 
		axes.set_ylim(-1, 1)
		axes.set_xlim(326, 347)
		#axes.set_aspect('equal', adjustable='datalim')
