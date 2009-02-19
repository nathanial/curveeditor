from __future__ import with_statement
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout, QPushButton,\
    QDialog, QRadioButton
from PyQt4.QtCore import SIGNAL, QSize, QMutex
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.plots import *
from las.file import LasFile
from dummy import *

class TracksView(QWidget):
    def __init__(self, main_window, parent = None):
        QWidget.__init__(self,parent)
        minimum_size_policy(self)
        self.main_window = main_window
        self.layout = QHBoxLayout(self)
        self._setup_file_menu()
        self._setup_tracks_menu()
        self._setup_depth_slider()
        self.tracks = []
        self.dummy_track = None
        self.curve_source = None
        self.changing_depth = False

    def select_file(self):
        self.file_menu.openFile()

    def update_curve_source(self, curve_source):
        self.curve_source = curve_source
        if self.dummy_track:
            self.replace_dummy_track()
        elif not self.tracks:
            self.add_new_track()
        else:
            for track in self.tracks:
                track.update_curve_source(curve_source)

    def add_new_track(self):
        track = Track(self.curve_source, self)
        self.add_track(track)
        
    def add_track(self, track):
        self.layout.addWidget(track.window)
        self.tracks.append(track)
        self.resize_after_remove()

    def remove_track(self):
        track = self.tracks[-1]
        track.window.hide()
        self.layout.removeWidget(track.window)
        del self.tracks[-1]
        self.resize_after_remove()

    def resize_after_remove(self):
        self.updateGeometry()
        QApplication.processEvents()
        self.adjustSize()
        QApplication.processEvents()
        self.main_window.updateGeometry()
        QApplication.processEvents()
        self.main_window.adjustSize()

    def replace_dummy_track(self):
        self.remove_dummy_track()
        self.add_new_track()

    def add_dummy_track(self):
        self.dummy_track = DummyTrack(self)
        self.add_track(self.dummy_track)

    def remove_dummy_track(self):
        del self.tracks[0]
        self.dummy_track.hide()
        self.layout.removeWidget(self.dummy_track.window)
        self.dummy_track = None

    def _setup_file_menu(self):
        self.file_menu = TracksFileMenu(self.main_window)
        self.main_window.menuBar().addMenu(self.file_menu)
        QWidget.connect(self.file_menu, SIGNAL("update_curve_source"),
                        self.update_curve_source)
    

    def _setup_tracks_menu(self):
        self.tracks_menu = TracksMenu(self.main_window)
        self.main_window.menuBar().addMenu(self.tracks_menu)
        QWidget.connect(self.tracks_menu, SIGNAL("add_track"),
                        self.add_new_track)
        QWidget.connect(self.tracks_menu, SIGNAL("remove_track"),
                        self.remove_track)

    def _setup_depth_slider(self):
        self.depth_slider = DepthSlider(self)
        self.layout.addWidget(self.depth_slider)
        QWidget.connect(self.depth_slider, SIGNAL("valueChanged(int)"),
                        self.change_depth)
        QWidget.connect(self.depth_slider, SIGNAL("sliderPressed()"),
                        self.animate_tracks)
        QWidget.connect(self.depth_slider, SIGNAL("sliderReleased()"),
                        self.deanimate_tracks)

    def change_depth(self, increment):
        for track in self.tracks: 
            track.set_increment(increment)

    def animate_tracks(self):
        for track in self.tracks:
            track.animation_on()
    
    def deanimate_tracks(self):
        for track in self.tracks:
            track.animation_off()

class Track(object):
    def __init__(self, curve_source, parent = None):
        self.curve_source = curve_source
        self.window = TrackWindow(self, parent)
        self.plot_canvas = PlotCanvas(self.window, width=4, height=6)
        self.window.layout.addWidget(self.plot_canvas)
        self.window.updateGeometry()
        
    def change_curve(self, old_plot, curve_name): 
        new_plot = None
        try:
            new_plot = Plot.of(curve_name, "depth").from_(self.curve_source)
        except AttributeError:
            new_plot = Plot.of(curve_name, "dept").from_(self.curve_source)
        self.plot_canvas.swap_plot(old_plot, new_plot)
        self.window.button_panel.swap_plot_info(old_plot, new_plot)

    def add_new_plot(self):
        plot = self._default_depth_plot()
        self.plot_canvas.add_plot(plot)
        self.window.add_plot_info(plot)

    def plots(self):
        return list(self.plot_canvas.plots)

    def set_increment(self, increment):
        self.plot_canvas.set_increment(increment)

    def draw(self): 
        self.plot_canvas.draw()

    def available_curves(self):
        return self.curve_source.available_curves()

    def update_curve_source(self, curve_source):
        self.curve_source = curve_source
        self.plot_canvas.remove_all_plots()
        self.window.remove_all_plot_info()

    def _default_depth_plot(self):
        cs = self.curve_source
        depth_curve = None
        if cs.has_curve("dept"):
            depth_curve = "dept"
        elif cs.has_curve("depth"):
            depth_curve = "depth"
        else:
            raise "Cannot find depth curve!"

        ycurve = cs.curve(depth_curve)
        xcurve = cs.curve(depth_curve)
        return Plot(xcurve, ycurve)

    def animation_on(self):
        self.plot_canvas.animation_on()
    
    def animation_off(self):
        self.plot_canvas.animation_off()

