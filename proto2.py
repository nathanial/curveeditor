import sys, os, random
from gui.main import ApplicationWindow
from helpers import read_lasfile
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow, QMenu, QWidget,\
    QVBoxLayout, QApplication, QMessageBox, QHBoxLayout
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

qApp = QApplication(sys.argv)

aw = ApplicationWindow()

#lf = read_lasfile("/home/nathan/projects/CurveEditor/test.las")

#gamma = Plot(aw.main_widget, width=4, height=8)
#facies = Plot(aw.main_widget, width=4, height=8)
#porosity = Plot(aw.main_widget, width=4, height=8)

#gline, = gamma.plot(lf.gamma_list, lf.depth_list, "b-", picker=5)
#fline, = facies.plot(lf.facies_list, lf.depth_list, "r-", picker=5)
#pline, = porosity.plot(lf.porosity_list, lf.depth_list, "g-", picker=5)

#DraggableLine(gline).connect()
#DraggableLine(fline).connect()
#DraggableLine(pline).connect()

#aw.add_plot(gamma)
#aw.add_plot(facies)
#aw.add_plot(porosity)

aw.setWindowTitle("Curve Editor")
aw.show()
sys.exit(qApp.exec_())
