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
from util import times, each, lfind, partial, lindex
from las.file import transform
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.menus import PlotsContextMenu
from gui.plots import Plot, PlotInfo
from gui.main import registry
from dummy import *

class TrackButtonPanel(QWidget):
    def __init__(self, track, parent):
        QWidget.__init__(self, parent)
        minimum_size_policy(self)
        self.track = track
        self.plot_infos = []
        self.layout = QVBoxLayout(self)

    def add_plot_info(self, plot):
        pi = self._build_plot_info(plot)
        self.layout.addWidget(pi)
        self.plot_infos.append(pi)
    
    def remove_plot_info(self, plot):
        deleted, index = self._destroy_plot_info(plot)
        del self.plot_infos[index]
        deleted.hide()
        self.layout.removeWidget(deleted)

    def swap_plot_info(self, old_plot, new_plot):
        new_info = self._build_plot_info(new_plot)
        old_info, index = self._destroy_plot_info(old_plot)
        old_info.hide()
        self.plot_infos[index] = new_info
        self.relayout()

    def relayout(self):
        for pi in self.plot_infos:
            self.layout.removeWidget(pi)
        for pi in self.plot_infos:
            self.layout.addWidget(pi)
    
    def _connect_to_track(self, plot_info):
        QWidget.connect(plot_info,
                        SIGNAL("change_curve"),
                        self.track.change_curve)

    def _disconnect_from_track(self, plot_info):
        QWidget.disconnect(plot_info,
                           SIGNAL("change_curve"),
                           self.track.change_curve)

    def _plot_index(self, plot):
        return map(lambda pi: pi.plot, self.plot_infos).index(plot)

    def _build_plot_info(self, plot):
        plot_info = PlotInfo(plot, self)
        self._connect_to_track(plot_info)
        return plot_info
    
    def _destroy_plot_info(self, plot):
        index = self._plot_index(plot)
        pi = self.plot_infos[index]
        self._disconnect_from_track(pi)
        return pi, index
        
        
            
        

from gui.tracks import TrackWindow
class TracksPanel(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self,parent)
        minimum_size_policy(self)
        self.tracks = []
        self.layout = QHBoxLayout(self)
        self.first_time = True
        registry.lasfile_listeners.append(self.replace_dummy)
        
    def add_track(self, track):
        self.layout.addWidget(track.window)
        self.tracks.append(track)

    def remove_track(self):
        track = self.tracks[-1]
        track.window.hide()
        self.layout.removeWidget(track.window)
        del self.tracks[-1]
        self.resize_after_remove()

    def add_new_track(self):
        from gui.tracks import Track
        track = Track(self)
        self.add_track(track)

    def add_dummy_track(self):
        self.dummy_track = DummyTrack(self)
        self.add_track(self.dummy_track)

    def remove_dummy_track(self):
        del self.tracks[0]
        self.dummy_track.hide()
        self.layout.removeWidget(self.dummy_track.window)

    def resize_after_remove(self):
        self.updateGeometry()
        QApplication.processEvents()
        self.adjustSize()
        QApplication.processEvents()

    def change_depth(self, increment):
        for track in self.tracks: track.set_increment(increment)
        for track in self.tracks: track.draw()

    def replace_dummy(self):
        if self.first_time:
            self.remove_dummy_track()
            self.add_new_track()
            self.first_time = False
