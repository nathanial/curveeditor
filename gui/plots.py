from las.file import LasCurve, transform
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL, QSize
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout, QPushButton,\
    QDialog, QRadioButton, QLabel
from gui.gutil import minimum_size_policy, fixed_size_policy
from util import *
import thread

class Plot(Line2D):
    def __init__(self, xfield = None, yfield = None, canvas = None, *args, **kwargs):
        self.canvas = canvas
        self.original_xfield = xfield
        self.original_yfield = yfield
        self.current_xfield = xfield
        self.current_yfield = yfield
        self.press = None
        self.draggable = False
        self.color = "b"
        self.marker = "None"
        self.xscale = 1.0
        self.yscale = 1.0
        self.xoffset = 0
        self.yoffset = 0
        Line2D.__init__(self, 
                        self.current_xfield.to_list(), 
                        self.current_yfield.to_list(),
                        *args,**kwargs)

    def name(self):
        return self.original_xfield.name()

    def scale(self,xscale = 1.0, yscale = 1.0, xoffset = 0, yoffset = 0):
        self.xscale = xscale
        self.yscale = yscale
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.current_xfield = transform(self.original_xfield, xscale, xoffset)
        self.current_yfield = transform(self.original_yfield, yscale, yoffset)
        self.set_xdata(self.current_xfield.to_list())
        self.set_ydata(self.current_yfield.to_list())

    def yrange(self):
        return self.ymax() - self.ymin()

    def ymin(self):
        return min(self.original_yfield.to_list())

    def ymax(self):
        return max(self.original_yfield.to_list())

    def xrange(self):
        return self.xmax() - self.xmin()

    def xmax(self):
        return max(self.original_xfield.to_list())
    
    def xmin(self):
        return min(self.original_xfield.to_list())

    def set_color(self, color):
        self.color = color
        ret = Line2D.set_color(self, color)
        if self.canvas: self.canvas.draw()
        return ret
    
    def set_marker(self, marker):
        self.marker = marker
        ret = Line2D.set_marker(self, marker)
        if self.canvas: self.canvas.draw()
        return ret

    @staticmethod
    def of(xcurve_name, ycurve_name):
        return PlotBuilder(xcurve_name, ycurve_name)

    #Y Methods
    def scaled_yrange(self):
        return self.yscale * self.yrange()

    def offset_ymin(self):
        return self.yoffset + self.ymin()

    def offset_ymax(self):
        return self.yoffset + self.ymax()

    #X Methods
    def scaled_xrange(self):
        return self.xscale * self.xrange()

    def offset_xmin(self):
        return self.xoffset + self.xmin()
    
    def offset_xmax(self):
        return self.xoffset + self.xmax()

    #Dragging methods
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
        self.animation_on()
        self.press = attrd['ind']

    def drag_on_motion(self, event):
        if self.press is None: return
        ind = self.press
        if len(ind) > 1: ind = ind[0]
        self.current_xfield[ind] = event.xdata
        self.set_xdata(self.current_xfield.to_list())
        self.update_animation()

    def drag_on_release(self, event):
        self.press = None
        self.animation_off()

    def disconnect_draggable(self):
        self.canvas.mpl_disconnect(self.cidpress)
        self.canvas.mpl_disconnect(self.cidrelease)
        self.canvas.mpl_disconnect(self.cidmotion)
        self.draggable = False

    #Animation methods
    def animation_on(self):
        canvas = self.canvas
        axes = self.canvas.axes
        self.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(axes.bbox)
        axes.draw_artist(self)
        canvas.blit(axes.bbox)

    def update_animation(self):
        canvas = self.canvas
        axes = canvas.axes
        canvas.restore_region(self.background)
        axes.draw_artist(self)
        canvas.blit(axes.bbox)

    def animation_off(self):
        self.set_animated(False)
        self.background = None
        self.canvas.draw()

class PlotBuilder(object):
    def __init__(self, xcurve_name, ycurve_name):
        self.xcurve_name = xcurve_name
        self.ycurve_name = ycurve_name

    def from_(self, curve_source):
        xcurve,ycurve = curve_source.curves(
            self.xcurve_name,self.ycurve_name)
        return Plot(xcurve, ycurve)

class PlotInfo(QWidget):
    def __init__(self, plot, available_curves, parent):
        QWidget.__init__(self, parent)
        self.plot = plot
        minimum_size_policy(self)

        self.curve_box = QComboBox(self)
        self.curve_names = available_curves
        index = self.curve_names.index(plot.name())

        self.curve_box.addItems(self.curve_names)
        self.curve_box.setCurrentIndex(index)

        self.xmax_label = QLabel(str(plot.xmax()), self)
        self.xmin_label = QLabel(str(plot.xmin()), self)
        
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.xmin_label)
        self.layout.addWidget(self.curve_box)
        self.layout.addWidget(self.xmax_label)

        QWidget.connect(self.curve_box, 
                        SIGNAL("currentIndexChanged(int)"),
                        self.change_curve)

    def change_curve(self, index):
        name = self.curve_names[index]
        self.emit(SIGNAL("change_curve"), self.plot, name)

