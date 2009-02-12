from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QVBoxLayout
from gui.plots import Plot


class Run(object): 
    def __init__(self, parent = None):
        self.increment = 0
        self.window = RunWindow(self, parent)
        self.plot_canvas = PlotCanvas(self.window, width=4, height=6)

class RunWindow(QWidget):
    def __init__(self, run, parent = None):
        QWidget.__init__(self, parent)
        fixed_size_policy(self)
        self.run = run
        self.button_panel = RunButtonPanel(run, self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.button_panel)

    def add_plot_info(self, plot):
        self.button_panel.add_plot_info(plot)
        self.updateGeometry()

class Track(object):
    def __init__(self, las_source, parent = None):
        self.las_source = las_source
        self.window = TrackWindow(self, parent)
        self.plot_canvas = PlotCanvas(self.window, width=4, height=6)
        self.window.layout.addWidget(self.plot_canvas)
        self.add_new_plot()
        self.window.updateGeometry()
        
    def change_curve(self, old_plot, curve_name): 
        new_plot = Plot.of(curve_name, "depth")
        self.plot_canvas.swap_plot(old_plot, new_plot)
        self.window.button_panel.swap_plot_info(old_plot, new_plot)

    def add_new_plot(self):
        plot = Plot.of("dept", "depth").from_(self.las_source)
        self.plot_canvas.add_plot(plot)
        self.window.add_plot_info(plot)

    def plots(self):
        return list(self.plot_canvas.plots)

    def set_increment(self, increment):
        self.plot_canvas.set_increment(increment)

    def draw(self):
        self.plot_canvas.draw()

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
