from glue.viewers.custom.qt import CustomViewer

from glue.core.subset import RoiSubsetState

from matplotlib.colors import LogNorm
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.lines import Line2D
import numpy as np

class dls_viewer(CustomViewer):
    name = 'dls_viewer'
    x = 'att(/GMD)'	#this switch swaps the x and y axes.
    y = 'att(/acqiris2)'	#need to figure out how to make this programable.  Replaced x and y with pop and viv, then need to rename in glue.
    bins = (10, 100)
    #more_bins =(-10,10)	#this adds bins 
    z = 'att(/atm_corrected_timing)'
    ephoton = 'att(/ebeam/photon_energy)'
    hitrate = False
    color = ['Reds', 'Purples']
    #hit = 'att(shot_made)'

    def make_selector(self, roi, x, y):

        state = RoiSubsetState()
        state.roi = roi
        state.xatt = x.id
        state.yatt = y.id

        return state

    def plot_data(self, axes, x, y,z, color, style,bins):
        #axes.hexbin(x, y,cmap=color,gridsize=bins,norm=LogNorm(),mincnt=1)
        myHistogramW=np.histogram(z,bins=np.arange(326.9,347.1,0.075),weights = np.nan_to_num(y*x*1.0/(x**2+1e-12)))
        myHistogram=np.histogram(z,bins=np.arange(326.9,347.1,0.075))
        the_dls= myHistogramW[0]/myHistogram[0]
        the_dls -= np.mean(the_dls)
        the_dls/=np.std(the_dls)
        axes.plot(myHistogram[1][:-1],the_dls[::-1],marker='o',linewidth=0)
        #print(myHistogram)
        #print(z)
        #axes.plot(np.arange(1000))

    def plot_subset(self, axes, x, y,z, style,bins):
        #axes.plot(x, y, 'o', alpha=style.alpha, mec=style.color,mfc=style.color, ms=style.markersize)
        #axes.hexbin(x, y,cmap='Reds', gridsize=bins, mincnt=1)	#this plots another set of hexbins instead of points
        myHistogramW=np.histogram(z,bins=np.arange(326.9,347.1,0.075),weights = np.nan_to_num(y*x*1.0/(x**2+1e-12)))
        myHistogram=np.histogram(z,bins=np.arange(326.9,347.1,0.075))
        the_dls= myHistogramW[0]/myHistogram[0]
        the_dls -= np.mean(the_dls)
        the_dls/=np.std(the_dls)
        axes.plot(myHistogram[1][:-1],the_dls[::-1],mec=style.color,mfc=style.color,marker='o',linewidth=0)

    def setup(self, axes):
        temp =0 
        axes.set_ylim(-1, 1)
        axes.set_xlim(326, 347)
        #axes.set_aspect('equal', adjustable='datalim')
