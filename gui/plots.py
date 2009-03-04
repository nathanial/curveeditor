from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QMenu, QWidget, QApplication, QHBoxLayout, QComboBox, QLabel, \
    QStandardItem, QStandardItemModel, QIcon, QPixmap
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure, SubplotParams
from matplotlib.lines import Line2D

from gui.gutil import minimum_size_policy, fixed_size_policy
from las.file import transform
from util import *

ICON_WIDTH=64
ICON_HEIGHT=64
CAPTION_LENGTH = 6
LINE_WIDTH = 4

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
        self.change_callbacks = []
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
        self.modify_xdata(ind, event.xdata)
        self.update_animation()
        self.notify_change(ind)

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
    
    def add_change_callback(self, cc):
        self.change_callbacks.append(cc)
    
    def remove_change_listener(self, cc):
        self.change_callbacks.remove(cc)

    def notify_change(self, idx):
        for cc in self.change_callbacks:
            cc(self, idx)

    def modify_xdata(self, ind, new_xdata):
        self.current_xfield[ind] = new_xdata
        self.set_xdata(self.current_xfield.to_list())

class PlotBuilder(object):
    def __init__(self, xcurve_name, ycurve_name):
        self.xcurve_name = xcurve_name
        self.ycurve_name = ycurve_name

    def from_(self, curve_source):
        xcurve,ycurve = curve_source.curves(
            self.xcurve_name,self.ycurve_name)
        return Plot(xcurve, ycurve)

class PlotInfo(QWidget):
    def __init__(self, plot, available_curves, info_panel):
        QWidget.__init__(self, info_panel)
        self.plot = plot
        self.info_panel = info_panel
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

    def my_connect(self):
        QWidget.connect(self.curve_box, 
                        SIGNAL("currentIndexChanged(int)"),
                        self.change_plot)
        self.info_panel.layout.addWidget(self)

    def my_disconnect(self):
        self.hide()
        QWidget.disconnect(self.curve_box,
                           SIGNAL("currentIndexChanged(int)"),
                           self.change_plot)
        self.info_panel.layout.removeWidget(self)

    def change_plot(self, index):
        name = self.curve_names[index]
        self.emit(SIGNAL("change_plot"), name)

    def switch_plot(self, plot):
        self.plot = plot
        self.xmax_label.setText(str(plot.xmax()))
        self.xmin_label.setText(str(plot.xmin()))

class PlotCanvas(FigureCanvas):
    def __init__(self, ymin, ymax, yinc, parent = None, width=5, height=4, dpi=100):
        #params control border sizes
        params = SubplotParams(left=.02, right=.98, top=.99, bottom=.01)
        self.fig = Figure(figsize=(width,height), dpi=dpi,
                          subplotpars=params)                
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.plots = []
        self.increment = 0
        self.animation_engaged = False
        self.ymax = ymax
        self.ymin = ymin
        self.yinc = yinc
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        minimum_size_policy(self)

    def swap_plot(self, old, new):
        old.disconnect_draggable()
        self._insert_plot(new, lambda: swap(self.plots, old, new))

    def add_plot(self, plot):
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
        self._render_plots()
        self._reset_ylim()
        self.draw()

    def _render_plots(self):
        each(self.plots, self._render_plot)
        self.axes.set_xticks([])
        self.axes.set_yticks([])

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
        self.axes.set_ylim(self.ymin + self._percentage_increment(),
                           self.ymin + self.yinc + self._percentage_increment())
        if self.animation_engaged:
            self.update_animation()
        else:
            self.draw()

    def _percentage_increment(self):
        return (self.increment / 100.0) * self.yrange()

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
        xrange = plot.xrange()
        if xrange:
            return PlotCanvas.xrange(plots) / xrange
        else:
            return 0
    
    @staticmethod
    def xoffset(plot, plots):
        return (PlotCanvas.xmax(plots) - plot.xmax()) / 2.0        


    def yrange(self):
        return self.ymax - self.ymin

        
class PlotAndInfo(object):
    def __init__(self, xcurve_name, curve_source, plot_canvas, info_panel):
        self.xcurve_name = xcurve_name
        self.curve_source = curve_source
        self.plot_canvas = plot_canvas
        self.info_panel = info_panel
        self.plot = Plot.of(xcurve_name, 
                            curve_source.index_name()).from_(curve_source)

    def my_connect(self):
        self.plot_info = PlotInfo(self.plot,
                                  self.curve_source.available_curves(),
                                  self.info_panel)
        self.plot_info.my_connect()
        self.plot_canvas.add_plot(self.plot)
        QWidget.connect(self.plot_info,
                        SIGNAL("change_plot"),
                        self.change_plot)
            
    def my_disconnect(self):
        self.plot_info.my_disconnect()
        self.plot_canvas.remove_plot(self.plot)
        QWidget.disconnect(self.plot_info,
                           SIGNAL("change_plot"),
                           self.change_plot)

    def reindex(self):
        new_plot = self._new_plot(self.plot.original_xfield.name())
        self.plot_canvas.swap_plot(self.plot, new_plot)
        self.plot_info.switch_plot(new_plot)
        self.plot = new_plot

    def change_plot(self, name):
        self.xcurve_name = name
        new_plot = self._new_plot(name)
        self.plot_canvas.swap_plot(self.plot, new_plot)
        self.plot_info.switch_plot(new_plot)
        self.plot = new_plot

    def _new_plot(self, name):
        iname = self.curve_source.index_name()
        nplot = Plot.of(name,iname).from_(self.curve_source)
        nplot.set_color(self.plot.color)
        nplot.set_marker(self.plot.marker)
        return nplot
        
        
        
        
        
        
        
class PlotItem(QStandardItem):
    def __init__(self, plot):
        icon = self._create_icon(plot)
        QStandardItem.__init__(self, icon, plot.name())
        self.icon = icon
        self.plot = plot

    def _create_icon(self, plot):
        plot_canvas = PlotCanvas(ymin=plot.ymin(),
                                  ymax=plot.ymax(),
                                  yinc=(plot.ymax() - plot.ymin()))
        plot_canvas.add_plot(plot)
        filename = "tmp/" + plot.name() + ".png"
        plot_canvas.fig.savefig(filename)
        plot_canvas.remove_plot(plot)
        return QIcon(QPixmap(filename))

class PlotItemModel(QStandardItemModel):
    def mimeData(self, indexes):
        assert len(indexes) == 1
        index = indexes[0]
        item = self.item(index.row())
        plot = item.plot
        mdata = QStandardItemModel.mimeData(self, indexes)
        mdata.xcurve = plot.original_xfield
        mdata.ycurve = plot.original_yfield
        return mdata

    def dropMimeData(self, mime_data, action, row, column, parent):
        plot = Plot(mime_data.xcurve, mime_data.ycurve)
        item = PlotItem(plot)
        self.appendRow(item)
        return True
