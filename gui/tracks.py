from __future__ import with_statement
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout, QPushButton,\
    QDialog, QRadioButton, QPalette
from PyQt4.QtCore import SIGNAL, QSize, QMutex
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.plots import *
from las.file import LasFile
from dummy import *

class TrackPanel(QWidget):
    def __init__(self,curve_source, main_window, parent = None):
        QWidget.__init__(self,parent)
        fixed_size_policy(self)
        self.main_window = main_window
        self.layout = QHBoxLayout(self)
        self._setup_depth_slider()
        self.tracks = []
        self.dummy_track = None
        self.curve_source = curve_source
        self.changing_depth = False
        self.updateGeometry()

    def add_new_track(self):
        track = Track(self.curve_source, self)
        self.add_track(track)
        self.layout.invalidate()
        self.updateGeometry()
        
    def add_track(self, track):
        for t in self.tracks:
            self.layout.setStretchFactor(t, 0)
        self.tracks.append(track)
        self.layout.addWidget(track, 1, Qt.AlignLeft)

    def add_dummy_track(self):
        self.dummy_track = DummyTrack(self)
        self.add_track(self.dummy_track)

    def remove_track(self):
        track = self.tracks[-1]
        track.hide()
        self.layout.removeWidget(track)
        self.tracks = self.tracks[:-1]
        self.resize_after_remove()

    def remove_dummy_track(self):
        del self.tracks[0]
        self.dummy_track.hide()
        self.layout.removeWidget(self.dummy_track.window)
        self.dummy_track = None

    def replace_dummy_track(self):
        self.remove_dummy_track()
        self.add_new_track()

    def set_depth(self, percentage):
        for track in self.tracks: 
            track.set_depth(percentage)

    def set_index(self, curve_name):
        self.curve_source.set_index(curve_name)
        for track in self.tracks:
            track.refresh_index()

    def resize_after_remove(self):
        self.layout.invalidate()
        self.updateGeometry()
        QApplication.processEvents()
        self.adjustSize()
        QApplication.processEvents()
        self.main_window.updateGeometry()
        QApplication.processEvents()
        self.main_window.adjustSize()

    def _setup_depth_slider(self):
        self.depth_slider = DepthSlider(self)
        self.layout.addWidget(self.depth_slider)
        self.layout.setAlignment(self.depth_slider, Qt.AlignLeft)
        QWidget.connect(self.depth_slider, SIGNAL("valueChanged(int)"),
                        self.set_depth)
        QWidget.connect(self.depth_slider, SIGNAL("sliderPressed()"),
                        self.animate_tracks)
        QWidget.connect(self.depth_slider, SIGNAL("sliderReleased()"),
                        self.deanimate_tracks)

    def animate_tracks(self):
        for track in self.tracks:
            track.animation_on()
    
    def deanimate_tracks(self):
        for track in self.tracks:
            track.animation_off()

class Track(QWidget):
    def __init__(self, curve_source, parent = None):
        QWidget.__init__(self, parent)
        self.curve_source = curve_source
        self.layout = QVBoxLayout(self)
        fixed_size_policy(self)
        self.pais = []
        self.index = self.curve_source.index()
        self.plot_canvas = PlotCanvas(ymin=self.index.min(), 
                                      ymax=self.index.max(),
                                      yinc=100, 
                                      parent = self,
                                      width=4, height=6)
        self.button_panel = TrackButtonPanel(self, self)
        self.layout.addWidget(self.button_panel)
        self.layout.addWidget(self.plot_canvas)
        self.add_new_plot()
        self.updateGeometry()
        
    def available_curves(self):
        return self.curve_source.available_curves()

    def remove_plot(self, plot):
        pai = lfind(self.pais, lambda p: p.plot == plot)
        pai.my_disconnect()
        self.pais.remove(pai)
        self.updateGeometry()

    def add_new_plot(self):
        pai = PlotAndInfo(self.curve_source.index_name(),
                          self.curve_source,
                          self.plot_canvas,
                          self.button_panel)
        pai.my_connect()
        self.pais.append(pai)
        self.updateGeometry()

    def plots(self):
        return [pai.plot for pai in self.pais]

    def set_depth(self, increment):
        self.plot_canvas.set_increment(increment)

    def refresh_index(self):
        for pai in self.pais:
            pai.reindex()

    def animation_on(self):
        self.plot_canvas.animation_on()
    
    def animation_off(self):
        self.plot_canvas.animation_off()

    def contextMenuEvent(self, event):
        TrackContextMenu(self, self).popup(event.globalPos())

class TrackButtonPanel(QWidget):
    def __init__(self, track, parent):
        QWidget.__init__(self, parent)
        minimum_size_policy(self)
        self.track = track
        self.layout = QVBoxLayout(self)
        self.layout.setSizeConstraint(QLayout.SetMinimumSize)

class DepthSlider(QSlider):
    def __init__(self, parent = None):
        self.tracks_view = parent
        tv = parent
        QSlider.__init__(self, QtCore.Qt.Vertical, parent)
class TrackContextMenu(QMenu):
    def __init__(self, track, parent):
        QMenu.__init__(self, parent)
        self.track = track
        plots = track.plots()

        self.addAction('&Add Curve', self.track.add_new_plot)
        for plot in plots:
            self.addMenu(CurveContextMenu(self, plot))

        QApplication.processEvents()
        self.updateGeometry()
        QApplication.processEvents()
        self.adjustSize()
                
class CurveContextMenu(QMenu):
    def __init__(self, parent, plot):
        QMenu.__init__(self, plot.name(), parent)
        color_menu = CurveColorMenu(self,plot)
        marker_menu = CurveMarkerMenu(self,plot)
        self.addMenu(color_menu)
        self.addMenu(marker_menu)
        self.addAction('&Remove', lambda: parent.track.remove_plot(plot))

class CurveColorMenu(QMenu):
    def __init__(self, parent,plot):
        QMenu.__init__(self,"Color", parent)
        self.addAction('&Red', lambda: plot.set_color("r"))
        self.addAction('&Blue', lambda: plot.set_color("b"))
        self.addAction('&Green', lambda: plot.set_color("g"))

class CurveMarkerMenu(QMenu):
    def __init__(self, parent, plot):
        QMenu.__init__(self,"Marker", parent)
        self.addAction('&None', lambda: plot.set_marker("None"))
        self.addAction('&Circle', lambda: plot.set_marker("o"))
        self.addAction('&Triangle', lambda: plot.set_marker("^"))

