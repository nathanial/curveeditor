from __future__ import with_statement
import sys, os, random
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL, QSize
from PyQt4.QtGui import QMainWindow, QMenu, QWidget, QHBoxLayout, QFileDialog, \
    QTabWidget

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import arange, sin, pi

from util import each
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.tracks import TrackView
from las.file import LasFile

class ApplicationWindow(QMainWindow):
    def __init__(self):
        self.tracks = []
        QMainWindow.__init__(self)
        minimum_size_policy(self)
        self.track_views = []

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Curve Editor")
        self.main_widget = FileTabPanel(self)
        self.file_tab_panel = self.main_widget
        minimum_size_policy(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

        self.file_menu = FileMenu(self)
        self.menuBar().addMenu(self.file_menu)
        
        self.tracks_menu = TracksMenu(self)
        self.menuBar().addMenu(self.tracks_menu)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.updateGeometry()
        
    def closeEvent(self, ce):
        self.close()

    def sizeHint(self):
        return QSize(400, 700)

    def track_view_with_focus(self):
        return self.file_tab_panel.currentWidget()

    def create_new_track_view(self, lasfile):
        track_view = TrackView(lasfile, self, None)
        for i in range(0, self.tracks_menu.track_count):
            track_view.add_new_track()
        self.track_views.append(track_view)
        self.file_tab_panel.addTab(track_view, lasfile.name())
        return track_view

class FileTabPanel(QTabWidget):
    def __init__(self, main_window):
        self.main_window = main_window
        QTabWidget.__init__(self, main_window)
                        

class FileMenu(QMenu):
    def __init__(self, parent):
        self.app_window = parent
        QMenu.__init__(self, '&File', parent)
        self.addAction('&Open', self.open,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.addAction('&Save', self.save,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.addAction('&Save As', self.save_as)
        self.addAction('&Quit', self.quit,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
                       

    def open(self):
        dialog = QFileDialog(self, "Open LAS")
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            filename, = dialog.selectedFiles()
            if LasFile.is_lasfile(filename):
                lasfile = LasFile.from_(filename)
            else:
                raise "%s is not a las file!!" % filename
            self.app_window.create_new_track_view(lasfile)

    def save(self):
        track_view = self.app_window.track_view_with_focus()
        lasfile = track.curve_source
        filename = lasfile.path
        with open(filename, "w") as f:
            f.write(lasfile.to_las())

    def save_as(self):
        track_view = self.app_window.track_view_with_focus()
        lasfile = track_view.curve_source
        dialog = QFileDialog(self, "Save As")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec_():
            filename, = dialog.selectedFiles()
            with open(filename, "w") as f:
                f.write(lasfile.to_las())

    def quit(self):
        QApplication.quit()


class TracksMenu(QMenu):
    def __init__(self, main_window):
        self.track_count = 1
        self.main_window = main_window
        QMenu.__init__(self, '&Tracks', main_window)
        self.addAction('&Add Track', self.addTrack)
        self.addAction('&Remove Track', self.removeTrack)
        
    def addTrack(self):
        self.track_count += 1
        for track_view in self.main_window.track_views:
            track_view.add_new_track()
        
    def removeTrack(self):
        self.track_count -= 1
        for track_view in self.main_window.track_views:
            track_view.remove_track()
        for track_view in self.main_window.track_views:
            track_view.resize_after_remove()
