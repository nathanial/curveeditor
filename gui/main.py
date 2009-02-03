from __future__ import with_statement
import sys, os, random
from helpers import read_lasfile
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout, QFileDialog
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gui.plots import Plot, DraggableLine, PlotWindow

class ApplicationWindow(QMainWindow):
    def __init__(self):
        self.plots = []

        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Curve Editor")

        self.setup_menu()

        self.main_widget = QWidget(self)      
        
        self.setup_plots(self.main_widget)
        
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        
    def fileQuit(self):
        self.close()
        
    def closeEvent(self, ce):
        self.fileQuit()

    def add_plot(self, plot):
        self.plot_layout.addWidget(plot)
        self.plots.append(plot)

    def setup_menu(self):
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.file_menu.addAction('&Open', self.openFile,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Save', self.saveFile,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)

        self.menuBar().addMenu(self.file_menu)

    def setup_plots(self, main_widget):
        self.plot_layout = QHBoxLayout(self.main_widget)
        self.add_plot(PlotWindow(main_widget))

    def read_and_plot(self, filename):
        self.las_file = read_lasfile(filename)
        lf = self.las_file
        
        for plot in self.plots:
            plot.las_file = lf
            plot.las_update()        

    def openFile(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            self.filename, = dialog.selectedFiles()
            self.read_and_plot(self.filename)

    def saveFile(self):
        with open(self.filename, "w") as f:
            f.write(self.las_file.to_las())
    
            
            
        
