from gui.icons import *
from las.file import *


app = QApplication([])
main_window = QMainWindow()

test_las = LasFile.from_("robert.las")
curve_panel = CurvePanel(test_las, main_window)

main_window.setCentralWidget(curve_panel)
main_window.show()
main_window.updateGeometry()
main_window.adjustSize()
app.exec_()
