import sys, os, random
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout, QPushButton,\
    QDialog, QRadioButton
from PyQt4.QtCore import SIGNAL, QSize
from numpy import arange, sin, pi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from util import times, each, lfind, partial
from las.file import transform
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.menus import CurvesContextMenu
from gui.curve import Curve, TransformedCurve, CurveInfo
from gui.main import registry
from gui.tracks import TrackWindow
from dummy import *

class TrackButtonPanel(QWidget):
    def __init__(self, track, track_window):
        QWidget.__init__(self, track_window)
        minimum_size_policy(self)
        self.track_window = track_window
        self.track = track
        self.plot_infos = []
        self.layout = QVBoxLayout(self)

    def add_plot_info(self, plot):
        plot_info = PlotInfo(plot, self.track, self)
        self.layout.addWidget(plot_info)
        self.plot_infos.append(plot_info)
    
    def remove_plot_info(self, plot):
        index = map(lambda ci: ci.curve, self.curve_infos).index(curve)
        deleted = self.curve_info[index]
        del self.curve_infos[index]
        deleted.hide()
        self.layout.removeWidget(deleted)

    def first_curve_info(self):
        return len(self.curve_infos) == 0

class TracksPanel(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self,parent)
        minimum_size_policy(self)
        self.track_windows = []
        self.tracks_layout = QHBoxLayout(self)
        self.las_file = None
        self.increment = 0
        self.first_time = True
        registry.lasfile_listeners.append(self.replace_dummy)
        
    def add_track_window(self, track_window):
        self.tracks_layout.addWidget(track_window)
        self.track_windows.append(track_window)

    def remove_track(self):
        right_most = self.track_windows[-1]
        right_most.hide()
        self.tracks_layout.removeWidget(right_most)
        self.track_windows = self.track_windows[:-1]
        self.resize_after_remove()

    def add_new_track(self):
        tw = TrackWindow(self)
        tw.increment = self.increment
        self.add_track_window(tw)

    def add_dummy_track(self):
        self.dummy_track = DummyTrackWindow(self)
        self.add_track_window(self.dummy_track)

    def remove_dummy_track(self):
        del self.track_windows[0]
        self.dummy_track.hide()
        self.tracks_layout.removeWidget(self.dummy_track)

    def resize_after_remove(self):
        self.updateGeometry()
        QApplication.processEvents()
        self.adjustSize()
        QApplication.processEvents()

    def change_depth(self, increment):
        self.increment = increment
        def each_tw(fn): each(self.track_windows, fn)
        each_tw(lambda tw: tw.set_increment(increment))
        each_tw(lambda tw: tw.track.draw())

    def replace_dummy(self):
        if self.first_time:
            self.remove_dummy_track()
            self.add_new_track()
            self.first_time = False
