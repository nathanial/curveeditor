from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL, QSize, QStringList
from PyQt4.QtGui import QMainWindow, QMenu, QWidget, QHBoxLayout, QFileDialog, \
    QTabWidget, QListView, QDialog, QStringListModel, QListWidget, QListWidgetItem, \
    QVBoxLayout, QPushButton, QAbstractItemView


class MergePanel(QWidget):
    def __init__(self, track_views, parent = None): 
        QWidget.__init__(self, parent)
        self.sources = [tv.curve_source for tv in track_views]
        self.name = "merge " + tv.curve_source.name()
        
class MergeWindow(QWidget): pass

