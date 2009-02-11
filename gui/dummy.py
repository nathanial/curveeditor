from las.file import LasCurve, transform
from matplotlib.lines import Line2D
from PyQt4 import QtGui, QtCore
from gui.main import registry
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
        
        track = DummyTrack(self, width=4, height=6)
        button_panel = DummyTrackButtonPanel(self)

        layout = QVBoxLayout(self)
        layout.addWidget(button_panel)
        layout.addWidget(track)
        self.updateGeometry()

class DummyTrackButtonPanel(QWidget):
    def __init__(self, track_window):
        QWidget.__init__(self, track_window)
        minimum_size_policy(self)
        
        curve_info = DummyBox(self)
        layout = QVBoxLayout(self)
        layout.addWidget(curve_info)
        self.updateGeometry()

class DummyTrack(FigureCanvas):
    def __init__(self, parent = None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width,height), dpi=dpi)
        axes = fig.add_subplot(111)
        axes.hold(False)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        fixed_size_policy(self)



        
        

        
