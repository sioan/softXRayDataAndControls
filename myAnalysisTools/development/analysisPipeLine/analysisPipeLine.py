#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python

#--------------------------------------------------------------------------
# File and Version Information:
#  $Id: README 2017-08-06 18:54:12Z sioan@SLAC.STANFORD.EDU $
#
# Description:
#  README file for data analysis
#------------------------------------------------------------------------

#Package author: Sioan Zohar

#Brief description:
#==================
#Abstracts away details of manual ordering of 
#
#summary of organic analysis procedures below. problems are self evident.
#1) code analysis pipeline (e.g. bin size, filtering criteria, normalization procedure)
#2) visually compare to previous analysis routines. and theory. does it provide expected results? Yes, skip to step 8! No continue
#3) code another analysis pipeline (e.g. bin size, filtering criteria, normalization procedure)
#4) is analysis (quality metric)  better or worse than previous analysis?

#4) figure out metric for better or worse.  go back to 1
#5) display analysis quality metric vs algorithm /  tuning parameter
#6) choose algorithm and tuning parameters that are best for data. (optimize some set of metrics)


#7) how does frequency domain behavior change with binning? (un binned? how to compare on same graph)

#8) create figure for publication
#==================
#implementation

class makeAnalysisPipeLineInstance():
	#members
	def __init__(self,pipeLineAlias):
		self.pipeLineAlias = pipeLineAlias
		self.collectionOfAnalysisSteps = {}	#e.g. load data, normalize x by y, bins along z,
		self.collectionOfAnalysisResults = {}
		self.collectionOfDisplayConfigurations = {}
		self.orderOfAnalyses = [] #(this should always have all the keys from collection of analysis steps)
		
		#destinationList will be used to indicate which function should use which data. The dict key is the data source and the entry is the destination. 
		#can be used to fork. but multiple function calls can't be duplicated unless they have aliases. is this problem present regardless?
		#Thoughts for later.  Instead of a collectionOfAnalysisSteps, have a layer of analyses. Layer1, Layer2, Layer3.  each Layer has inputs 
		#This could be visualized by an overlay architecture this would be better described by a controls diagram.
		self.destinationList = {} 
		

	#methods
	def insert_analysis_step(self,nameOfNewStep,placeToInsert):
		
		

		return 0

	def remove_analysis_step(self,analysis_alias):
		if(analysis_alias in self.collectionOfAnalysisSteps):
			del self.collectionOfAnalysisSteps[analysis_alias]
		if(analysis_alias in self.collectionOfAnalysisResults):
			del self.collectionOfAnalysisResults[analysis_alias]

		self.orderOfAnalyses = [i for i in self.orderOfAnalyses if i != analysis_alias]
		return 0

	def append_analysis_step(self,analysis_function,analysis_alias):
		self.collectionOfAnalysisSteps[analysis_alias] = analysis_function
		self.orderOfAnalyses.append(analysis_alias)
		return 0

	def execute_analysis(self,initial_input):

		firstAnalysisStep = self.orderOfAnalyses[0]
		self.collectionOfAnalysisResults[firstAnalysisStep] = self.collectionOfAnalysisSteps[firstAnalysisStep](initial_input)
		print("executing step "+firstAnalysisStep)

		for i in range(1,len(self.orderOfAnalyses)):
			previousAnalysisStep, currentAnalysisStep = self.orderOfAnalyses[i-1], self.orderOfAnalyses[i]
			previousResult = self.collectionOfAnalysisResults[previousAnalysisStep]
			print("executing step "+currentAnalysisStep)
			self.collectionOfAnalysisResults[currentAnalysisStep] = self.collectionOfAnalysisSteps[currentAnalysisStep](previousResult) 

	def displayDataSummary():
		return 0
#collectionOfAnaysisPipelines = {}
#collectionOfAnaysisPipelines['first_try'] = makeAnalysisPipeLineInstance
#display and compare collectionOfAnaysisPipelines['first_try'].collectionOfAnalysisResults


#################################


