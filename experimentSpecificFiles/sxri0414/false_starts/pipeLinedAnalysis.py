from pylab import *
import h5py
import os
import sys
import IPython
from hdf5_to_dict import hdf5_to_dict
from filterMasks import filterMasks
from scipy.optimize import curve_fit
from plotPackage import errorWeightedSmoothing
from scipy.interpolate import interp1d
#ion()	#works with python. for ipython need to use %matplotlib from shell
#matplotlib.pyplot.switch_backend('QT4Agg')# does'nt work 

import analysisPipeLine
import analysisPipeLineMonitor 

#####################################
####Setting up analysis functions####
#####################################


#layer 1
def loadData(experimentRunName):
	experimentRunName = "sxri0414run81"
	myFile = experimentRunName+".h5"
	myHdf5Object = h5py.File("smallHdf5Data/"+myFile)
	myDataDict = hdf5_to_dict(myHdf5Object)

#layer 1
def loadMask(experimentRunName):
	myMask =  filterMasks.__dict__[experimentRunName](myHdf5Object)
	#currently static.  needs to be dynamic so users can change filtering and and see how results change.
	#or this could be an interactive approach
	#make socket connection with glue

#layer 2. preparing the delay stage axis
def convert_delay_stage_to_time(un_binned_data,config):
	myDict["time_axis"] = 2/.3*(myDict['delayStage']-myOffset)+timeToolSign*myDict['TSS_OPAL']['pixelTime']/1000.0

#layer 3. Normalization of transmitted data.  3 different ways (compare. divide, line, polynomial) and then can choose energy (1/wavelength) dependent calibration. increases number of ways by two.  Then choosing the energy binning value.
#make one function with if statements? or N

def normalize_and_bin(unbinnedData,method) #methods described above
	if (method=="poly_fit"):
		#fitting. (is this event accurate given the plots that have energy dependence?)
	if (method =="energy_calibrated"):
		#some three column I,I0,energy covariance matrix approach. details are vague. not like binned piece wise line fitting as done in delayTraceMaker.py.  			#Actually, I do need the piece wise cause I know it's not linear.
	if (method == "brute_division"):
		basicHistogram(myDict,keyToAverage,correctedKeyToBin,bins=arange(-5.0,26,.1),isLog=logFlag)	#need to abstract out fixed values

#layer 4. wiener filtering
def wiener_filter(signal,bandwidth_physical_limitation,noise):
	#
	#return filtered data convolved with noise
	#bandwidth_physical_limitation is for the hat matrix.


#####################################
####Setting up analysis pipelines####
#####################################

collectionOfAnalysisPipelines = {'myFirstPipeLine':analysisPipeLine.makeAnalysisPipeLineInstance('myFirstPipeLine')}
collectionOfAnalysisPipelines['my2ndPipeLine']=analysisPipeLine.makeAnalysisPipeLineInstance('my2ndPipeLine')

#collectionOfAnalysisPipelines['myFirstPipeLine'] = analysisPipeLine.makeAnalysisPipeLineInstance('myFirstPipeLine')

#append_analysis_step(self,analysis_function,analysis_alias):
collectionOfAnalysisPipelines['myFirstPipeLine'].append_analysis_step(f,"a_plus_b")
collectionOfAnalysisPipelines['myFirstPipeLine'].append_analysis_step(g,"square")
collectionOfAnalysisPipelines['myFirstPipeLine'].append_analysis_step(h,"divide_by_ten")


collectionOfAnalysisPipelines['my2ndPipeLine'].append_analysis_step(f,"a_plus_b")
collectionOfAnalysisPipelines['my2ndPipeLine'].append_analysis_step(g,"square")
collectionOfAnalysisPipelines['my2ndPipeLine'].append_analysis_step(h,"divide_by_ten")

print collectionOfAnalysisPipelines['myFirstPipeLine'].collectionOfAnalysisResults.keys()
print collectionOfAnalysisPipelines['myFirstPipeLine'].collectionOfAnalysisResults

collectionOfAnalysisPipelines['myFirstPipeLine'].remove_analysis_step("square")
print collectionOfAnalysisPipelines['myFirstPipeLine'].collectionOfAnalysisResults

#####################################
####Executing analysis pipelines#####
#####################################
collectionOfAnalysisPipelines['myFirstPipeLine'].execute_analysis([-1.0**arange(10),10*ones(10)])
collectionOfAnalysisPipelines['my2ndPipeLine'].execute_analysis([-1.0**(arange(10)),4*arange(10)])

print collectionOfAnalysisPipelines['myFirstPipeLine'].collectionOfAnalysisResults
print collectionOfAnalysisPipelines['my2ndPipeLine'].collectionOfAnalysisResults

myAnalysisMatplotlibMonitor = analysisPipeLineMonitor.matplotlibMonitor()
myAnalysisMatplotlibMonitor.analysisMatplotlibMonitor(collectionOfAnalysisPipelines)

#show()
