from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL, QSize, QStringList
from PyQt4.QtGui import QMainWindow, QMenu, QWidget, QHBoxLayout, QFileDialog, \
    QTabWidget, QListView, QDialog, QStringListModel, QListWidget, QListWidgetItem, \
    QVBoxLayout, QPushButton, QAbstractItemView, QLabel, QGroupBox
from gutil import minimum_size_policy, fixed_size_policy
from plots import *
from tracks import *

class MergePanel(AbstractTrackPanel):
    def __init__(self, curve_sources, parent = None): 
        AbstractTrackPanel.__init__(self, [], parent)
        self._setup_buttons()
        self.curve_sources = curve_sources
        self.name = "merge " + " ".join([cs.name() for cs in self.curve_sources])
        self.ymin = min([cs.index().min() for cs in self.curve_sources])
        self.ymax = max([cs.index().max() for cs in self.curve_sources])
        self._setup_depth_slider(self.ymin, self.ymax)
        self.tracks = [MergeTrack(cs, 
                                  ymin=self.ymin,
                                  ymax=self.ymax,
                                  parent=self)
                       for cs in self.curve_sources]
        for mt in self.tracks:
            self.layout.addWidget(mt)
        

    def _setup_buttons(self):
        self.button_box = QGroupBox(self)
        self.bb_layout = QVBoxLayout()
        
        self.merge_left_button = QPushButton("merge_left", self)
        self.bb_layout.addWidget(self.merge_left_button, 0, Qt.AlignTop)
        QWidget.connect(self.merge_left_button,
                        SIGNAL("clicked()"),
                        self.merge_left)

        self.merge_right_button = QPushButton("merge_right", self)
        self.bb_layout.addWidget(self.merge_right_button, 1, Qt.AlignTop)
        QWidget.connect(self.merge_right_button,
                        SIGNAL("clicked()"),
                        self.merge_right)

        self.layout.addWidget(self.button_box)
        self.button_box.setLayout(self.bb_layout)

    def merge_left(self): 
        self._clear_tracks()
        tlen = len(self.tracks)
        rrange = range(0, tlen)
        rrange.reverse()
        for i in rrange:
            if i > 0:
                lsource = self.tracks[i-1].curve_source
                rsource = self.tracks[i].curve_source
                new_source = lsource.merge_left(rsource)
                new_source._name = "merged"
                self.tracks[i-1].my_disconnect()
                self.tracks[i-1] = MergeTrack(new_source, self.ymin, self.ymax, self)
        self._restore_tracks()
                
    def merge_right(self): 
        self._clear_tracks()
        tlen = len(self.tracks)
        for i in range(0, tlen):
            if i < tlen - 1:
                lsource = self.tracks[i].curve_source
                rsource = self.tracks[i+1].curve_source
                new_source = lsource.merge_right(rsource)
                new_source._name = "merged"
                self.tracks[i+1].my_disconnect()
                self.tracks[i+1] = MergeTrack(new_source, self.ymin, self.ymax, self)
                self.layout.addWidget(self.tracks[i+1])
        self._restore_tracks()

    def _clear_tracks(self):
        for track in self.tracks:
            self.layout.removeWidget(track)
    
    def _restore_tracks(self):
        for track in self.tracks:
            self.layout.addWidget(track)
                

class MergeTrack(Track):
    def __init__(self, curve_source, ymin, ymax, parent):
        Track.__init__(self, curve_source, parent,
                       ymin = ymin, ymax = ymax)
        self.source_label = QLabel(curve_source.name(), self)
        self.layout.insertWidget(0, self.source_label)        
