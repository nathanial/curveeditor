from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL, QSize, QStringList
from PyQt4.QtGui import QMainWindow, QMenu, QWidget, QHBoxLayout, QFileDialog, \
    QTabWidget, QListView, QDialog, QStringListModel, QListWidget, QListWidgetItem, \
    QVBoxLayout, QPushButton, QAbstractItemView, QLabel
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.plots import *
from gui.tracks import *

class MergePanel(AbstractTrackPanel):
    def __init__(self, curve_sources, parent = None): 
        AbstractTrackPanel.__init__(self, [], parent)
        self.curve_sources = curve_sources
        self.name = "merge " + " ".join([cs.name() for cs in self.curve_sources])
        ymin = min([cs.index().min() for cs in self.curve_sources])
        ymax = max([cs.index().max() for cs in self.curve_sources])
        self.tracks = [MergeTrack(cs,ymin=ymin,ymax=ymax,parent=self)
                       for cs in self.curve_sources]
        for mt in self.tracks:
            self.layout.addWidget(mt)
        
    def merge_left(self): pass

    def merge_right(self): pass    

class MergeTrack(Track):
    def __init__(self, curve_source, ymin, ymax, parent):
        Track.__init__(self, curve_source, parent,
                       ymin = ymin, ymax = ymax)
        self.source_label = QLabel(curve_source.name(), self)
        self.layout.insertWidget(0, self.source_label)
