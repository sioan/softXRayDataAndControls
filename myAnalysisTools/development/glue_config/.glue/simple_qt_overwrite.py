from glue.qt.widgets.data_viewer import DataViewer

class MyGlueWidget(DataViewer):

    def __init__(self, session, parent=None):
        super(MyGlueWidget, self).__init__(session, parent=parent)
        self.my_widget = MyWidget()
        self.setCentralWidget(self.my_widget)

# Register the viewer with glue
from glue.config import qt_client
qt_client.add(MyGlueWidget)
