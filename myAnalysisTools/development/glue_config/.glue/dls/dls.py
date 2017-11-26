from glue.viewers.custom.qt import CustomViewer

from glue.core.subset import RoiSubsetState

from matplotlib.colors import LogNorm
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.lines import Line2D
import numpy as np
from lib.analysis_library import vectorized_binned_statistic_dd

def t_func(r):
	temp = array([pickle.loads(i) for i in r])
	
	x=temp[:,0]
	y=temp[:,1]
	#if len(x)<len(y): y=y[:-1]
	#elif len(x)>len(y): x=x[:-1]
	#elif (len(x)==0): return nan

	#IPython.embed()

	myLength=len(y)
	threshold=0.05
	ySortedIndex = argsort(y)
	y = y[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	x = x[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	
	xSortedIndex = argsort(x)
	y = y[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	x = x[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]

	#print(str(len(x))+", "+str(len(y))+", "+str(len(r)))
	#print(str(len(x))+", "+str(len(y)))
	
	myCov = cov(x,y)
	simple_slope = myCov[0,1]/myCov[0,0]
	
	non_serialized_result = array([mean(y*1.0/x),mean(y)/mean(1.0*x),simple_slope])
	#serialized_result = pickle.dumps(non_serialized_result)
	dict_result = {'shot_by_shot_median':median(y*1.0/x),'shot_by_shot':mean(y*1.0/x),'median':median(y)/median(1.0*x),'averaged':mean(y)/mean(1.0*x),'simple_slope':simple_slope}

	#IPython.embed()
	return dict_result

class dls_viewer(CustomViewer):
	name = 'dls_viewer'
	x = 'att(/GMD)'	#this switch swaps the x and y axes.
	y = 'att(/acqiris2)'	#need to figure out how to make this programable.  Replaced x and y with pop and viv, then need to rename in glue.
	bins = (10, 100)
	#more_bins =(-10,10)	#this adds bins 
	z = 'att(/atm_corrected_timing)'
	ephoton = 'att(/ebeam/photon_energy)'
	hitrate = False
	color = ['Reds', 'Purples']
	#hit = 'att(shot_made)'

	def make_selector(self, roi, x, y):

		state = RoiSubsetState()
		state.roi = roi
		state.xatt = x.id
		state.yatt = y.id

		return state

	def plot_data(self, axes, x, y,z, color, style,bins):
		myHistogramW=np.histogram(z,bins=np.arange(326.9,347.1,0.075),weights = np.nan_to_num(y*x*1.0/(x**2+1e-12)))
		myHistogram=np.histogram(z,bins=np.arange(326.9,347.1,0.075))
		the_dls= myHistogramW[0]/myHistogram[0]
		the_dls -= np.mean(the_dls)
		the_dls/=np.std(the_dls)
		axes.plot(myHistogram[1][:-1],the_dls[::-1],marker='o',linewidth=0)


	def plot_subset(self, axes, x, y,z, style,bins):
		myHistogramW=np.histogram(z,bins=np.arange(326.9,347.1,0.075),weights = np.nan_to_num(y*x*1.0/(x**2+1e-12)))
		myHistogram=np.histogram(z,bins=np.arange(326.9,347.1,0.075))
		the_dls= myHistogramW[0]/myHistogram[0]
		the_dls -= np.mean(the_dls)
		the_dls/=np.std(the_dls)
		axes.plot(myHistogram[1][:-1],the_dls[::-1],mec=style.color,mfc=style.color,marker='o',linewidth=0)

	def setup(self, axes):
		temp =0 
		axes.set_ylim(-1, 1)
		axes.set_xlim(326, 347)
		#axes.set_aspect('equal', adjustable='datalim')
