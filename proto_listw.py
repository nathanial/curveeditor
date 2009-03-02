from las.file import *
from gui.plots import *
from gui.gutil import *
from gui.icons import *
from PyQt4.QtCore import QRectF, Qt, QSize
from PyQt4.QtGui import QApplication, QMainWindow, QLabel,\
    QPixmap, QWidget, QPainter, QVBoxLayout, QGridLayout, QListView, \
    QStandardItem, QStandardItemModel, QIcon, QAbstractItemView

        
app = QApplication([])
test_las = LasFile.from_("test.las")
curve_panel = CurvePanel(test_las)
app.exec_()



