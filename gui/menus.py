from __future__ import with_statement
import sys, os, random
from helpers import read_lasfile
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout, QFileDialog
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from util import each, times
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

class CurvesContextMenu(QMenu):
    def __init__(self, track_window):
        QMenu.__init__(self, track_window)
        curves = track_window.curves
        
        self.addAction('&Add Curve', track_window.add_new_curve)
        
        def create_and_add(i):
            print "creating and adding"
            menu = CurveContextMenu(self,curves[i].curve_name, i, track_window)
            self.addMenu(menu)
        times(len(curves), create_and_add)

        QApplication.processEvents()
        self.updateGeometry()
        QApplication.processEvents()
        self.adjustSize()
                
class CurveContextMenu(QMenu):
    def __init__(self, parent, curve_name, index, track_window):
        QMenu.__init__(self,curve_name, parent)
        self.track_window = track_window
        self.track_color_menu = CurveColorMenu(index,track_window)
        self.track_marker_menu = CurveMarkerMenu(index,track_window)
        self.addMenu(self.track_color_menu)
        self.addMenu(self.track_marker_menu)

class CurveColorMenu(QMenu):
    def __init__(self, index, track_window):
        QMenu.__init__(self,"Color")
        self.track_window = track_window
        self.addAction('&Red', lambda: self.track_window.change_color("r",index))
        self.addAction('&Blue', lambda: self.track_window.change_color("b",index))
        self.addAction('&Green', lambda: self.track_window.change_color("g",index))    

class CurveMarkerMenu(QMenu):
    def __init__(self, index, track_window):
        QMenu.__init__(self,"Marker")
        self.track_window = track_window
        self.addAction('&None', lambda: self.track_window.change_marker("None",index))
        self.addAction('&Circle', lambda: self.track_window.change_marker("o",index))
        self.addAction('&Triangle', lambda: self.track_window.change_marker("^",index))
