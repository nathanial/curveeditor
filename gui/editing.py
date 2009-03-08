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
    def __init__(self, plots, parent = None):
        AbstractTrackPanel.__init__(self, [], parent)
        self.curves = [p.original_xfield for p in plots]
        self.indexes = [p.original_yfield for p in plots]
        self.main_index = self._longest_index()
        print "main_index = %s " % self.main_index
        self.plots = plots

        self._setup_table()
        self._connect_table()

        self.changing_depth = False
        self._setup_depth_slider(self.main_index.min(), self.main_index.max())

        self.tracks = [SinglePlotTrack(p, self) for p in plots]
        for track in self.tracks:
            track.add_change_callback(self.on_plot_change)
            self.layout.addWidget(track)
        self.updateGeometry()

    def center_on(self, ycoord):
        plot_canvas = self.track().plot_canvas
        ycoord = ycoord - plot_canvas.ymin
        yrange = plot_canvas.yrange()
        increment = ((ycoord / yrange) * 100) - 4
        if increment < 0:
            increment = 0
        self.set_depth(increment)
        self.depth_slider.slider.setValue(increment)

    def _setup_table(self):
        num_points = self._num_points()
        self.table = QTableWidget(num_points, 2, self)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["depth","value"])
        self.layout.addWidget(self.table)
        last = None
        main_index = self._longest_index()
        for i in range(0, num_points):
            val_idx = (num_points - 1) - i

            depth = QTableWidgetItem(str(main_index[val_idx]))
            depth.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(i, 0, depth)
            last = depth

            col = 1
            for c in self.curves:
                if i < len(c):
                    value = QTableWidgetItem(str(c[val_idx]))
                    self.table.setItem(i, col, value)
                col += 1

        self.table.scrollToItem(last)
        QWidget.connect(self.table, SIGNAL("itemSelectionChanged()"),
                        self._hilite_selected_items)

    def _num_points(self):
        return len(self._longest_curve())

    def _longest_curve(self):
        longest = self.curves[0]
        for c in self.curves:
            if len(c) > len(longest):
                longest = c
        return longest

    def _longest_index(self):
        longest = self.indexes[0]
        for i in self.indexes:
            if len(i) > len(longest):
                longest = i
        return longest
            
    def on_plot_change(self, track, plot, idx):
        self._disconnect_table()
        self._update_table(idx)
        self._connect_table()

    def on_table_change(self, row, col):
        track = self.tracks[0]
        num_points = len(self.curve)
        depth = float(self.table.item(row,0).text())
        new_xdata = float(self.table.item(row,1).text())
        idx = num_points - (row + 1)
        track.plot.modify_xdata(idx, new_xdata)
        track.plot.canvas.draw()
        self.center_on(depth)
        track.repaint()

    
    def _update_table(self, val_idx):
        num_points = self._num_points()
        row = (num_points - 1) - val_idx
        value = QTableWidgetItem(str(self.curve[val_idx]))
        self.table.setItem(row,1,value)
        self.table.scrollToItem(value)

    def _hilite_selected_items(self):
        print [i.row() for i in self.table.selectedIndexes()]

    def _connect_table(self):
        QWidget.connect(self.table, SIGNAL("cellChanged(int,int)"),
                        self.on_table_change)

    def _disconnect_table(self):
        QWidget.disconnect(self.table, SIGNAL("cellChanged(int,int)"),
                           self.on_table_change)
        
class CurveEditingWindow(QMainWindow):
    def __init__(self, plots, parent = None):
        QMainWindow.__init__(self, parent)
        self.plots = plots
        self.dirty = False
        self.setWindowTitle(" ".join([p.name() for p in self.plots]))
        self._setup_menu()
        QApplication.processEvents()
        self.editing_panel = CurveEditingPanel(self.plots, self)
        self.setCentralWidget(self.editing_panel)
        self.updateGeometry()

    def _setup_menu(self):
        self.tool_bar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, 
                        self.tool_bar)
        self.tool_bar.addAction(QIcon("icons/floppy_disk_48.png"), "save", self.on_save)
    
    def on_save(self): pass
    def on_close(self): pass
        
