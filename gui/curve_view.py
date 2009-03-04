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
from gui.icons import *
from gui.editing import *
from las.file import LasFile

class CurvePanel(QListView):
    def __init__(self, curve_source, parent = None):
        QListView.__init__(self, parent)
        self.curve_source = curve_source
        self.setViewMode(QListView.IconMode)
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

class DraggableCurvePanel(CurvePanel):
    def __init__(self, curve_source, file_tab_panel, parent = None):
        CurvePanel.__init__(self, curve_source, parent)
        self.file_tab_panel = file_tab_panel

    def mouseMoveEvent(self, event):
        epos = event.pos()
        for i in range(0, self._tab_count()):
            if self._set_if_in_tab(i, epos):
                break
        return CurvePanel.mouseMoveEvent(self, event)

    def dragMoveEvent(self, event):
        epos = event.pos()
        for i in range(0, self._tab_count()):
            if self._set_if_in_tab(i, epos):
                break
        return CurvePanel.dragMoveEvent(self, event)

    def _set_if_in_tab(self, index, point):
        tb = self.file_tab_panel.tabBar()
        rect = tb.tabRect(index)
        if rect.contains(point):
            self.file_tab_panel.setCurrentIndex(index)
            return True
        return False

    def _tab_count(self):
        return self.file_tab_panel.tabBar().count()

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
