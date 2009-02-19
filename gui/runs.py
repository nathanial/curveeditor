from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QVBoxLayout
from gui.plots import Plot

class RunsView(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        minimum_size_policy(self)
        self.runs = []
        self.layout = QHBoxLayout(self)
        
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
