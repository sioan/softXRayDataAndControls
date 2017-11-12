import matplotlib.pyplot as plt
import numpy as np

#operates on dictionary of pipelines.
class matplotlibMonitor():
	def __init__(self):	
		self.myFigureDictionary = {}
		#self.collectionOfAnalysisPipelines = collectionOfAnalysisPipelines

	def analysisMatplotlibMonitor(self,collectionOfAnalysisPipelines):
		
		for i in collectionOfAnalysisPipelines:
				
	
			#myFigureDictionary[i]['myColor']=iter(cm.rainbow(np.linspace(0,1,len(myDataDict.keys()))))
			for j in collectionOfAnalysisPipelines[i].collectionOfAnalysisResults:
				print (i+", "+j)
				y = collectionOfAnalysisPipelines[i].collectionOfAnalysisResults[j]
				try:
					
					self.myFigureDictionary[j]['axs'].plot(y)
				except KeyError:
					self.myFigureDictionary[j] = {}
					self.myFigureDictionary[j]['fig'], self.myFigureDictionary[j]['axs'] = plt.subplots(nrows=1, ncols=1, sharex=True)	
					self.myFigureDictionary[j]['axs'].set_title(j)	
					self.myFigureDictionary[j]['axs'].plot(y)

		for i in self.myFigureDictionary:
			self.myFigureDictionary[j]['axs'].legend()

	def showPlots(self):
		for j in self.myFigureDictionary:
			self.myFigureDictionary[j]['fig'].show()
	
	def clearPlots(self):
		for i in self.myFigureDictionary:
			self.myFigureDictionary[i]['axs'].cla()

