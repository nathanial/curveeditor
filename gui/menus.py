from __future__ import with_statement
import sys, os, random
from helpers import read_lasfile
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout, QFileDialog
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from util import each
from PyQt4.QtCore import SIGNAL

class FileMenu(QMenu):
    def __init__(self, parent):
        self.filename = None
        self.las_file = None
        self.app_window = parent
        QMenu.__init__(self, '&File', parent)
        self.addAction('&Open', self.openFile,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.addAction('&Save', self.saveFile,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.addAction('&Quit', self.fileQuit,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

    def openFile(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            self.filename, = dialog.selectedFiles()
            self.las_file = read_lasfile(self.filename)
            self.emit(SIGNAL("file_changed"), self.las_file)

    def saveFile(self):
        with open(self.filename, "w") as f:
            f.write(self.las_file.to_las())

    def fileQuit(self):
        self.app_window.close()

class TracksMenu(QMenu):
    def __init__(self, parent):
        self.app_window = parent
        QMenu.__init__(self, '&Tracks', parent)
        self.addAction('&Add Track', self.addTrack)
        self.addAction('&Remove Track', self.removeTrack)
        
    def addTrack(self):
        self.emit(SIGNAL("add_track"))
        
    def removeTrack(self):
        self.emit(SIGNAL("remove_track"))
                
class TrackContextMenu(QMenu):
    def __init__(self, track_window):
        QMenu.__init__(self, track_window)
        self.track_window = track_window
        self.track_color_menu = TrackColorMenu(track_window)
        self.track_marker_menu = TrackMarkerMenu(track_window)
        self.addMenu(self.track_color_menu)
        self.addMenu(self.track_marker_menu)

class TrackColorMenu(QMenu):
    def __init__(self, track_window):
        QMenu.__init__(self, "Color", track_window)
        self.track_window = track_window
        self.addAction('&Red', lambda: self.track_window.change_color("r",0))
        self.addAction('&Blue', lambda: self.track_window.change_color("b",0))
        self.addAction('&Green', lambda: self.track_window.change_color("g",0))    

class TrackMarkerMenu(QMenu):
    def __init__(self, track_window):
        QMenu.__init__(self, "Marker", track_window)
        self.track_window = track_window
        self.addAction('&None', lambda: self.track_window.change_marker("None",0))
        self.addAction('&Circle', lambda: self.track_window.change_marker("o",0))
        self.addAction('&Triangle', lambda: self.track_window.change_marker("^",0))
