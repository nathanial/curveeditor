import numpy as np
import matplotlib.pyplot as plt
from helpers import DraggableLine

xs = np.arange(0., 10., 1.)
ys = np.arange(0., 10., 1.)

line, = plt.plot(xs, ys, "b-", picker=5)
dline = DraggableLine(line)
dline.connect()

plt.show()

