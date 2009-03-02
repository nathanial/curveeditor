from las.file import *
from gui.plots import *
from gui.gutil import *
from PyQt4.QtCore import QRectF, Qt, QSize
from PyQt4.QtGui import QApplication, QMainWindow, QLabel,\
    QPixmap, QWidget, QPainter, QVBoxLayout, QGridLayout, QListView, \
    QStandardItem, QStandardItemModel, QIcon, QAbstractItemView

ICON_WIDTH=64
ICON_HEIGHT=64
CAPTION_LENGTH = 6
LINE_WIDTH = 4

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

class CurvePanel(QListView):
    def __init__(self, curve_source):
        QListView.__init__(self)
        self.curve_source = curve_source
        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(64,64))
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setWrapping(True)
        self.show()

    def add_curves_from_source(self):
        for curve in self.curve_source._curves:
            self.add_curve(curve)
            self.doItemsLayout()
            QApplication.processEvents()

    def edit(self, index, trigger, event):
        if trigger == QAbstractItemView.DoubleClicked:
            item = self.model.item(index.row())
            curve = item.curve
            print curve.name()
            return True
        else:
            return False

    def add_new_curve(self):
        pass
    
    def add_curve(self, curve):
        name = curve.name()
        plot = self._create_plot(name)
        item = PlotItem(plot)
        item.curve = curve
        self.model.appendRow(item)

    def _create_plot(self, xcurve_name):
        index = self.curve_source.index()
        return Plot.of(xcurve_name, index.name()).from_(self.curve_source)
