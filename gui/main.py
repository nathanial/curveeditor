from __future__ import with_statement
import sys, os, random

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QMainWindow, QMenu, QWidget, QHBoxLayout, QFileDialog

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import arange, sin, pi

from util import each
from las.file import LasFile
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.tracks import TrackView

class ApplicationWindow(QMainWindow):
    def __init__(self):
        self.tracks = []
        QMainWindow.__init__(self)
        minimum_size_policy(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Curve Editor")

        self.file_menu = FileMenu(self)

        self.menuBar().addMenu(self.file_menu)

        self.main_widget = QWidget(self)      
        minimum_size_policy(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

        self.track_view = TrackView(self, self.main_widget)
        self.main_layout.addWidget(self.track_view)
        self.track_view.add_dummy_track()

        QWidget.connect(self.file_menu, SIGNAL("update_curve_source"),
                        self.track_view.update_curve_source)
        
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.updateGeometry()
        
    def closeEvent(self, ce):
        self.close()

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
            filename, = dialog.selectedFiles()
            if LasFile.is_lasfile(filename):
                curve_source = LasFile.from_(filename)
            self.emit(SIGNAL("update_curve_source"), curve_source)

    def saveFile(self):
        with open(self.filename, "w") as f:
            f.write(self.las_file.to_las())

    def fileQuit(self):
        self.app_window.close()
