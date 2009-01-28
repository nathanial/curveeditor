from editor import Plotter
from helpers import read_lasfile

lf = read_lasfile("test2.las")
pl = Plotter(lf.gamma_list, lf.depth_list)
pl.show()
