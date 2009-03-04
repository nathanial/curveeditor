from las.file import *
from gui.plots import *
from gui.gutil import *
from gui.tracks import *
from PyQt4.QtCore import QRectF, Qt, QSize, QMimeData
from PyQt4.QtGui import QApplication, QMainWindow, QLabel,\
    QPixmap, QWidget, QPainter, QVBoxLayout, QGridLayout, QListView, \
    QStandardItem, QStandardItemModel, QIcon, QAbstractItemView, \
    QMenu, QMenuBar, QSizePolicy, QToolBar, QTableWidget, QTableWidgetItem

class CurveEditingPanel(AbstractTrackPanel):
    def __init__(self, curve, index, parent = None):
        AbstractTrackPanel.__init__(self, [], parent)
        self.curve = curve
        self.index = index

        self._setup_table()

        self.changing_depth = False
        self._setup_depth_slider(index.min(), index.max())

        track = SinglePlotTrack(Plot(self.curve, self.index), self)
        track.add_change_callback(self.on_change)

        self.tracks.append(track)
        self.layout.addWidget(track, 1, Qt.AlignLeft)
        self.updateGeometry()

    def _setup_table(self):
        num_points = len(self.curve)
        self.table = QTableWidget(num_points, 2, self)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["depth","value"])
        self.layout.addWidget(self.table)
        yrange = self.index.range()
        last = None
        for i in range(0,num_points):
            val_idx = num_points - (i + 1)
            depth = QTableWidgetItem(str(self.index[val_idx]))
            value = QTableWidgetItem(str(self.curve[val_idx]))
            self.table.setItem(i,0,depth)
            self.table.setItem(i,1,value)
            last = depth
        self.table.scrollToItem(last)

    def on_change(self, track, plot):
        self._update_table()

    def _update_table(self):
        num_points = len(self.curve)
        for i in range(0, num_points):
            val_idx = num_points - (i + 1)
            depth = QTableWidgetItem(str(self.index[val_idx]))
            value = QTableWidgetItem(str(self.curve[val_idx]))
            self.table.setItem(i,0,depth)
            self.table.setItem(i,1,value)
        
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
        
