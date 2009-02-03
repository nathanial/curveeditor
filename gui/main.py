import sys, os, random
from helpers import read_lasfile
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Curve Editor")
        
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        
        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        
        self.main_widget = QWidget(self)
        
        self.plot_layout = QHBoxLayout(self.main_widget)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        
    def fileQuit(self):
        self.close()
        
    def closeEvent(self, ce):
        self.fileQuit()

    def addPlot(self, plot):
        self.plot_layout.addWidget(plot)

