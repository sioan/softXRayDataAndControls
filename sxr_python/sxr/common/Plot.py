import matplotlib
#matplotlib.use("TkAgg")
import pylab as p
from numpy import array,isfinite
from PeakAnalysis import PeakAnalysis

class Plot2D:
	def __init__(self,i,x=None,y=None):
		self.__id = i
		p.ion(); # interactive on
		self.enable=True
		self.fig = p.figure(i)
		self.fig.canvas.set_window_title('SXRpython online plot')
		self.plot=self.fig.add_subplot(1,1,1); # make one plot
		specs = ['ko-','rs-','gd-','b^-','mv-','c>-','y<-']
		specdescs = ['black circles','red squares','green diamonds','blue triangles up','magenta triangles down','cyan triangles right','yellow triangles left (last linespec series, next will be black again)']
		specNO = self.fig.get_label()
		if not specNO:
			specNO=0
		if specNO==7:
			specNO=0
		thisspec = specs[specNO]
		print 'Data is plotted as %s.' % specdescs[specNO]
		self.fig.set_label(specNO+1)

		if (x is not None):
			self.line,=self.plot.plot(x,y,thisspec)
		else:
			self.line,=self.plot.plot([0, 1],[0,1],thisspec)
		p.draw()

	def win_title(self,title):
		self.fig.canvas.set_window_title(title)
	def set_xlabel(self,xlabel):
		p.figure(self.__id)
		p.xlabel(xlabel)
	def set_ylabel(self,ylabel):
		p.figure(self.__id)
		p.ylabel(ylabel)
	def set_title(self,title):
		p.figure(self.__id)
		p.title(title)

	def setdata(self,x,y):
		if (not self.enable):
			return
		p.figure(self.__id)
		x=array(x)
		y=array(y)
#		print y
#		idx = isfinite(y)
#		x = x[idx]
#		y = y[idx]
		self.line.set_data(x,y)
		self.plot.set_ylim(y.min(),y.max())
		self.plot.set_xlim(x.min(),x.max())
		try :
			(CEN,FWHM,PEAK) = PeakAnalysis(x,y)
		except:
			CEN=FWHM=PEAK=1e1000/1e1000
		title = "CEN %.3e, FWHM %.3e, PEAK %.3e" % (CEN,FWHM,PEAK)
		self.set_title(title)
		p.draw()

	def __call__(self,x,y):
		self.setdata(x,y)

