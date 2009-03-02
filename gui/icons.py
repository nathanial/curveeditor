from las.file import *
from gui.plots import *
from gui.gutil import *
from PyQt4.QtGui import QApplication, QMainWindow, QLabel,\
    QPixmap, QWidget, QPainter, QVBoxLayout, QGridLayout
from PyQt4.QtCore import QRectF, Qt, QSize

ICON_WIDTH=64
ICON_HEIGHT=64
CAPTION_LENGTH = 6
LINE_WIDTH = 4

class Icon(QWidget):
    def __init__(self, file, parent = None):
        QWidget.__init__(self,parent)
        self.pixmap = QPixmap(file).scaled(ICON_WIDTH, ICON_HEIGHT)
        self.setFixedHeight(ICON_HEIGHT)
        self.setFixedWidth(ICON_WIDTH)
        
    def paintEvent(self, event):
        target = QRectF(0.,0., ICON_WIDTH, ICON_HEIGHT)
        source = QRectF(0.,0., ICON_WIDTH, ICON_HEIGHT)
        painter = QPainter(self)
        painter.drawPixmap(target, self.pixmap, source)
        
    def sizeHint(self):
        return QSize(ICON_WIDTH, ICON_HEIGHT)

    
class CaptionedIcon(QWidget):
    def __init__(self, caption, icon, parent = None):
        QWidget.__init__(self, parent)
        self.caption = self._elide_caption(caption)
        self.total_height = ICON_HEIGHT + 36
        self.setFixedWidth(ICON_WIDTH)
        self.setFixedHeight(self.total_height)
        self.icon = icon
        self.icon.setParent(self)
        self.label = QLabel(self.caption, self)
        self.label.setFixedWidth(ICON_WIDTH)
        self.label.setAlignment(Qt.AlignHCenter)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.icon)
        self.layout.addWidget(self.label)

    def sizeHint(self):
        return QSize(ICON_WIDTH, self.total_height)

    def _elide_caption(self, caption):
        if len(caption) > CAPTION_LENGTH:
            ncap = caption[:CAPTION_LENGTH]
            ncap += "..."
            return ncap
        else:
            return caption
            

class PlotIcon(QWidget):
    def __init__(self, plot, parent = None):
        QWidget.__init__(self, parent)
        plot_canvas = PlotCanvas(ymin=plot.ymin(),
                                 ymax=plot.ymax(),
                                 yinc=(plot.ymax() - plot.ymin()))
        plot_canvas.add_plot(plot)
        filename = plot.name() + ".png"
        plot_canvas.fig.savefig(filename)
        plot_canvas.remove_plot(plot)
        self.icon = CaptionedIcon(plot.name(), Icon(filename), self) 

    def sizeHint(self):
        return self.icon.sizeHint()

class CurvePanel(QWidget):
    COLUMNS = 4
    
    def __init__(self, curve_source, parent = None):
        QWidget.__init__(self, parent)
        self.layout = QGridLayout(self)
        self.curve_icons = {}
        self.curve_source = curve_source
        for curve in curve_source._curves:
            self.add_curve(curve)

    def add_new_curve(self):
        pass

    def add_curve(self, curve):
        print "curve = %s " % curve
        print "name = %s " % curve.name()
        name = curve.name()
        plot = self._create_plot(name)
        plot.set_linewidth(LINE_WIDTH)
        icon = PlotIcon(plot, self)
        self.layout.addWidget(icon, self._row(), self._column())
        self.curve_icons[curve] = icon
        self.updateGeometry()
        self.adjustSize()
    
    def remove_curve(self, curve):
        icon = self.curve_icons[curve]
        icon.hide()
        self.layout.removeWidget(icon)
        del self.curve_icons[curve]
        self.updateGeometry()
        self.adjustSize()

    def _create_plot(self, xcurve_name):
        index = self.curve_source.index()
        return Plot.of(xcurve_name, index.name()).from_(self.curve_source)

    def _row(self):
        return len(self.curve_icons) / CurvePanel.COLUMNS

    def _column(self):
        return len(self.curve_icons) % CurvePanel.COLUMNS
