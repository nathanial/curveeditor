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
        self.increment = 0
        self.xs = []
        self.ys = []

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        fixed_size_policy(self)

    def plot(self, xs, ys, *args, **kwargs):
        self.xs = xs
        self.ys = ys
        ret = self.axes.plot(xs, ys, *args, **kwargs)
        if not ys == []:
            self.ymin = min(ys)
            self.yrange = max(ys) - self.ymin
        else:
            self.ymin = 0
            self.yrange = 0
        self._reset_ylim()
        self.draw()
        return ret

    def set_increment(self, increment):
        self.increment = increment
        self._reset_ylim()
        self.draw()

    def _reset_ylim(self):
        self.axes.set_ylim(self.ymin + self._percentage_increment(),
                           self.ymin + 100 + self._percentage_increment())

    def _percentage_increment(self):
        return ((self.increment + 1) / 100.0) * self.yrange

class LasFileLineChangeListener:
    def __init__(self, xfield, yfield):
        self.xfield = xfield
        self.yfield = yfield
        
    def receive_line_change(self, xs, ys):
        def setx(i): self.xfield[i] = xs[i]
        def sety(i): self.yfield[i] = ys[i]
        times(len(xs), setx)
        times(len(ys), sety)

class TrackPropertiesDialog(QDialog):
    def __init__(self, parent, track_window):
        QDialog.__init__(self, parent)
        self.track_window = track_window
        self.dialog_layout = QHBoxLayout(self)
        self.setup_color_panel()

    def setup_color_panel(self):
        self.color_panel = QWidget(self)
        self.dialog_layout.addWidget(self.color_panel)
        layout = QVBoxLayout(self.color_panel)
        self.red = QRadioButton("red", self.color_panel)
        self.blue = QRadioButton("blue", self.color_panel)
        self.green = QRadioButton("green", self.color_panel)
        each([self.red,self.blue,self.green], lambda c: layout.addWidget(c))
        self.connect(self.red,
                     SIGNAL("clicked()"),
                     lambda: self.track_window.change_color("r"))
        self.connect(self.blue,
                     SIGNAL("clicked()"),
                     lambda: self.track_window.change_color("b"))
        self.connect(self.green,
                     SIGNAL("clicked()"),
                     lambda: self.track_window.change_color("g"))
        self.updateGeometry()
        self.adjustSize()


class TrackButtonPanel(QWidget):
    def __init__(self, track_window):
        QWidget.__init__(self, track_window)
        minimum_size_policy(self)
        self.track_window = track_window
        self.curve_box = QComboBox(self)
        self.properties_button = QPushButton("Properties",self)
        layout = QHBoxLayout(self)
        layout.addWidget(self.curve_box)
        layout.addWidget(self.properties_button)

        self.connect(self.curve_box, 
                     SIGNAL("currentIndexChanged(QString)"),
                     self.track_window.change_curve)
        self.connect(self.properties_button,
                     SIGNAL("clicked()"),
                     self.show_properties_dialog)
                     

        self.curve_box.addItems(self.track_window.curves)

    def update_curves(self, curves):
        self.curve_box.clear()
        self.curve_box.addItems(curves)

    def show_properties_dialog(self):
        properties_dialog = TrackPropertiesDialog(self, self.track_window)
        properties_dialog.exec_()

class TrackWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        fixed_size_policy(self)

        self.color = "b"
        self.increment = 0        
        self.curves = ["None"]
        self.las_file = None
        self.curve_line = None
        self.draggable_line = None

        self.track = Track(self, width=4, height=8)        
        self.button_panel = TrackButtonPanel(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.button_panel)
        layout.addWidget(self.track)
        self.updateGeometry()
        
    def las_update(self, las_file):
        if not las_file == None:
            self.las_file = las_file
            self.curves = self.las_file.curve_header.mnemonics()
            self.button_panel.update_curves(self.curves)

        self.repaint()

    def change_curve(self, curve_name):
        if not curve_name == "None":
            try:
                xfield = getattr(self.las_file, str(curve_name + "_field"))
                yfield = self.las_file.depth_field
                xs = xfield.to_list()
                ys = yfield.to_list()
                self.curve_line, = self.track.plot(xs,ys,self.color + "-", picker=5, scaley=False)
                listener = LasFileLineChangeListener(xfield, yfield)                                                     
                self.draggable_line = DraggableLine(self.curve_line, [listener])
                self.draggable_line.connect()                
                self.repaint()
            except AttributeError:
                self.curve_line, = self.track.plot([], [])
                self.draggable_line = DraggableLine(self.curve_line)
                self.draggable_line.connect()
        else:
            self.curve_line, = self.track.plot([],[])
            self.draggable_line = DraggableLine(self.curve_line)
            self.draggable_line.connect()

    def set_increment(self, increment):
        self.track.set_increment(increment)

    def change_color(self, color):
        self.color = color
        self.curve_line.set_color(color)
        self.track.draw()

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
