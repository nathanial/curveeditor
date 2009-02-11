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
from gui.menus import PlotsContextMenu
from gui.curve import Plot, TransformedCurve, PlotInfo
from gui.main import registry
from dummy import *

class Track(FigureCanvas):
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

    def switch_plot(self, old, new):
        self.axes.clear()
        index = self.plot.index(old)
        self.plots[index] = new
        for i in range(0, len(self.plots)):
            self.plots[i] = self._render_plot(self.plots[i])
        self.draw()

    def add_plot(self, plot):
        if self.first_plot():
            self.lowest_depth = pl.ymin()
            self.highest_depth = plot.ymax()
            self._reset_ylim()
        self.plots.append(self._render_plot(plot, add_plot = True))
        self.draw()

    def add_new_plot(self):
        curve_name = "dept" #fixme
        x = registry.get_curve(curve_name)
        y = registry.get_curve("depth")
        plot = Plot(curve_name, self, x, y, picker=5)
        self.add_plot(plot)

    def _render_plot(self, plot, add_plot = False):
        if plot.draggable: plot.disconnect_draggable()
        plot = plot.untransform()
        xscale = Track.xscale(plot, self.untransformed_plots(), add_plot)
        xoffset = Track.xoffset(plot, self.untransformed_plots(), add_plot)
        plot = plot.transform(xscale = xscale, xoffset = xoffset)
        self.axes.add_line(plot)
        self.axes.autoscale_view(scaley=False)
        plot.connect_draggable()
        return plot

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

    def untransformed_plots(self):
        return Track.untransform(self.plots)

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
    def xscale(plot, plots, add_plot = False):
        if add_plot:        
            plots = plots + [plot]
        return Track.xrange(plots) / plot.xrange()
    
    @staticmethod
    def xoffset(plot, plots, add_plot = False):
        if add_plot:
            plots = plots + [plot]
        return (Track.xmax(plots) - plot.xmax()) / 2.0

    @staticmethod
    def untransform(plots):
        return map(lambda p: p.untransform(), plots)

class TrackWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        fixed_size_policy(self)

        self.increment = 0        
        self.track = Track(self, width=4, height=6)        
        self.button_panel = TrackButtonPanel(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.button_panel)
        layout.addWidget(self.track)

        self.track.add_new_plot()
        self.updateGeometry()

    def contextMenuEvent(self, event):
        self.plots_context_menu = PlotsContextMenu(self)
        self.plots_context_menu.popup(event.globalPos())

    def curves(self):
        return self.track.curves
