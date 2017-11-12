from pylab import *
ion()
#matplotlib.pyplot.switch_backend('QT4Agg')

import analysisPipeLine
import analysisPipeLineMonitor 

def f(a):
	return a[0]+a[1]

def g(y):
	#x = arange(0,2,0.01)
	#return sin(y**2*x)
	return y**2

def h(x):
	return x/10.0

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
