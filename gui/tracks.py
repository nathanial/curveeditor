import sys, os, random
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout
from PyQt4.QtCore import SIGNAL, QSize
from numpy import arange, sin, pi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from util import times, each
from gui.gutil import minimum_size_policy, fixed_size_policy

class DraggableLine(object):
    def __init__(self, line, line_change_listeners = []):
        self.line = line
        self.press = None
        self.canvas = self.line.figure.canvas
        self.line_change_listeners = line_change_listeners

    def connect(self):
        self.cidpress = self.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        contains,attrd = self.line.contains(event)
        if not contains: return
        self.press = attrd['ind']

    def on_motion(self, event):
        if self.press is None: return
        ind = self.press

        xs = self.line.get_xdata()
        ys = self.line.get_ydata()
        xs[ind] = event.xdata
        ys[ind] = event.ydata
       
        self.line.set_xdata(xs)
        self.line.set_ydata(ys)
        self.canvas.draw()
        self.publish_line_change(xs, ys)

    def on_release(self, event):
        self.press = None
        self.canvas.draw()

    def disconnect(self):
        self.canvas.mpl_disconnect(self.cidpress)
        self.canvas.mpl_disconnect(self.cidrelease)
        self.canvas.mpl_disconnect(self.cidmotion)

    def publish_line_change(self, xs, ys):
        for listener in self.line_change_listeners:
            listener.receive_line_change(xs,ys)
            

class Track(FigureCanvas):
    def __init__(self, parent = None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        fixed_size_policy(self)

    def plot(self, *args, **kwargs):
        ret = self.axes.plot(*args, **kwargs)
        self.draw()
        return ret

class LasFileLineChangeListener:
    def __init__(self, xfield, yfield):
        self.xfield = xfield
        self.yfield = yfield
        
    def receive_line_change(self, xs, ys):
        def setx(i): self.xfield[i] = xs[i]
        def sety(i): self.yfield[i] = ys[i]
        times(len(xs), setx)
        times(len(ys), sety)

class TrackWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        fixed_size_policy(self)

        self.increment = 0        
        self.ymin = 0
        self.yrange = 0
        self.curves = ["None"]
        self.las_file = None
        self.curve_line = None

        self.track = Track(self, width=4, height=8)        

        self.curve_box = QComboBox(self)
        minimum_size_policy(self.curve_box)
        self.curve_box.addItems(self.curves)
        self.connect(self.curve_box, 
                     SIGNAL("currentIndexChanged(QString)"),
                     self.change_curve)

        layout = QVBoxLayout(self)
        layout.addWidget(self.curve_box)
        layout.addWidget(self.track)
        self.updateGeometry()
        
    def las_update(self, las_file):
        if not las_file == None:
            self.las_file = las_file
            self.curves = self.las_file.curve_header.mnemonics()
            self.curve_box.clear()
            self.curve_box.addItems(self.curves)

        self.repaint()

    def change_curve(self, curve_name):
        if not curve_name == "None":
            try:
                xfield = getattr(self.las_file, str(curve_name + "_field"))
                yfield = self.las_file.depth_field
                xs = xfield.to_list()
                ys = yfield.to_list()
                line, = self.track.plot(xs,ys,"b-", picker=5, scaley=False)
                self.ymin = min(ys)
                self.yrange = max(ys) - self.ymin
                print "yrange = %s " % self.yrange
                self.track.axes.set_ylim(self.ymin + self._percentage_increment(), 
                                         self.ymin + 100 + self._percentage_increment())
                listener = LasFileLineChangeListener(xfield, yfield)
                                                     
                self.curve_line = DraggableLine(line, [listener])
                self.curve_line.connect()                
                self.repaint()
            except AttributeError:
                line, = self.track.plot([], [])
                self.curve_line = DraggableLine(line)
                self.curve_line.connect()
        else:
            line, = self.track.plot([],[])
            self.curve_line = DraggableLine(line)
            self.curve_line.connect()

    def set_increment(self, increment):
        self.increment = increment
        self.track.axes.set_ylim(self.ymin + self._percentage_increment(),
                                 self.ymin + 100 + self._percentage_increment())
        self.track.draw()

    def _percentage_increment(self):
        return ((self.increment + 1) / 100.0) * self.yrange

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
        each(self.track_windows, lambda tw: tw.set_increment(increment))
