from las.file import *
from gui.plots import *
from gui.gutil import *
from gui.tracks import *
from PyQt4.QtCore import QRectF, Qt, QSize, QMimeData
from PyQt4.QtGui import QApplication, QMainWindow, QLabel,\
    QPixmap, QWidget, QPainter, QVBoxLayout, QGridLayout, QListView, \
    QStandardItem, QStandardItemModel, QIcon, QAbstractItemView, \
    QMenu, QMenuBar, QSizePolicy, QToolBar

class CurveEditingPanel(AbstractTrackPanel):
    def __init__(self, curve, index, parent = None):
        AbstractTrackPanel.__init__(self, [], parent)
        self.curve = curve
        self.index = index
        self.changing_depth = False
        self._setup_depth_slider(index.min(), index.max())

        track = SinglePlotTrack(Plot(self.curve, self.index), self)
        self.tracks.append(track)
        self.layout.addWidget(track, 1, Qt.AlignLeft)
        self.updateGeometry()

class CurveEditingWindow(QMainWindow):
    def __init__(self, plot, parent = None):
        QMainWindow.__init__(self, parent)
        self.plot = plot
        self.dirty = False
        self.setWindowTitle(self.plot.name())
        self._setup_menu()
        QApplication.processEvents()
        self.editing_panel = CurveEditingPanel(self.plot.original_xfield,
                                               self.plot.original_yfield,
                                               self)
        self.setCentralWidget(self.editing_panel)
        self.updateGeometry()

    def _setup_menu(self):
        self.tool_bar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, 
                        self.tool_bar)
        self.tool_bar.addAction(QIcon("icons/floppy_disk_48.png"), "save", self.on_save)
    
    def on_save(self): pass
    def on_close(self): pass
        
