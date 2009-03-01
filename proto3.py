from las.file import *
from gui.plots import *
from PyQt4.QtGui import QApplication, QMainWindow

app = QApplication([])

test_las = LasFile.from_("test.las")
plot = Plot.of("facies", "dept").from_(test_las)
plot.set_linewidth(4)
main_window = QMainWindow()
plot_canvas = PlotCanvas(ymin=plot.ymin(),
                         ymax=plot.ymax(),
                         yinc=100,
                         parent = main_window)
main_window.setCentralWidget(plot_canvas)
main_window.show()
plot_canvas.add_plot(plot)
plot_canvas.draw()
plot_canvas.fig.savefig("facies.png")

app.exec_()
