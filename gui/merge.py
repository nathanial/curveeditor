from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL, QSize, QStringList
from PyQt4.QtGui import QMainWindow, QMenu, QWidget, QHBoxLayout, QFileDialog, \
    QTabWidget, QListView, QDialog, QStringListModel, QListWidget, QListWidgetItem, \
    QVBoxLayout, QPushButton, QAbstractItemView
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.plots import *

class MergePanel(QWidget):
    def __init__(self, curve_sources, parent = None): 
        QWidget.__init__(self, parent)
        self.curve_sources = curve_sources
        self.name = "merge " + " ".join([cs.name() for cs in self.curve_sources])
        self.merge_tracks = [MergeTrack(cs,self) for cs in self.curve_sources]
        self.layout = QHBoxLayout(self)
        for mt in self.merge_tracks:
            self.layout.addWidget(mt)
        
    def merge_left(self): pass

    def merge_right(self): pass    

class MergeTrack(QWidget):
    def __init__(self, curve_source, parent = None):
        QWidget.__init__(self, parent)
        fixed_size_policy(self)
        self.curve_source = curve_source
        self.plot_canvas = PlotCanvas(self, width=4, height=6)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.plot_canvas)
        self.updateGeometry()
