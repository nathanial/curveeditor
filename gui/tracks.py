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
from util import times, each, lfind, partial, swap
from las.file import transform
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.menus import PlotsContextMenu
from gui.panels import TrackButtonPanel
from gui.plots import Plot
from gui.main import registry
from dummy import *

class TrackCanvas(FigureCanvas):
    def __init__(self, parent = None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)
        self.plots = []
        self.increment = 0
        self.lowest_depth = None
        self.highest_depth = None

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        fixed_size_policy(self)

    def swap_plot(self, old, new):
        new.canvas = self
        self.axes.clear()
        swap(self.plots, old, new)
        each(self.plots, self._render_plot)
        self.draw()

    def add_plot(self, plot):
        if self.first_plot():
            self.lowest_depth = plot.ymin()
            self.highest_depth = plot.ymax()
            self._reset_ylim()
        plot.canvas = self
        self.axes.clear()
        self.plots.append(plot)
        each(self.plots, self._render_plot)
        self.draw()

    def _render_plot(self, plot):
        xscale = TrackCanvas.xscale(plot, self.plots)
        xoffset = TrackCanvas.xoffset(plot, self.plots)
        plot.scale(xscale = xscale, xoffset = xoffset)
        self.axes.add_line(plot)
        self.axes.autoscale_view(scaley=False)
        if not plot.draggable: plot.connect_draggable()

    def set_increment(self, increment):
        self.increment = increment
        self._reset_ylim()

    def _reset_ylim(self):
        self.axes.set_ylim(self.lowest_depth + self._percentage_increment(),
                           self.lowest_depth + 100 + self._percentage_increment())

    def _percentage_increment(self):
        return ((self.increment + 1) / 100.0) * self.depth_range()

    def depth_range(self):
        return self.highest_depth - self.lowest_depth

    def first_plot(self):
        return len(self.plots) == 0

    @staticmethod
    def xrange(plots):        
        return max([p.xrange() for p in plots])

    @staticmethod
    def xmin(plots):
        return min([p.xmin() for p in plots])

    @staticmethod
    def xmax(plots):
        return max([p.xmax() for p in plots])

    @staticmethod
    def xscale(plot, plots):
        return TrackCanvas.xrange(plots) / plot.xrange()
    
    @staticmethod
    def xoffset(plot, plots):
        return (TrackCanvas.xmax(plots) - plot.xmax()) / 2.0


class TrackWindow(QWidget):
    def __init__(self, track, parent = None):
        QWidget.__init__(self, parent)
        fixed_size_policy(self)
        self.track = track

        self.button_panel = TrackButtonPanel(track, self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.button_panel)

    def contextMenuEvent(self, event):
        self.plots_context_menu = PlotsContextMenu(self.track, self)
        self.plots_context_menu.popup(event.globalPos())

class Track(object):
    def __init__(self, parent = None):
        self.increment = 0        
        self.window = TrackWindow(self, parent)
        self.track_canvas = TrackCanvas(self.window, width=4, height=6)
        self.window.layout.addWidget(self.track_canvas)
        self.add_new_plot()
        self.window.updateGeometry()
        
    def change_curve(self, old_plot, curve_name): 
        new_plot = Plot.of(curve_name, "depth")
        self.track_canvas.swap_plot(old_plot, new_plot)
        self.window.button_panel.swap_plot_info(old_plot, new_plot)

    def add_new_plot(self):
        plot = Plot.of("dept", "depth")
        self.track_canvas.add_plot(plot)
        self.window.button_panel.add_plot_info(plot)
        self.window.updateGeometry()

    def plots(self):
        return list(self.track_canvas.plots)

    def set_increment(self, increment):
        self.track_canvas.set_increment(increment)

    def draw(self):
        self.track_canvas.draw()
