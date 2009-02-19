import sys, os, random
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL, QSize
from PyQt4.QtGui import QMainWindow, QMenu, QWidget, QHBoxLayout, QFileDialog

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import arange, sin, pi

from util import each
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.tracks import TracksView

class ApplicationWindow(QMainWindow):
    def __init__(self):
        self.tracks = []
        QMainWindow.__init__(self)
        minimum_size_policy(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Curve Editor")
        self.main_widget = QWidget(self)      
        minimum_size_policy(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

        self.views_menu = ViewsMenu(self)
        self.menuBar().addMenu(self.views_menu)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.updateGeometry()
        
    def closeEvent(self, ce):
        self.close()

    def sizeHint(self):
        return QSize(400, 700)


class TracksFileMenu(QMenu):
    def __init__(self, parent):
        self.app_window = parent
        QMenu.__init__(self, '&File', parent)
        self.addAction('&Open', self.openFile,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.addAction('&Save', self.saveFile,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_S)

    def openFile(self):
        dialog = QFileDialog(self, "Open LAS")
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            filename, = dialog.selectedFiles()
            if LasFile.is_lasfile(self.filename):
                curve_source = LasFile.from_(self.filename)
            self.app_window.track_with_focus().update_curve_source(curve_source)

    def saveFile(self):
        track = self.app_window.track_with_focus()
        lasfile = track.curve_source
        filename = lasfile.path
        with open(filename, "w") as f:
            f.write(lasfile.to_las())



class FileMenu(QMenu):
    def __init__(self, parent):
        self.app_window = parent
        QMenu.__init__(self, '&File', parent)
        self.addAction('&Open', self.new_track_view,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_T)
        self.addAction('&Quit', self.quit,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

    def new_track_view(self): 
        self.tracks_view = TracksView(self.app_window,
                                      self.app_window.main_widget)
        self.app_window.main_layout.addWidget(self.tracks_view)
        self.tracks_view.select_file()

    def new_run_view(self): pass        

    def quit(self): 
        self.app_window.close()
