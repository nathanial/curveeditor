from __future__ import with_statement

from PyQt4 import QtCore
from PyQt4.QtCore import SIGNAL, QSize
from PyQt4.QtGui import QMainWindow, QMenu, \
    QWidget, QHBoxLayout, QFileDialog, QTabWidget, \
    QDialog, QListWidget, QListWidgetItem, QVBoxLayout,\
    QPushButton, QAbstractItemView, QTabBar, QApplication, \
    QProgressBar, QProgressDialog

from gui.gutil import minimum_size_policy
from gui.merge import MergePanel
from gui.tracks import TrackPanel
from las.file import LasFile


class ApplicationWindow(QMainWindow):
    def __init__(self):
        self.tracks = []
        QMainWindow.__init__(self)
        minimum_size_policy(self)
        self.track_panels = []
        self.merge_views = []

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Curve Editor")
        self.main_widget = FileTabPanel(self)
        self.file_tab_panel = self.main_widget

        self.file_menu = FileMenu(self)
        self.menuBar().addMenu(self.file_menu)
        
        self.tracks_menu = TracksMenu(self)
        self.menuBar().addMenu(self.tracks_menu)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.updateGeometry()
        
    def closeEvent(self, ce):
        self.close()

    def sizeHint(self):
        return QSize(400, 700)

    def track_panel_with_focus(self):
        return self.file_tab_panel.currentWidget()

    def create_new_track_panel(self, lasfile):
        track_panel = TrackPanel(lasfile, self, self.file_tab_panel)
        track_panel.add_new_track()
        self.track_panels.append(track_panel)
        self.file_tab_panel.addTab(track_panel, track_panel.curve_source.name())
        return track_panel

    def create_new_merge_view(self, track_panels):
        merge_view = MergePanel([tv.curve_source for tv in track_panels], None)
        self.merge_views.append(merge_view)
        self.file_tab_panel.addTab(merge_view, merge_view.name)


class FileTabPanel(QTabWidget):
    def __init__(self, main_window):
        QTabWidget.__init__(self, main_window)
                        

class FileMenu(QMenu):
    def __init__(self, parent):
        self.app_window = parent
        QMenu.__init__(self, '&File', parent)
        self.addAction('&Open', self.open,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.addAction('&Save', self.save,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.addAction('&Save As', self.save_as)
        self.addAction('&Quit', self.quit,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
                       
    
    def open(self):
        dialog = QFileDialog(self, "Open LAS")
        dialog.setFileMode(QFileDialog.ExistingFiles)
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            show_progress = len(filenames) > 1            
            if show_progress:
                progress = QProgressDialog(self.app_window)
                progress.setMinimum(1)
                progress.setMaximum(len(filenames))
            for filename in filenames:
                if LasFile.is_lasfile(filename):
                    lasfile = LasFile.from_(filename)
                    if show_progress:
                        progress.setValue(progress.value() + 1)
                else:
                    raise "%s is not a las file!!" % filename
                self.app_window.create_new_track_panel(lasfile)

    def save(self):
        track_panel = self.app_window.track_panel_with_focus()
        lasfile = track.curve_source
        filename = lasfile.path
        with open(filename, "w") as f:
            f.write(lasfile.to_las())

    def save_as(self):
        track_panel = self.app_window.track_panel_with_focus()
        lasfile = track_panel.curve_source
        dialog = QFileDialog(self, "Save As")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec_():
            filename, = dialog.selectedFiles()
            with open(filename, "w") as f:
                f.write(lasfile.to_las())

    def quit(self):
        QApplication.quit()


class TracksMenu(QMenu):
    def __init__(self, main_window):
        self.main_window = main_window
        QMenu.__init__(self, '&Tracks', main_window)
        self.addAction('&Add', self.add_track)
        self.addAction('&Remove', self.remove_track)
        self.addAction('&Merge', self.merge_tracks)
        self.addAction('&Set Index', self.set_index)
        
    def add_track(self):
        track_panel = self.main_window.track_panel_with_focus()
        track_panel.add_new_track()
        for tp in self.main_window.track_panels:
            tp.layout.invalidate()
            
    def remove_track(self):
        track_panel = self.main_window.track_panel_with_focus()
        track_panel.remove_track()

    def merge_tracks(self):
        dialog = MergeDialog(self.main_window.track_panels)
        if dialog.exec_():
            track_panels = dialog.selected_track_panels()
            self.main_window.create_new_merge_view(track_panels)

    def set_index(self):
        track_panel = self.main_window.track_panel_with_focus()
        dialog = IndexDialog(track_panel)
        if dialog.exec_():
            new_index = dialog.index()
            track_panel.set_index(new_index)

class IndexDialog(QDialog):
    def __init__(self, track_panel, parent = None):
        QDialog.__init__(self, parent)
        self.track_panel = track_panel
        self.layout = QVBoxLayout(self)
        self.list = QListWidget(self)
        curve_names = self.track_panel.curve_source.available_curves()
        for curve_name in curve_names:
            self.list.addItem(QListWidgetItem(curve_name, self.list))

        self.ok_button = QPushButton("ok", self)
        minimum_size_policy(self.ok_button)
        QWidget.connect(self.ok_button, SIGNAL("clicked()"),
                        self.accept)
        self.list.updateGeometry()
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.ok_button)
        self.updateGeometry()
        self.adjustSize()

    def index(self):
        selected, = self.list.selectedItems()
        return selected.text()
            
        
class MergeDialog(QDialog):
    def __init__(self, track_panels, parent = None):
        QDialog.__init__(self, parent)
        self.track_panels = track_panels
        self.layout = QVBoxLayout(self)
        self.list = QListWidget(self)
        self.list.setSelectionMode(QAbstractItemView.MultiSelection)
        for tv in track_panels:
            name = tv.curve_source.name()
            self.list.addItem(QListWidgetItem(name, self.list))

        self.ok_button = QPushButton("ok", self)
        minimum_size_policy(self.ok_button)
        QWidget.connect(self.ok_button, SIGNAL("clicked()"),
                        self.accept)

        self.list.updateGeometry()
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.ok_button)
        self.updateGeometry()
        self.adjustSize()

    def selected_track_panels(self):
        selected = self.list.selectedItems()
        names = [s.text() for s in selected]
        return [tv for tv in self.track_panels 
                if tv.curve_source.name() in names]        

        
        
        
        
