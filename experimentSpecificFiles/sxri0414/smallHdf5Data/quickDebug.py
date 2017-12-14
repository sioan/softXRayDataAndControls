#startup command below
#glue --auto-merge sxri0414run60.h5 -x quickDebug.py  doesn't work
#glue --auto-merge sxri0414run60.h5
#exec(open("./quickDebug.py").read())


"""import ctypes
int(0x7f94c17d2630)
a int(0x7f94c17d2630)
a  = int(0x7f94c17d2630)
b
b = ctypes.cast(a,ctypes.py_object)
b
b.value
b.value.my_sub_groups


b.value.my_sub_groups.keys()
b.value.my_sub_groups['0x7f94c1534e80']['offset']
b.value.my_sub_groups['0x7f94c1534e80']['offset'] = 0
b.value.my_sub_groups['0x7f94c1534e80']['offset']

"""

"""
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

#my_dls_viewer = application.new_data_viewer(dls.dls_viewer)	#this doesn't work
my_Histogram_mod_viewer = application.new_data_viewer(data_viewer.HistogramViewer_mod)
my_Histogram_mod_viewer.add_data(dc[0])
my_Histogram_mod_viewer.x_att=myData.id['/GMD']
my_Histogram_mod_viewer.y_att=myData.id['/acqiris2']
######
"""
import sys           
import zmq                                          

port = "5556"      
# Socket to talk to server 
context = zmq.Context()
socket = context.socket(zmq.SUB)

print("Collecting updates from weather server...")
socket.connect ("tcp://localhost:%s" % port)


######
topicfilter = "10001"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

# Process 5 updates
total_value = 0
for update_nbr in range (5):
	string = socket.recv()
	topic, messagedata = string.split()
	total_value += int(messagedata)
	print(topic, messagedata)

print("Average messagedata value for topic '%s' was %dF" % (topicfilter,total_value / update_nbr))




