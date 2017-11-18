def makeGraphableData(unBinnedDataDictionary,instructionObject):
	#instructionObject has the mode. raw binning, correlation, saturated correction correlation

	#instantiation
	unBinnedDataDictionary[''] = 0

	
	graphableDataObject['x'] = xDataBinned
	graphableDataObject['y'] = yDataBinned
	graphableDataObject['yStandDev'] = yStandDev

	return graphableDataObject
