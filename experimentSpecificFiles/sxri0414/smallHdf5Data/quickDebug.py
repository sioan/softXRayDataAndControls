#startup command below
#glue --auto-merge sxri0414run60.h5 -x quickDebug.py  doesn't work
#glue --auto-merge sxri0414run60.h5
#exec(open("./quickDebug.py").read())


from glue.app.qt import GlueApplication
from glue.viewers.scatter.qt import ScatterViewer
from dls import dls
myData = dc[0]

#ga = GlueApplication(dc)
#scatter = ga.new_data_viewer(ScatterViewer)		#for starting new glue environment 
my_scatter_viewer = application.new_data_viewer(ScatterViewer)	#for existing glue environment
my_scatter_viewer.add_data(myData)
my_scatter_viewer.state.x_att=myData.id['/GMD']
my_scatter_viewer.state.y_att=myData.id['/acqiris2']

#my_dls_viewer = application.new_data_viewer(dls.dls_viewer)
my_Histogram_mod_viewer = application.new_data_viewer(data_viewer.HistogramViewer_mod)
my_Histogram_mod_viewer.add_data(myData)
my_Histogram_mod_viewer.x_att=myData.id['/GMD']
my_Histogram_mod_viewer.y_att=myData.id['/acqiris2']

