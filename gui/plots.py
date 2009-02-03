import sys, os, random
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QWidget, QVBoxLayout, QComboBox
from PyQt4.QtCore import SIGNAL
from numpy import arange, sin, pi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
            

class Plot(FigureCanvas):
    def __init__(self, parent = None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def plot(self, *args, **kwargs):
        ret = self.axes.plot(*args, **kwargs)
        self.draw()
        return ret

class LasFileLineChangeListener:
    def __init__(self, xfield, yfield):
        self.xfield = xfield
        self.yfield = yfield
        
    def receive_line_change(self, xs, ys):
        for idx in range(0, len(xs)):
            self.xfield.set_at(idx,xs[idx])
        for idx in range(0, len(ys)):
            self.yfield.set_at(idx,ys[idx])

class PlotWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        QWidget.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        QWidget.updateGeometry(self)

        self.layout = QVBoxLayout(self)
        self.curves = ["None"]
        self.las_file = None
        self.curve_line = None

        self.plot = Plot(self, width=4, height=8)        
        self.curve_box = QComboBox(self)
        self.curve_box.addItems(self.curves)
        self.connect(self.curve_box, 
                     SIGNAL("currentIndexChanged(QString)"),
                     self.change_curve)

        self.layout.addWidget(self.curve_box)
        self.layout.addWidget(self.plot)
        
        
    def las_update(self):
        if not self.las_file == None:
            self.curves = self.las_file.curve_header.descriptor_mnemonics()
            self.curve_box.clear()
            self.curve_box.addItems(self.curves)
        
        self.repaint()

    def change_curve(self, curve_name):
        if not curve_name == "None":
            try:
                xfield = getattr(self.las_file, str(curve_name + "_field"))
                yfield = self.las_file.depth_field
                line, = self.plot.plot(xfield.to_list(),yfield.to_list(),
                                       "b-", picker=5)
                listener = LasFileLineChangeListener(xfield, yfield)
                                                     
                self.curve_line = DraggableLine(line, [listener])
                self.curve_line.connect()
                self.repaint()
            except AttributeError:
                line, = self.plot.plot([], [])
                self.curve_line = DraggableLine(line)
                self.curve_line.connect()
        else:
            line, = self.plot.plot([],[])
            self.curve_line = DraggableLine(line)
            self.curve_line.connect()

    
                       
        
        
        
        
