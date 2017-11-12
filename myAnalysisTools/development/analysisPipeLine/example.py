from pylab import *
import analysisPipeLine

def f(a,b):
	return a+b

def g(y):
	return y**2

def h(x):
	return x/10.0

collectionOfAnaysisPipelines = {}

collectionOfAnaysisPipelines['myFirstPipeLine'] = analysisPipeLine.makeAnalysisPipeLineInstance('myFirstPipeLine')

#append_analysis_step(self,analysis_function,analysis_alias):
collectionOfAnaysisPipelines['myFirstPipeLine'].append_analysis_step(self,f,"a_plus_b")

collectionOfAnaysisPipelines['myFirstPipeLine'].append_analysis_step(self,g,"square")

collectionOfAnaysisPipelines['myFirstPipeLine'].append_analysis_step(self,g,"divide_by_ten")
