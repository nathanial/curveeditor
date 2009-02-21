from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL, QSize, QStringList
from PyQt4.QtGui import QMainWindow, QMenu, QWidget, QHBoxLayout, QFileDialog, \
    QTabWidget, QListView, QDialog, QStringListModel, QListWidget, QListWidgetItem, \
    QVBoxLayout, QPushButton, QAbstractItemView, QLabel
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.plots import *
from gui.tracks import *

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

class MergeTrack(Track):
    def __init__(self, curve_source, parent = None):
        Track.__init__(self, curve_source, parent)
        self.source_label = QLabel(curve_source.name(), self)
        self.layout.insertWidget(0, self.source_label)
