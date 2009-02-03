import numpy as np
import matplotlib.pyplot as plt
from gui.plots import DraggableLine

class Plotter(object): 
    def __init__(self, xs, ys):
        self.xs = xs
        self.ys = ys
        
    def show(self):
        line, = plt.plot(self.xs, self.ys, "b-", picker=5)
        dline = DraggableLine(line)
        dline.connect()
        plt.show()



        
