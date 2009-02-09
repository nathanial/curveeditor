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
from gui.curve import Curve, TransformedCurve

class Track(FigureCanvas):
    def __init__(self, parent = None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)
        self.curves = []
        self.increment = 0
        self.lowest_depth = None
        self.highest_depth = None
        self.colors = ["b"]
        self.markers = ["None"]

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        fixed_size_policy(self)

    def switch_curve(self, curve, index):
        self.axes.clear()
        if self.first_curve():
            self.lowest_depth = curve.ymin()
            self.highest_depth = curve.ymax()
            self._reset_ylim()
            self.curves.append(self._render_curve(curve, add_curve=True))
            self.draw()
        else:
            self.curves[index] = curve
            print "--------"
            for i in range(0, len(self.curves)):
                self.curves[i] = self._render_curve(self.curves[i])
            self.draw()

    def add_curve(self, curve):
        self.curves.append(self._render_curve(curve, add_curve = True))
        self.draw()

    def _render_curve(self, curve, add_curve = False):
        if curve.draggable: curve.disconnect_draggable()
        if isinstance(curve, TransformedCurve): curve = curve.original()

        xscale = Track.xscale(curve, self.original_curves(), add_curve)
        xoffset = Track.xoffset(curve, self.original_curves(), add_curve)
        if add_curve:
            print "xmin %s for %s" % (Track.xmin(self.original_curves() + [curve]),
                                      curve.curve_name)
        else:
            print "xmin %s for %s" % (Track.xmin(self.original_curves()),
                                      curve.curve_name)
                                      
        print "xscale %s for %s" % (xscale, curve.curve_name)
        print "xoffset %s for %s" % (xoffset, curve.curve_name)

        curve = curve.transform(xscale = xscale, xoffset = xoffset)
        self.axes.add_line(curve)
        self.axes.autoscale_view(scaley=False)
        curve.connect_draggable()
        return curve

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

    def first_curve(self):
        return len(self.curves) == 0

    def original_curves(self):
        return Track.originals(self.curves)

    @staticmethod
    def xrange(curves):        
        return max([c.xrange() for c in curves])

    @staticmethod
    def xmin(curves):
        return min([c.xmin() for c in curves])

    @staticmethod
    def xmax(curves):
        return max([c.xmax() for c in curves])

    @staticmethod
    def xscale(curve, curves, add_curve = False):
        if add_curve:        
            curves = curves + [curve]
        return Track.xrange(curves) / curve.xrange()
    
    @staticmethod
    def xoffset(curve, curves, add_curve = False):
        if add_curve:
            curves = curves + [curve]
        return (Track.xmax(curves) - curve.xmax()) / 2.0

    @staticmethod
    def originals(curves):
        acc = []
        for curve in curves:
            if isinstance(curve, TransformedCurve):
                acc.append(curve.original())
            else:
                acc.append(curve)
        return acc

class TrackButtonPanel(QWidget):
    def __init__(self, track_window):
        QWidget.__init__(self, track_window)
        minimum_size_policy(self)
        self.track_window = track_window
        self.curve_boxes = []
        self.curve_boxes.append(QComboBox(self))
        self.panel_layout = QVBoxLayout(self)
        self.panel_layout.addWidget(self.curve_boxes[0])
        self.connect(self.curve_boxes[0], 
                     SIGNAL("currentIndexChanged(QString)"),
                     lambda name: self.track_window.change_curve(name, 0))
        
        self.curve_boxes[0].addItems(self.track_window.curves())

    def update_curves(self, curves):
        for cb in self.curve_boxes:
            cb.clear()
            cb.addItems(curves)

    def add_curve_box(self, curve_name):
        curve_box = QComboBox(self)
        curve_box.addItems(self.track_window.pos_curves)
        curve_box.setCurrentIndex(self.track_window.pos_curves.index(curve_name))
        self.curve_boxes.append(curve_box)
        self.panel_layout.addWidget(curve_box)
        self.connect(self.curve_boxes[-1],
                     SIGNAL("currentIndexChanged(QString)"),
                     lambda name: self.track_window.change_curve(name, len(self.curve_boxes) - 1))
    
    def remove_curve_box(self):
        right_most = self.curve_boxes[-1]
        right_most.hide()
        self.panel_layout.removeWidget(right_most)
        self.curve_boxes = self.curve_boxes[:-1]


class TrackWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        fixed_size_policy(self)

        self.increment = 0        
        self.pos_curves = ["None"]
        self.las_file = None
        self.draggable_line = None

        self.track = Track(self, width=4, height=6)        
        self.button_panel = TrackButtonPanel(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.button_panel)
        layout.addWidget(self.track)
        self.updateGeometry()
        
    def las_update(self, las_file):
        if not las_file == None:
            self.las_file = las_file
            self.pos_curves = self.las_file.curve_header.mnemonics()
            self.button_panel.update_curves(self.pos_curves)

        self.repaint()

    def change_curve(self, curve_name, index):
        if not curve_name == "None":
            try:
                xfield = getattr(self.las_file, str(curve_name + "_field"))
                yfield = self.las_file.depth_field

                curve = Curve(str(curve_name),self.track,xfield,yfield,picker=5)
                curve.set_color(self.track.colors[index])
                curve.set_marker(self.track.markers[index])

                self.track.switch_curve(curve, index)
                self.repaint()
            except AttributeError, e:
                print "Could not change curve: Attribute Error"
                print str(e)

    def add_new_curve(self):
        curve_name = self.track.curves[0].curve_name
        xfield = getattr(self.las_file, str(curve_name + "_field"))
        yfield = self.las_file.depth_field
        
        curve = Curve(str(curve_name), self.track,xfield,yfield,picker=5)
        self.track.colors.append("b")
        self.track.markers.append("None")
        curve.set_color("b")
        curve.set_marker("None")
        self.track.add_curve(curve)
        self.button_panel.add_curve_box(curve_name)
        self.repaint()

    def set_increment(self, increment):
        self.track.set_increment(increment)

    def change_color(self, color, index):
        self.track.colors[index] = color
        self.curves()[index].set_color(color)
        self.track.draw()

    def change_marker(self, marker, index):
        self.track.markers[index] = marker
        self.curves()[index].set_marker(marker)
        self.track.draw()

    def contextMenuEvent(self, event):
        self.curves_context_menu = CurvesContextMenu(self)
        self.curves_context_menu.popup(event.globalPos())

    def curves(self):
        return self.track.curves

class TracksPanel(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self,parent)
        minimum_size_policy(self)
        self.track_windows = []
        self.tracks_layout = QHBoxLayout(self)
        self.las_file = None
        self.increment = 0
        
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
        if self.las_file:
            tw.las_update(self.las_file)
        self.add_track_window(tw)

    def send_to_tracks(self, las_file):
        self.las_file = las_file
        each(self.track_windows, lambda t: t.las_update(las_file))

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