class TracksMenu(QMenu):
    def __init__(self, parent):
        QMenu.__init__(self, '&Tracks', parent)
        self.addAction('&Add Track', self.addTrack)
        self.addAction('&Remove Track', self.removeTrack)
        
    def addTrack(self):
        self.emit(SIGNAL("add_track"))
        
    def removeTrack(self):
        self.emit(SIGNAL("remove_track"))

class TracksFileMenu(QMenu):
    def __init__(self, parent):
        self.app_window = parent
        QMenu.__init__(self, '&File', parent)
        self.addAction('&Open', self.openFile,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.addAction('&Save', self.saveFile,
                       QtCore.Qt.CTRL + QtCore.Qt.Key_S)

    def openFile(self):
        dialog = QFileDialog(self, "Open LAS")
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            self.filename, = dialog.selectedFiles()
            if LasFile.is_lasfile(self.filename):
                curve_source = LasFile.from_(self.filename)
            self.las_file = curve_source
            self.emit(SIGNAL("update_curve_source"), curve_source)            

    def saveFile(self):
        with open(self.filename, "w") as f:
            f.write(self.las_file.to_las())



class TrackButtonPanel(QWidget):
    def __init__(self, track, parent):
        QWidget.__init__(self, parent)
        minimum_size_policy(self)
        self.track = track
        self.plot_infos = []
        parent.layout.addWidget(self)
        self.layout = QVBoxLayout(self)

    def add_plot_info(self, plot):
        pi = self._build_plot_info(plot)
        self.layout.addWidget(pi)
        self.plot_infos.append(pi)
    
    def remove_plot_info(self, plot):
        deleted, index = self._destroy_plot_info(plot)
        del self.plot_infos[index]
        deleted.hide()
        self.layout.removeWidget(deleted)

    def remove_all_plot_info(self):
        for plot_info in self.plot_infos:
            plot_info.hide()
        self.plot_infos = []
        self.relayout()

    def swap_plot_info(self, old_plot, new_plot):
        new_info = self._build_plot_info(new_plot)
        old_info, index = self._destroy_plot_info(old_plot)
        old_info.hide()
        self.plot_infos[index] = new_info
        self.relayout()

    def relayout(self):
        for pi in self.plot_infos:
            self.layout.removeWidget(pi)
        for pi in self.plot_infos:
            self.layout.addWidget(pi)
    
    def _plot_index(self, plot):
        return map(lambda pi: pi.plot, self.plot_infos).index(plot)

    def _build_plot_info(self, plot):
        plot_info = PlotInfo(plot, self.track.available_curves(), self)
        self._connect_to_track(plot_info)
        return plot_info
    
    def _destroy_plot_info(self, plot):
        index = self._plot_index(plot)
        pi = self.plot_infos[index]
        self._disconnect_from_track(pi)
        return pi, index

    def _connect_to_track(self, plot_info):
        QWidget.connect(plot_info,
                        SIGNAL("change_curve"),
                        self.track.change_curve)

    def _disconnect_from_track(self, plot_info):
        QWidget.disconnect(plot_info,
                           SIGNAL("change_curve"),
                           self.track.change_curve)            


class TrackWindow(QWidget):
    def __init__(self, track, parent = None):
        QWidget.__init__(self, parent)
        fixed_size_policy(self)
        self.track = track
        self.layout = QVBoxLayout(self)
        self.button_panel = TrackButtonPanel(track, self)

    def contextMenuEvent(self, event):
        PlotsContextMenu(self.track, self).popup(event.globalPos())

    def add_plot_info(self, plot):
        self.button_panel.add_plot_info(plot)
        self.updateGeometry()
    
    def remove_all_plot_info(self):
        self.button_panel.remove_all_plot_info()        

class DepthSlider(QSlider):
    def __init__(self, parent = None):
        self.tracks_view = parent
        tv = parent
        QSlider.__init__(self, QtCore.Qt.Vertical, parent)
        self.hide()
        QWidget.connect(tv.tracks_menu, SIGNAL("add_track"),
                        self.hide_or_show)
        QWidget.connect(tv.tracks_menu, SIGNAL("remove_track"),
                        self.hide_or_show)
        QWidget.connect(tv.file_menu, SIGNAL("update_curve_source"),
                        self.hide_or_show)
        
    def hide_or_show(self):
        if self.tracks_view.tracks == []:
            self.hide()
        else:
            self.show()
