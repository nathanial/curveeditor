from PyQt4 import QtGui, QtCore

def minimum_size_policy(widget):
    widget.setSizePolicy(QtGui.QSizePolicy.Minimum,
                         QtGui.QSizePolicy.Minimum)
    widget.updateGeometry()

def fixed_size_policy(widget):
    widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                         QtGui.QSizePolicy.Fixed)
    widget.updateGeometry()
        
