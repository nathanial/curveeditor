from __future__ import with_statement
import sys, os, random
from helpers import read_lasfile
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout, QFileDialog
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gui.plots import Track, DraggableLine, TrackWindow
from util import each
from PyQt4.QtCore import SIGNAL
from gui.menus import FileMenu, TracksMenu
from gui.gutil import minimum_size_policy, fixed_size_policy

class ApplicationWindow(QMainWindow):
    def __init__(self):
        self.tracks = []
        QMainWindow.__init__(self)
        minimum_size_policy(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Curve Editor")

        self.file_menu = FileMenu(self)
        self.connect(self.file_menu, SIGNAL("file_changed"), self.send_to_tracks)

        self.tracks_menu = TracksMenu(self)
        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.tracks_menu)

        self.main_widget = QWidget(self)      
        minimum_size_policy(self.main_widget)
        
        self.setup_tracks(self.main_widget)
        
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.updateGeometry()
        
    def closeEvent(self, ce):
        self.close()

    def add_track(self, track):
        self.track_layout.addWidget(track)
        self.tracks.append(track)
        self.updateGeometry()

    def remove_track(self):
        right_most = self.tracks[-1]
        right_most.hide()
        self.track_layout.removeWidget(right_most)
        self.tracks = self.tracks[:-1]
        each(self.tracks, lambda t: t.updateGeometry())
        self.updateGeometry()

    def add_new_track(self):
        tw = TrackWindow(self.main_widget)
        if self.file_menu.las_file:
            tw.las_update(self.file_menu.las_file)
        self.add_track(tw)

    def setup_tracks(self, main_widget):
        self.track_layout = QHBoxLayout(self.main_widget)
        self.add_new_track()

    def send_to_tracks(self, las_file):
        each(self.tracks, lambda t: t.las_update(las_file))

