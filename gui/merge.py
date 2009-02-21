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
        self.ymin = min([cs.index().min() for cs in self.curve_sources])
        self.ymax = max([cs.index().max() for cs in self.curve_sources])
        self.tracks = [MergeTrack(cs,
                                  ymin=self.ymin,
                                  ymax=self.ymax,
                                  parent=self)
                       for cs in self.curve_sources]
        for mt in self.tracks:
            self.layout.addWidget(mt)
        
        self.merge_left_button = QPushButton("merge_left", self)
        self.layout.addWidget(self.merge_left_button)
        QWidget.connect(self.merge_left_button,
                        SIGNAL("clicked()"),
                        self.merge_left)

        self.merge_right_button = QPushButton("merge_right", self)
        self.layout.addWidget(self.merge_right_button)
        QWidget.connect(self.merge_right_button,
                        SIGNAL("clicked()"),
                        self.merge_right)
        
    def merge_left(self): 
        tlen = len(self.tracks)
        rrange = range(0, tlen)
        rrange.reverse()
        for i in rrange:
            if i > 0:
                lsource = self.tracks[i-1].curve_source
                rsource = self.tracks[i].curve_source
                new_source = lsource.merge_left(rsource)
                new_source.path = lsource.path
                self.tracks[i-1].my_disconnect()
                self.layout.removeWidget(self.tracks[i-1])
                self.tracks[i-1] = MergeTrack(new_source, self.ymin, self.ymax, self)
                
        for track in self.tracks[1:]:
            self.layout.addWidget(track)
                
    def merge_right(self): 
        tlen = len(self.tracks)
        
        for track in self.tracks[1:]:
            track.my_disconnect()
            self.layout.removeWidget(track)

        for i in range(0, tlen):
            if i < tlen - 1:
                lsource = self.tracks[i].curve_source
                rsource = self.tracks[i+1].curve_source
                new_source = lsource.merge_right(rsource)
                new_source._name = "merged"
                self.tracks[i+1] = MergeTrack(new_source, self.ymin, self.ymax, self)
                self.layout.addWidget(self.tracks[i+1])
                

class MergeTrack(Track):
    def __init__(self, curve_source, ymin, ymax, parent):
        Track.__init__(self, curve_source, parent,
                       ymin = ymin, ymax = ymax)
        self.source_label = QLabel(curve_source.name(), self)
        self.layout.insertWidget(0, self.source_label)        
