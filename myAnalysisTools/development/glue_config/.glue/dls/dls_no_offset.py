from glue.viewers.custom.qt import CustomViewer

from glue.core.subset import RoiSubsetState

from matplotlib.colors import LogNorm
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.lines import Line2D
import numpy as np
from lib.analysis_library import vectorized_binned_statistic_dd
from scipy.stats import binned_statistic
import pickle
import sys

def t_func(r,median_truncation):
	try:
		temp = np.array([pickle.loads(i) for i in r])
	
		x=temp[:,0]
		y=temp[:,1]


		myLength=len(y)
		threshold=median_truncation/400.0
		ySortedIndex = np.argsort(y)
		y = y[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
		x = x[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	
		xSortedIndex = np.argsort(x)
		y = y[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
		x = x[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]

	
		myCov = np.cov(x,y)
		simple_slope = myCov[0,1]/myCov[0,0]
	
		non_serialized_result = np.array([np.mean(y*1.0/x),np.mean(y)/np.mean(1.0*x),simple_slope])
		#serialized_result = pickle.dumps(non_serialized_result)
		dict_result = {'shot_by_shot_median':np.median(y*1.0/x),'shot_by_shot_average':np.mean(y*1.0/x),'median':np.median(y)/np.median(1.0*x),'average':np.mean(y)/np.mean(1.0*x),'slope':simple_slope}
	except:
		dict_result = {'shot_by_shot_median':-9999.0,'shot_by_shot_average':-9999.0,'median':-9999.0,'average':-9999.0,'slope':-9999.0}

	return dict_result

def normalize_statistic(y):

	x = y - np.mean(y)
	x/=np.std(x)

	return x

def normalize_statistic(y):

	x = y - np.mean(y)
	x/=np.std(x)

	return x

class dls_viewer(CustomViewer):
	name = 'dls_viewer'
	#x = 'att(/GMD)'	
	#y = 'att(/acqiris2)'
	#z = 'att(/atm_corrected_timing)'

	x = 'att'	#using above for quicker development
	y = 'att'	#using above for quicker development
	z = 'att'

	bin_start = 326.9
	bin_end = 347.1
	n_bins = 150
	median_truncation = (1,100,1)
	#more_bins =(-10,10)	#this adds bins 
	apply_settings = False
	normalized = True
	auto_scale = True
	auto_bin = False
	statistic_type =["average","median","shot_by_shot_average","shot_by_shot_median", "slope"]
	reverse_axis={"normal":1,"reversed":-1}

	#hit = 'att(shot_made)'

	def __init__(self, widget_instance):
		if(3==sys.version_info[0]):
			super().__init__(widget_instance)
		else:
			CustomViewer.__init__(self,widget_instance)
		
		self.myStats = {}
		self.to_display = 0
		self.last_hex_x_id = 0
		self.last_hex_y_id = 0
		self.last_bin_hash_id = 0
		self.last_median_truncation = 0 
		self.last_apply_settings = False
		self.bin_start = 0
		self.bin_end = 1

	def plot_data(self, axes, x, y,z, style,auto_bin):
		temp =0

	def plot_subset(self, axes, x, y,z, style,bin_start, bin_end,n_bins,median_truncation, statistic_type,normalized,apply_settings,reverse_axis,auto_scale,auto_bin):



		if(auto_bin):
			bin_end=max(z)
			bin_start = min(z)
		else:
			pass
		
		tEdges = np.arange(bin_start,bin_end,(bin_end-bin_start)/n_bins)

		#identify the subset coming in
		my_hex_style_id = str(hex(id(style)))

		#hash the values to prevent frivolous recalculation 
		my_hex_x_id = str(hash(frozenset(x)))
		my_hex_y_id = str(hash(frozenset(y)))
		bin_hash_id = str(hash(frozenset(tEdges)))
		

		bin_hash_id = str(hash(frozenset(tEdges)))

		if (int ==type(self.to_display)):
			self.to_display = np.zeros(len(tEdges)-1)
			self.tEdges = tEdges
			self.myStats[statistic_type] = np.ones(len(tEdges)-1)
			


		myValues = np.array([x,y]).transpose()
		def t_func_wrapper(r):
			return t_func(r,median_truncation)

		needs_recalculation = (self.last_median_truncation!=median_truncation)
		needs_recalculation = needs_recalculation or (self.last_bin_hash_id!=bin_hash_id)
		needs_recalculation = needs_recalculation and (self.last_apply_settings !=apply_settings)

		if(len(z)!=0 and apply_settings and needs_recalculation):
			print("recalculating")
			self.tEdges = tEdges
			self.myStats = vectorized_binned_statistic_dd(z,myValues,bins=[tEdges],statistic=t_func_wrapper)#square brackets around tEdges is important
	

		else:
			pass

		if(normalized):
			self.to_display = normalize_statistic(self.myStats[statistic_type])
		else:	
			self.to_display = self.myStats[statistic_type]

		axes.plot(self.tEdges[:-1][::reverse_axis],self.to_display,c=style.color,marker='.',linewidth=2)
		axes.set_xlim(min(tEdges),max(tEdges))
		
		if(auto_scale):
			myCenter = (min(self.to_display)+max(self.to_display))/2.0
			myWindow = (-min(self.to_display)+max(self.to_display))
			axes.set_ylim(myCenter-myWindow/(2-0.2),myCenter+myWindow/(2-0.2))

		else: pass
			

		#update last values to current values
		self.last_hex_x_id = my_hex_x_id
		self.last_hex_y_id = my_hex_y_id
		self.last_bin_hash_id = bin_hash_id
		self.last_median_truncation = median_truncation
		self.last_apply_settings =apply_settings

	def setup(self, axes):
		temp =0 
		axes.set_ylim(-1, 1)
		axes.set_xlim(326, 347)
		#axes.set_aspect('equal', adjustable='datalim')