class PlotCanvas(FigureCanvas):
    def __init__(self, parent = None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)
        self.plots = []
        self.increment = 0
        self.lowest_depth = None
        self.highest_depth = None
        self.animation_engaged = False
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        fixed_size_policy(self)

    def swap_plot(self, old, new):
        old.disconnect_draggable()
        self._insert_plot(new, lambda: swap(self.plots, old, new))

    def add_plot(self, plot):
        if self.first_plot():
            self.lowest_depth = plot.ymin()
            self.highest_depth = plot.ymax()
            self._reset_ylim()
        self._insert_plot(plot, lambda: self.plots.append(plot))

    def remove_plot(self, plot):
        plot.disconnect_draggable()
        plot.canvas = None
        index = self.plots.index(plot)
        del self.plots[index]
        self.axes.clear()
        self._render_plots()
        self.draw()

    def remove_all_plots(self):
        for plot in self.plots:
            self.remove_plot(plot)

    def _insert_plot(self, plot, fn):
        plot.canvas = self
        self.axes.clear()
        fn()
        each(self.plots, self._render_plot)
        self.draw()

    def _render_plots(self):
        each(self.plots, self._render_plot)

    def _render_plot(self, plot):
        xscale = PlotCanvas.xscale(plot, self.plots)
        xoffset = PlotCanvas.xoffset(plot, self.plots)
        plot.scale(xscale = xscale, xoffset = xoffset)
        self.axes.add_line(plot)
        self.axes.autoscale_view(scaley=False)
        if not plot.draggable: plot.connect_draggable()

    def set_increment(self, increment):
        self.increment = increment
        self._reset_ylim()

    def animation_on(self):
        self.animation_engaged = True
        for plot in self.plots:
            plot.set_animated(True)
        self.draw()
        self.animation_background = self.copy_from_bbox(self.axes.bbox)
        for plot in self.plots:
            self.axes.draw_artist(plot)
        self.blit(self.axes.bbox)

    def update_animation(self):
        self.restore_region(self.animation_background)
        for plot in self.plots:
            self.axes.draw_artist(plot)
        self.blit(self.axes.bbox)
    
    def animation_off(self):
        self.animation_engaged = False
        for plot in self.plots:
            plot.set_animated(False)
        self.draw()

    def _reset_ylim(self):
        self.axes.set_ylim(self.lowest_depth + self._percentage_increment(),
                           self.lowest_depth + 100 + self._percentage_increment())
        if self.animation_engaged:
            self.update_animation()
        else:
            self.draw()

    def _percentage_increment(self):
        return ((self.increment + 1) / 100.0) * self.depth_range()

    def depth_range(self):
        return self.highest_depth - self.lowest_depth

    def first_plot(self):
        return len(self.plots) == 0

    def draw(self):
        self.replot = True
        FigureCanvasAgg.draw(self)
        self.update()

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
        return PlotCanvas.xrange(plots) / plot.xrange()
    
    @staticmethod
    def xoffset(plot, plots):
        return (PlotCanvas.xmax(plots) - plot.xmax()) / 2.0        

class PlotsContextMenu(QMenu):
    def __init__(self, track, parent):
        QMenu.__init__(self, parent)
        self.track = track
        plots = track.plots()

        self.addAction('&Add Curve', self.track.add_new_plot)
        for plot in plots:
            self.addMenu(PlotContextMenu(self, plot))

        QApplication.processEvents()
        self.updateGeometry()
        QApplication.processEvents()
        self.adjustSize()
                
class PlotContextMenu(QMenu):
    def __init__(self, parent, plot):
        QMenu.__init__(self, plot.name(), parent)
        color_menu = PlotColorMenu(self,plot)
        marker_menu = PlotMarkerMenu(self,plot)
        self.addMenu(color_menu)
        self.addMenu(marker_menu)
        self.addAction('&Remove', lambda: parent.track.remove_curve(plot))

class PlotColorMenu(QMenu):
    def __init__(self, parent,plot):
        QMenu.__init__(self,"Color", parent)
        self.addAction('&Red', lambda: plot.set_color("r"))
        self.addAction('&Blue', lambda: plot.set_color("b"))
        self.addAction('&Green', lambda: plot.set_color("g"))

class PlotMarkerMenu(QMenu):
    def __init__(self, parent, plot):
        QMenu.__init__(self,"Marker", parent)
        self.addAction('&None', lambda: plot.set_marker("None"))
        self.addAction('&Circle', lambda: plot.set_marker("o"))
        self.addAction('&Triangle', lambda: plot.set_marker("^"))
