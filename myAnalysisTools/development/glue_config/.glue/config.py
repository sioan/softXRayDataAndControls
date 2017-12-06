from __future__ import absolute_import, division, print_function



"""Declare any extra link functions like this"""
#@link_function(info='translates A to B', output_labels=['b'])
#def a_to_b(a):
#    return a * 3
from glue.config import link_function

@link_function(info="Celsius to Fahrenheit", output_labels=['F'])
def celsius2farhenheit(c):
    return c  * 9. / 5. + 32

"""Data factories take a filename as input and return a Data object"""
#@data_factory('JPEG Image')
#def jpeg_reader(file_name):
#    ...
#    return data


"""Extra qt clients"""
#qt_client(ClientClass)
#from bball_viewer import bball_viewer_6
from dls import dls
#import simple_qt_overwrite
#from histogram.qt import data_viewer
#from histogram_mod.qt import data_viewer

"""
from glue.viewers.common.qt.data_viewer import DataViewer
from designer_examples.ExampleApp import ExampleApp 
#from glue.qt.widgets.data_viewer import DataViewer# no good

class MyGlueWidget(DataViewer):

    def __init__(self, session, parent=None):
        super(MyGlueWidget, self).__init__(session, parent=parent)
        self.my_widget = ExampleApp()
        self.setCentralWidget(self.my_widget)

# Register the viewer with glue
from glue.config import qt_client
qt_client.add(MyGlueWidget)"""
