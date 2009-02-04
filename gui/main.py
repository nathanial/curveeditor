from __future__ import with_statement
import sys, os, random
from helpers import read_lasfile
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QLayout
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gui.tracks import Track, DraggableLine, TrackWindow, TracksPanel
from util import each
from PyQt4.QtCore import SIGNAL
from gui.menus import FileMenu, TracksMenu
from gui.gutil import minimum_size_policy, fixed_size_policy

class DepthSlider(QSlider):
    def __init__(self, parent = None):
        QSlider.__init__(self, QtCore.Qt.Vertical, parent)

class ApplicationWindow(QMainWindow):
    def __init__(self):
        self.tracks = []
        QMainWindow.__init__(self)
        minimum_size_policy(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Curve Editor")

        self.file_menu = FileMenu(self)

        self.tracks_menu = TracksMenu(self)

        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.tracks_menu)

        self.main_widget = QWidget(self)      
        minimum_size_policy(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.depth_slider = DepthSlider(self.main_widget)
        self.main_layout.addWidget(self.depth_slider)
        self.main_layout.setSizeConstraint(QLayout.SetNoConstraint)

        self.tracks_panel = TracksPanel(self.main_widget)
        self.main_layout.addWidget(self.tracks_panel)
        self.connect(self.file_menu, SIGNAL("file_changed"), 
                     self.tracks_panel.send_to_tracks)
        self.connect(self.tracks_menu, SIGNAL("add_track"), 
                     self.tracks_panel.add_new_track)
        self.connect(self.tracks_menu, SIGNAL("remove_track"),
                     self.remove_track_and_resize)
        self.connect(self.depth_slider, SIGNAL("valueChanged(int)"),
                     self.tracks_panel.change_depth)
        
        self.tracks_panel.add_new_track()
        
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.updateGeometry()
        
    def closeEvent(self, ce):
        self.close()

    def remove_track_and_resize(self):
        self.tracks_panel.remove_track()
        self.main_widget.updateGeometry()
        self.main_widget.adjustSize()
        self.updateGeometry()
        self.adjustSize()
