from las.file import LasCurve, transform
from matplotlib.lines import Line2D
from PyQt4 import QtGui, QtCore
from gui.main import registry
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout, QPushButton,\
    QDialog, QRadioButton, QLabel
from gui.gutil import minimum_size_policy, fixed_size_policy

class Plot(Line2D):
    def __init__(self,curve_name, canvas, xfield = None, yfield = None, *args, **kwargs):
        self.curve_name = curve_name
        self.canvas = canvas
        self.xfield = xfield
        self.yfield = yfield
        self._args = args
        self._kwargs = kwargs
        self.press = None
        self.draggable = False
        self.color = "b"
        self.marker = "None"
        Line2D.__init__(self, xfield.to_list(), yfield.to_list(), *args, **kwargs)

    def connect_draggable(self):
        self.cidpress = self.canvas.mpl_connect(
            'button_press_event', self.drag_on_press)
        self.cidrelease = self.canvas.mpl_connect(
            'button_release_event', self.drag_on_release)
        self.cidmotion = self.canvas.mpl_connect(
            'motion_notify_event', self.drag_on_motion)
        self.draggable = True
        
    def drag_on_press(self, event):
        contains,attrd = self.contains(event)
        if not contains: return
        self.press = attrd['ind']

    def drag_on_motion(self, event):
        if self.press is None: return
        ind = self.press
        if len(ind) > 1: ind = ind[0]
        self.xfield[ind] = event.xdata
        self.set_xdata(self.xfield.to_list())
        self.canvas.draw()

    def drag_on_release(self, event):
        self.press = None
        self.canvas.draw()

    def disconnect_draggable(self):
        self.canvas.mpl_disconnect(self.cidpress)
        self.canvas.mpl_disconnect(self.cidrelease)
        self.canvas.mpl_disconnect(self.cidmotion)
        self.draggable = False

    def transform(self,xscale = 1.0, yscale = 1.0, xoffset = 0, yoffset = 0):
        plot = TransformedPlot(self.curve_name,
                               self.canvas,
                               self.xfield, xscale, xoffset,
                               self.yfield, yscale, yoffset,
                               *self._args, **self._kwargs)
        plot.set_color(self.color)
        plot.set_marker(self.marker)
        return plot

    def untransform(self):
        return self
                     
    def yrange(self):
        return self.ymax() - self.ymin()

    def ymin(self):
        return min(self.yfield.to_list())

    def ymax(self):
        return max(self.yfield.to_list())

    def xrange(self):
        return self.xmax() - self.xmin()

    def xmax(self):
        return max(self.xfield.to_list())
    
    def xmin(self):
        return min(self.xfield.to_list())

    def set_color(self, color):
        self.color = color
        return Line2D.set_color(self, color)
    
    def set_marker(self, marker):
        self.marker = marker
        return Line2D.set_marker(self, marker)

class TransformedPlot(Plot):
    def __init__(self, curve_name, canvas, 
                 xfield, xscale, xoffset, 
                 yfield, yscale, yoffset, 
                 *args, **kwargs):
        self.original_xfield = xfield
        self.original_yfield = yfield
        Plot.__init__(self, curve_name, canvas,
                       transform(xfield, xscale, xoffset),
                       transform(yfield, yscale, yoffset),
                       *args, **kwargs)

    def transform(self, xscale = 1.0, yscale = 1.0, xoffset = 0, yoffset = 0):
        curve = TransformedPlot(self.curve_name, 
                                self.canvas,
                                self.original_xfield, xscale, xoffset,
                                self.original_yfield, yscale, yoffset,
                                *self._args, **self._kwargs)
        curve.set_color(self.color)
        curve.set_marker(self.marker)
        return curve

    def untransform(self):
        curve = Plot(self.curve_name,
                     self.canvas,
                     self.original_xfield, 
                     self.original_yfield,
                     *self._args, **self._kwargs)
        curve.set_color(self.color)
        curve.set_marker(self.marker)
        return curve

class PlotInfo(QWidget):
    def __init__(self, plot, button_panel):
        QWidget.__init__(self, button_panel)
        self.plot = plot
        self.button_panel = button_panel
        minimum_size_policy(self)
        self.curve_box = QComboBox(self)

        curve_names = registry.lasfile.curve_mnemonics()
        index = curve_names.index(plot.curve_name)

        self.curve_box.addItems(curve_names)
        self.curve_box.setCurrentIndex(index)
        QWidget.connect(self.curve_box, 
                        SIGNAL("currentIndexChanged(int)"),
                        self.changed_curve)

        self.xmax_label = QLabel(str(plot.xmax()), self)
        self.xmin_label = QLabel(str(plot.xmin()), self)
        
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.xmin_label)
        self.layout.addWidget(self.curve_box)
        self.layout.addWidget(self.xmax_label)

        
    def changed_curve(self, index):
        x = registry.lasfile.lascurves[index]
        y = registry.get_curve("depth")
        old_plot = self.plot
        new_plot = Plot(x.mnemonic, self.track, x, y, picker=5)
        self.track.switch_plot(old_plot, new_plot)
        self.plot = new_plot        
