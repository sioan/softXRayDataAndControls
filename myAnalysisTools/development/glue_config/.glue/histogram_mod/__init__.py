def setup():
    from glue.config import qt_client
    from .qt.data_viewer import HistogramViewer_mod
    qt_client.add(HistogramViewer_mod)
