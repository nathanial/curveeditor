from __future__ import with_statement
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout, QPushButton,\
    QDialog, QRadioButton, QPalette, QGroupBox, QAction
from PyQt4.QtCore import SIGNAL, QSize, QMutex
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.plots import *
from gui.editing import *
from las.file import LasFile
import registry
from util import cmp_max

class CurvePanel(QListView):
    def __init__(self, curve_source, parent = None):
        QListView.__init__(self, parent)
        self.curve_source = curve_source
        self.setViewMode(QListView.IconMode)
        self.setSelectionMode(QListView.ExtendedSelection)
        self.setIconSize(QSize(64,64))
        self.model = PlotItemModel()
        self.setModel(self.model)
        self.setWrapping(True)
        self.setAcceptDrops(True)
        self.updateGeometry()
        self.adjustSize()
        self.show()

    def add_curves_from_source(self):
        for curve in self.curve_source._curves:
            self.add_curve(curve)
            self.doItemsLayout()
            QApplication.processEvents()

    def edit(self, index, trigger, event):
        if trigger == QAbstractItemView.DoubleClicked:
            item = self.model.item(index.row())
            plots = item.plots
            dialog = CurveEditingWindow(plots, self)
            dialog.show()
            return True
        else:
            return False

    def mousePressEvent(self, event):
        if self._is_empty(event.pos()): self.clearSelection()
        return QListView.mousePressEvent(self, event)

    def add_new_curve(self):
        pass
    
    def add_curve(self, curve):
        plot = Plot(curve, self.curve_source.index())
        self.add_plot(plot)

    def add_plot(self, plot):
        item = PlotItem(plot)
        self.model.appendRow(item)

    def _is_empty(self, pos):
        return self.indexAt(pos).row() is -1

class CurvePanelContextMenu(QMenu):
    def __init__(self, curve_panel):
        QMenu.__init__(self, curve_panel)
        self.curve_panel = curve_panel
        self.addAction("&Copy", self.on_copy)
        self.addAction("&Paste", self.on_paste)
        self.addAction("&Delete", self.on_delete)
        self.addAction("&Layout", self.on_layout)
        self.addAction("&Combine", self.on_combine)

    def on_copy(self): 
        plot_items = self._selected_plot_items()
        registry.clipboard['plot_items'] = plot_items

    def on_paste(self): 
        plot_items = registry.clipboard['plot_items']
        for pi in plot_items:
            self.curve_panel.add_plot(pi.plot)

    def on_delete(self):
        model = self.curve_panel.model
        indexes = [mi.row() for mi in self.curve_panel.selectedIndexes()]
        indexes.sort(cmp=cmp_max)
        for index in indexes:
            model.removeRow(index)

    def on_layout(self):
        self.curve_panel.doItemsLayout()

    def on_combine(self):
        plot_items = self._selected_plot_items()
        cpi = CompoundPlotItem(plot_items)
        self.curve_panel.model.appendRow(cpi)
        

    def _selected_plot_items(self):
        model = self.curve_panel.model
        indexes = [mi.row() for mi in self.curve_panel.selectedIndexes()]
        return [model.item(i) for i in indexes]
        

class DraggableCurvePanel(CurvePanel):
    def __init__(self, curve_source, file_tab_panel, parent = None):
        CurvePanel.__init__(self, curve_source, parent)
        self.file_tab_panel = file_tab_panel
    
    def contextMenuEvent(self, event):
        CurvePanelContextMenu(self).popup(event.globalPos())

class ExpandoWidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

class CurvePanelTab(QWidget):
    def __init__(self, curve_source, file_tab_panel):
        QWidget.__init__(self)
        self.curve_source = curve_source
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.file_tab_panel = file_tab_panel
        self.layout = QVBoxLayout(self)
        self.curve_panel = DraggableCurvePanel(curve_source, self.file_tab_panel, self)

        self._setup_tool_bar()
        
        self.layout.addWidget(self.curve_panel)

        self.updateGeometry()
        self.adjustSize()

    def on_close(self):
        self.file_tab_panel.removeTab(self.file_tab_panel.currentIndex())

    def on_save(self):
        self.emit(SIGNAL("save_curve_source"), self.curve_source)

    def _setup_tool_bar(self):
        self.toolbar = QToolBar(self)
        self.close_action = QAction(QIcon("icons/cross_48.png"),
                                    "close", self.toolbar)
        QWidget.connect(self.close_action, SIGNAL("triggered()"),
                        self.on_close)
        self.toolbar.insertAction(None, self.close_action)
        self.toolbar.insertWidget(self.close_action, ExpandoWidget())

        self.layout.addWidget(self.toolbar)
