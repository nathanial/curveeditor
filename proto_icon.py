from las.file import *
from gui.plots import *
from gui.gutil import *
from PyQt4.QtGui import QApplication, QMainWindow, QLabel,\
    QPixmap, QWidget, QPainter, QVBoxLayout
from PyQt4.QtCore import QRectF, Qt, QSize

ICON_WIDTH=64
ICON_HEIGHT=64

class PngWidget(QWidget):
    def __init__(self, pngfile, parent = None):
        QWidget.__init__(self, parent)
        self.pixmap = QPixmap(pngfile).scaled(ICON_WIDTH,ICON_HEIGHT)
        self.setFixedHeight(ICON_HEIGHT)
        self.setFixedWidth(ICON_WIDTH)
    
    def paintEvent(self, event):
        target = QRectF(0.,0., ICON_WIDTH, ICON_HEIGHT)
        source = QRectF(0.,0., ICON_WIDTH, ICON_HEIGHT)
        painter = QPainter(self)
        painter.drawPixmap(target, self.pixmap, source)

    def sizeHint(self):
        return QSize(ICON_WIDTH,ICON_HEIGHT)

class IconWidget(QWidget):
    def __init__(self, caption, pngfile, parent = None):
        QWidget.__init__(self, parent)
        self.setFixedWidth(ICON_WIDTH)
        self.setFixedHeight(ICON_HEIGHT + 36)
        self.png_widget = PngWidget(pngfile, self)
        self.label = QLabel(caption, self)
        self.label.setFixedWidth(ICON_WIDTH)
        self.label.setAlignment(Qt.AlignHCenter)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.png_widget)
        self.layout.addWidget(self.label)

    def sizeHint(self):
        return QSize(ICON_WIDTH,ICON_HEIGHT + 36)


class PlotIcon(QWidget):
    def __init__(self, plot, parent = None):
        QWidget.__init__(self, parent)
        plot_canvas = PlotCanvas(ymin=plot.ymin(),
                                 ymax=plot.ymax(),
                                 yinc=100)
        plot_canvas.add_plot(plot)
        filename = plot.name() + ".png"
        plot_canvas.fig.savefig(filename)
        plot_canvas.remove_plot(plot)
        self.icon_widget = IconWidget(plot.name(), filename, self)

    def sizeHint(self):
        return self.icon_widget.sizeHint()
    


class IconPanel(QWidget):
    def __init__(self, icons, parent = None):
        QWidget.__init__(self, parent)
        self.layout = QHBoxLayout(self)
        for icon in icons:
            self.layout.addWidget(icon)
            icon.setParent(self)
        self.layout.invalidate()
        self.updateGeometry()
        self.adjustSize()

app = QApplication([])
main_window = QMainWindow()

test_las = LasFile.from_("test.las")
plots = [Plot.of(curve, "dept").from_(test_las) for curve in test_las.available_curves()]
for plot in plots:
    plot.set_linewidth(4)
icons = [PlotIcon(plot) for plot in plots]
icon_panel = IconPanel(icons, main_window)
                 
main_window.setCentralWidget(icon_panel)
main_window.show()
main_window.updateGeometry()
main_window.adjustSize()
app.exec_()
