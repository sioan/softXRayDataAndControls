from pylab import *
import IPython
import pickle

from lib._binned_statistic import binned_statistic_dd

def errorWeightedSmoothing(myData,myError,myWidth,myOrder):
	myWeights = savgol_coeffs(myWidth,myOrder,0)
	
	
	mySignal = convolve(myData/myError**2,myWeights,mode='same')

	mySignal = mySignal / convolve(1.0/myError**2,myWeights,mode='same')

	myErrors = (1.0/convolve(1.0/myError**2,myWeights,mode='same'))**0.5/sum(myWeights)**0.5

	return mySignal,myErrors

def vectorized_binned_statistic_dd(sample, values, statistic='mean',bins=10, range=None, expand_binnumbers=False):
	arg_axes = array([pickle.dumps(i) for i in values])

	results = binned_statistic_dd(sample,values = arg_axes,bins=bins,statistic=statistic)
	my_dict_of_arrays ={}

	for this_key in results[0].item(0).keys():
		#my_dict_of_arrays[this_key] = array([[array(j[this_key]) for j in i] for i in results[0]])	#only two dimensions
		my_dict_of_arrays[this_key] = zeros(results[0].shape)

	for i in my_dict_of_arrays:
		for j in arange(my_dict_of_arrays[i].size):
			my_dict_of_arrays[i].itemset(j,results[0].item(j)[i])

	#results[0]=my_dict_of_arrays
	#to do
	return my_dict_of_arrays

def removeNans(myDict):
	notNanMask = True
	for i in myDict:		
		notNanMask *= array([not math.isnan(j) for j in myDict[i]])
	
	for i in myDict:		
		myDict[i] = myDict[i][notNanMask]

	return myDict

def battery_of_histograms(data_dict,instruction_dict):

	instruction_dict = {}	#this needs to go somewhere else
	instruction_dict['counts']	= ones(len(data_dict['any_data']))
	xAxes = data_dict['atm_corrected_timing']
	
	myDict = {}
	#no way to get median-filtering on bin by bin basis
	for i in instruction_dict:
		myDict[i]['counts'] = histogram(xAxes,weights=ones(len(data_dict['normalized_intensity'])))
		myDict[i]['acqiris2'] = histogram(xAxes,weights=data_dict['acqiris2'])
		myDict[i]['GMD'] = histogram(xAxes,weights=data_dict['GMD'])
		myDict[i]['normalized_intensity'] = histogram(xAxes,weights=data_dict['normalized_intensity'])
		x = data_dict['GMD']		
		y = data_dict['acqiris2']
		myDict[i]['covxy']=histogram(data_dict[xAxes],weights=x*y)

		#https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.stats.binned_statistic.html		
		#windspeed = 8 * np.random.rand(500)
		#boatspeed = .3 * windspeed**.5 + .2 * np.random.rand(500)
		#bin_means, bin_edges, binnumber = stats.binned_statistic(windspeed,boatspeed, statistic='median', bins=[1,2,3,4,5,6,7])
		scipy.stats.binned_statistic(xAxes,passable_dict_or_array,func=median_filtered_cov) #can this take a dict for values?

def basic_histogram(myDict,keyToAverage,xAxis,bins,isLog):#fast for debugging

	myDataDictionary = {}

	if(isLog):
		myDataDictionary['x'] = bins[:-1]
		myDataDictionary['counts'] = histogram(myDict[xAxis],bins)[0]

		myDataDictionary['yMean'] = exp(histogram(myDict[xAxis],bins,weights = log(myDict[keyToAverage]))[0]/myDataDictionary['counts'])
		myDataDictionary['y2ndMoment'] = histogram(myDict[xAxis],bins,weights = log(myDict[keyToAverage])**2)[0]/myDataDictionary['counts']
		myDataDictionary['standardDeviation'] = exp((myDataDictionary['y2ndMoment']-myDataDictionary['yMean'])**0.5)

		
	else:
		myDataDictionary['x'] = bins[:-1]
		myDataDictionary['counts'] = histogram(myDict[xAxis],bins)[0]

		myDataDictionary['yMean'] = histogram(myDict[xAxis],bins,weights = myDict[keyToAverage])[0]/myDataDictionary['counts']
		myDataDictionary['y2ndMoment'] = histogram(myDict[xAxis],bins,weights = myDict[keyToAverage]**2)[0]/myDataDictionary['counts']
		myDataDictionary['standardDeviation'] = (myDataDictionary['y2ndMoment']-myDataDictionary['yMean']**2)**0.5

	del myDataDictionary['y2ndMoment']

	myDataDictionary = removeNans(myDataDictionary)

	return myDataDictionary

def median_sorted_filter(data_dict, filter_criterion):
	
	filtered_data = {}
	myLength = len(data_dict[data_dict.keys()[0]])
	for j in data_dict:
		sorted_index = argsort(data_dict)
		threshold = filter_criterion
		filtered_data[j] = data_dict[j][sorted_index][int(threshold*myLength):int(myLength*(1-1*threshold))]
		myLength = len(filtered_data[j])

	return filtered_data

def apply_filter(data_dict,filter_mask):
	myDict = {}
	#IPython.embed()
	for i in data_dict:
		try:
			myDict[i] = data_dict[i][filter_mask]
		except IndexError:
			pass
	
	return myDict
