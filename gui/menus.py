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
from gui.program import registry
from las.file import LasFile
from gui.plots import Plot

class FileMenu(QMenu):
    def __init__(self, parent):
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
            registry.filename, = dialog.selectedFiles()
            registry.lasfile = LasFile.from_(registry.filename)

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

class PlotsContextMenu(QMenu):
    def __init__(self, track, parent):
        QMenu.__init__(self, parent)
        self.track = track
        plots = track.plots()

        self.addAction('&Add Curve', self.track.add_new_plot)        
        for plot in plots:
            self.addMenu(PlotContextMenu(self, plot))

        QApplication.processEvents()
        self.updateGeometry()
        QApplication.processEvents()
        self.adjustSize()
                
class PlotContextMenu(QMenu):
    def __init__(self, parent, plot):
        QMenu.__init__(self, plot.name(), parent)
        color_menu = PlotColorMenu(self,plot)
        marker_menu = PlotMarkerMenu(self,plot)
        self.addMenu(color_menu)
        self.addMenu(marker_menu)

class PlotColorMenu(QMenu):
    def __init__(self, parent,plot):
        QMenu.__init__(self,"Color", parent)
        self.addAction('&Red', lambda: plot.set_color("r"))
        self.addAction('&Blue', lambda: plot.set_color("b"))
        self.addAction('&Green', lambda: plot.set_color("g"))

class PlotMarkerMenu(QMenu):
    def __init__(self, parent, plot):
        QMenu.__init__(self,"Marker", parent)
        self.addAction('&None', lambda: plot.set_marker("None"))
        self.addAction('&Circle', lambda: plot.set_marker("o"))
        self.addAction('&Triangle', lambda: plot.set_marker("^"))
