import numpy as np
import matplotlib.pyplot as plt

class DraggableLine:
    def __init__(self, line):
        self.line = line
        self.press = None

    def connect(self):
        self.cidpress = self.line.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.line.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.line.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        contains,attrd = self.line.contains(event)
        if not contains: return
        self.press = attrd['ind']

    def on_motion(self, event):
        if self.press is None: return
        ind = self.press

        oxs = self.line.get_xdata()
        oys = self.line.get_ydata()
        oxs[ind] = event.xdata
        oys[ind] = event.ydata
        self.line.set_xdata(oxs)
        self.line.set_ydata(oys)
        self.line.figure.canvas.draw()

    def on_release(self, event):
        self.press = None
        self.line.figure.canvas.draw()

    def disconnect(self):
        self.line.figure.canvas.mpl_disconnect(self.cidpress)
        self.line.figure.canvas.mpl_disconnect(self.cidrelease)
        self.line.figure.canvas.mpl_disconnect(self.cidmotion)
