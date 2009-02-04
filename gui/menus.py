from __future__ import with_statement
import sys, os, random
from helpers import read_lasfile
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout, QFileDialog
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gui.tracks import Track, DraggableLine, TrackWindow
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
        
        
