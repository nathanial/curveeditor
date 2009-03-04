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
        self._connect_table()

        self.changing_depth = False
        self._setup_depth_slider(index.min(), index.max())

        track = SinglePlotTrack(Plot(self.curve, self.index), self)
        track.add_change_callback(self.on_plot_change)

        self.tracks.append(track)
        self.layout.addWidget(track, 1, Qt.AlignLeft)
        self.updateGeometry()

    def _setup_table(self):
        num_points = len(self.curve)
        self.table = QTableWidget(num_points, 2, self)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["depth","value"])
        self.layout.addWidget(self.table)
        self._update_table(scroll_to_last = True)

    def on_plot_change(self, track, plot):
        self._disconnect_table()
        self._update_table()
        self._connect_table()

    def on_table_change(self, row, col):
        print "table change"
        track = self.tracks[0]
        num_points = len(self.curve)
        new_xdata = float(self.table.item(row,col).text())
        idx = num_points - (row + 1)
        print "new data = %s " % new_xdata
        print "idx = %s " % idx
        track.plot.modify_xdata(idx, new_xdata)
        track.plot.canvas.draw()
        track.repaint()

    def _update_table(self, scroll_to_last = False):
        num_points = len(self.curve)
        last = None
        for i in range(0, num_points):
            val_idx = num_points - (i + 1)
            depth = QTableWidgetItem(str(self.index[val_idx]))
            depth.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            value = QTableWidgetItem(str(self.curve[val_idx]))
            self.table.setItem(i,0,depth)
            self.table.setItem(i,1,value)
            last = depth
        if scroll_to_last:
            self.table.scrollToItem(last)

    def _connect_table(self):
        QWidget.connect(self.table, SIGNAL("cellChanged(int,int)"),
                        self.on_table_change)

    def _disconnect_table(self):
        QWidget.disconnect(self.table, SIGNAL("cellChanged(int,int)"),
                           self.on_table_change)
        
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
        
