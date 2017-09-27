from pylab import *

class roiConfigReader():
	def __init__ (self,fileName):
	#f = open("x229_ROI_V1.csv","r")
		self.f = open(fileName,"r")

		self.roiDescription = {}


		for i in self.f:
			myString = i.split(",")
			print(myString)
			if any ("#" in myString[0]):
				#print("should be skipping")
				continue
			if (len(i)<11):
				#print("should be skipping")
				#print(len(i))
				continue

			else:
				validRunStart,validRunEnd,roiName,upperLeftX,upperLeftY,lowerRightX,lowerRightY = myString[1:]
				self.roiDescription[roiName] = {}
				self.roiDescription[roiName]["validRunStart"] = int(validRunStart)
				self.roiDescription[roiName]["validRunEnd"] = int(validRunEnd)
				self.roiDescription[roiName]["upperLeftX"] = int(upperLeftX)
				self.roiDescription[roiName]["upperLeftY"] = int(upperLeftY)
				self.roiDescription[roiName]["lowerRightX"] = int(lowerRightX)
				self.roiDescription[roiName]["lowerRightY"] = int(lowerRightY[:-1])
