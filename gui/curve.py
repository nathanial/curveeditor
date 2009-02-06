from matplotlib.lines import Line2D

class Curve(Line2D):
    def __init__(self, xs, ys, *args, **kwargs):
        Line2D.__init__(self, xs, ys, *args, **kwargs)
        self.xs = xs
        self.ys = ys
