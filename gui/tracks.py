from __future__ import with_statement
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout,\
    QFileDialog, QSlider, QComboBox, QLayout, QPushButton,\
    QDialog, QRadioButton, QPalette, QGroupBox
from PyQt4.QtCore import SIGNAL, QSize, QMutex
from gui.gutil import minimum_size_policy, fixed_size_policy
from gui.plots import *
from las.file import LasFile
from dummy import *

class AbstractTrackPanel(QWidget):
    def __init__(self, tracks, parent):
        QWidget.__init__(self,parent)
        fixed_size_policy(self)
        self.tracks = tracks
        self.layout = QHBoxLayout(self)

    def animate_tracks(self):
        for track in self.tracks:
            track.animation_on()

    def deanimate_tracks(self):
        for track in self.tracks:
            track.animation_off()

    def set_depth(self, percentage):
        for track in self.tracks: 
            track.set_depth(percentage)
        
    def _setup_depth_slider(self, depth_min, depth_max):
        self.depth_slider = DepthSlider(depth_min, depth_max, self)
        self.layout.addWidget(self.depth_slider)
        self.layout.setAlignment(self.depth_slider, Qt.AlignLeft)
        QWidget.connect(self.depth_slider.slider, SIGNAL("valueChanged(int)"),
                        self.set_depth)
        QWidget.connect(self.depth_slider.slider, SIGNAL("sliderPressed()"),
                        self.animate_tracks)
        QWidget.connect(self.depth_slider.slider, SIGNAL("sliderReleased()"),
                        self.deanimate_tracks)
        

class TrackPanel(AbstractTrackPanel):
    def __init__(self, curve_source, main_window, parent):
        AbstractTrackPanel.__init__(self, [], parent)
        self.main_window = main_window
        self.tracks = []
        self.dummy_track = None
        self.curve_source = curve_source
        self.changing_depth = False
        index = self.curve_source.index()
        self._setup_depth_slider(index.min(), index.max())
        self.updateGeometry()

    def add_new_track(self):
        track = Track(self.curve_source, self)
        track.set_depth(self.depth_slider.slider.value())
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


class Track(QWidget):
    def __init__(self, curve_source, 
                 parent = None,
                 starting_plot = True,
                 ymin = None,
                 ymax = None,
                 yinc = None):
        QWidget.__init__(self, parent)
        self.curve_source = curve_source
        self.layout = QVBoxLayout(self)
        fixed_size_policy(self)
        self.pais = []
        self.index = self.curve_source.index()
        self.plot_canvas = PlotCanvas(ymin= ymin or self.index.min(), 
                                      ymax= ymax or self.index.max(),
                                      yinc= yinc or 100, 
                                      parent = self,
                                      width=4, height=6)
        self.info_panel = TrackInfoPanel(self, self)
        self.layout.addWidget(self.info_panel)
        self.layout.addWidget(self.plot_canvas)
        self.add_new_plot()
        self.updateGeometry()

    def my_disconnect(self):
        for pai in self.pais:
            pai.my_disconnect()
        self.hide()
        
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
                          self.info_panel)
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

class TrackInfoPanel(QWidget):
    def __init__(self, track, parent):
        QWidget.__init__(self, parent)
        minimum_size_policy(self)
        self.track = track
        self.layout = QVBoxLayout(self)
        self.layout.setSizeConstraint(QLayout.SetMinimumSize)

class DepthSlider(QWidget):
    def __init__(self, min_depth, max_depth, tracks_panel = None):
        QWidget.__init__(self, tracks_panel)
        self.tracks_panel = tracks_panel
        self.slider = QSlider(Qt.Vertical, self)
        tick_box = QGroupBox(self)
        tick_layout = QVBoxLayout()
        layout = QHBoxLayout(self)
        
        depth_range = max_depth - min_depth
        increment = depth_range / 8.0
        rrange = range(0,8)
        rrange.reverse()
        for i in rrange:
            tick_depth = i * increment + min_depth
            tick_layout.addWidget(QLabel(str(tick_depth)))
        tick_box.setLayout(tick_layout)
        
        layout.addWidget(tick_box)
        layout.addWidget(self.slider)

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

