from las.file import *
from gui.plots import *
from gui.gutil import *
from gui.tracks import *
from PyQt4.QtCore import QRectF, Qt, QSize, QMimeData
from PyQt4.QtGui import QApplication, QMainWindow, QLabel,\
    QPixmap, QWidget, QPainter, QVBoxLayout, QGridLayout, QListView, \
    QStandardItem, QStandardItemModel, QIcon, QAbstractItemView, \
    QMenu, QMenuBar, QSizePolicy

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

class CurveEditingWindow(QMainWindow):
    def __init__(self, plot, parent = None):
        QMainWindow.__init__(self, parent)
        self.plot = plot
        self.setWindowTitle(self.plot.name())
        self._setup_menu()
        QApplication.processEvents()
        self.editing_panel = CurveEditingPanel(self.plot.original_xfield,
                                               self.plot.original_yfield,
                                               self)
        self.setCentralWidget(self.editing_panel)
        self.updateGeometry()

    def _setup_menu(self):
        self.menuBar().addAction("&Foo")
        

class CurvePanel(QListView):
    def __init__(self, curve_source):
        QListView.__init__(self)
        self.curve_source = curve_source
        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(64,64))
        self.model = PlotItemModel()
        self.setModel(self.model)
        self.setWrapping(True)
        self.setAcceptDrops(True)
        self.show()

    def add_curves_from_source(self):
        for curve in self.curve_source._curves:
            self.add_curve(curve)
            self.doItemsLayout()
            QApplication.processEvents()

    def edit(self, index, trigger, event):
        if trigger == QAbstractItemView.DoubleClicked:
            item = self.model.item(index.row())
            plot = item.plot
            dialog = CurveEditingWindow(plot, self)
            dialog.show()
            return True
        else:
            return False

    def add_new_curve(self):
        pass
    
    def add_curve(self, curve):
        plot = Plot(curve, self.curve_source.index())
        item = PlotItem(plot)
        self.model.appendRow(item)
