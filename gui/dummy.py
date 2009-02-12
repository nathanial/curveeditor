from las.file import LasCurve, transform
from matplotlib.lines import Line2D
from PyQt4 import QtGui, QtCore
from gui.program import registry
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout, QPushButton,\
    QDialog, QRadioButton
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from gui.gutil import minimum_size_policy, fixed_size_policy
from matplotlib.figure import Figure

class DummyBox(QComboBox):
    def __init__(self, *args):
        QComboBox.__init__(self, *args)

class DummyTrackWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        fixed_size_policy(self)
        
        self.button_panel = DummyTrackButtonPanel(self)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.button_panel)
        self.updateGeometry()

class DummyTrackButtonPanel(QWidget):
    def __init__(self, track_window):
        QWidget.__init__(self, track_window)
        minimum_size_policy(self)
        curve_info = DummyBox(self)
        layout = QVBoxLayout(self)
        layout.addWidget(curve_info)
        self.updateGeometry()

class DummyTrackCanvas(FigureCanvas):
    def __init__(self, parent = None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width,height), dpi=dpi)
        axes = fig.add_subplot(111)
        axes.hold(False)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        fixed_size_policy(self)

class DummyTrack(object):
    def __init__(self, parent = None):
        self.window = DummyTrackWindow(parent)
        self.track = DummyTrackCanvas(self.window, width=4, height=6)
        self.window.layout.addWidget(self.track)

    def hide(self):
        self.window.hide()
        self.track.hide()

