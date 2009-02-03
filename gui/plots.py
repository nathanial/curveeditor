import sys, os, random
from PyQt4 import QtGui, QtCore
from numpy import arange, sin, pi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DraggableLine(object):
    def __init__(self, line, canvas):
        self.line = line
        self.press = None
        self.canvas = canvas

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

        oxs = self.line.get_xdata()
        oys = self.line.get_ydata()
        oxs[ind] = event.xdata
        oys[ind] = event.ydata
        self.line.set_xdata(oxs)
        self.line.set_ydata(oys)
        self.line.figure.canvas.draw()

    def on_release(self, event):
        self.press = None
        self.line.figure.canvas.draw()

    def disconnect(self):
        self.canvas.mpl_disconnect(self.cidpress)
        self.canvas.mpl_disconnect(self.cidrelease)
        self.canvas.mpl_disconnect(self.cidmotion)

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


#class MyStaticMplCanvas(MyMplCanvas):
#    def compute_initial_self.figure(self):
#        t = arange(0.0, 3.0, 0.01)
#        s = sin(2*pi*t)
#        self.axes.plot(t,s)
#
#class MyDynamicMplCanvas(MyMplCanvas):
#    def __init__(self, *args, **kwargs):
#        MyMplCanvas.__init__(self, *args, **kwargs)
#        timer = QtCore.QTimer(self)
#        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_self.figure)
#        timer.start(1000)
#
#    def compute_initial_self.figure(self):
#        self.axes.plot([0,1,2,3],[1,2,0,4], 'r')
#        
#    def update_self.figure(self):
#        l = [random.randint(0,10) for i in xrange(4)]
#        self.axes.plot([0,1,2,3], l, 'r')
#        self.draw()
