from las.file import LasCurve, transform
from matplotlib.lines import Line2D
from PyQt4 import QtGui, QtCore
from gui.main import registry
from PyQt4.QtCore import SIGNAL, QSize
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout, QPushButton,\
    QDialog, QRadioButton, QLabel
from gui.gutil import minimum_size_policy, fixed_size_policy

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
                        *args, **kwargs)

    def name(self):
        return self.original_xfield.name()

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
        self.current_xfield[ind] = event.xdata
        self.set_xdata(self.current_xfield.to_list())
        self.canvas.draw()

    def drag_on_release(self, event):
        self.press = None
        self.canvas.draw()

    def disconnect_draggable(self):
        self.canvas.mpl_disconnect(self.cidpress)
        self.canvas.mpl_disconnect(self.cidrelease)
        self.canvas.mpl_disconnect(self.cidmotion)
        self.draggable = False

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

    @staticmethod
    def of(xcurve_name, ycurve_name):
        x = registry.get_curve(xcurve_name)
        y = registry.get_curve(ycurve_name)
        return Plot(x,y)
        

class PlotInfo(QWidget):
    def __init__(self, plot, parent):
        QWidget.__init__(self, parent)
        self.plot = plot
        minimum_size_policy(self)

        self.curve_box = QComboBox(self)
        self.curve_names = registry.lasfile.curve_mnemonics()
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
