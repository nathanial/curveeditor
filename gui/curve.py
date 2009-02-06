from las.file import LasField
from matplotlib.lines import Line2D

class Curve(Line2D):
    def __init__(self,curve_name, xfield = None, yfield = None, *args, **kwargs):
        self.curve_name = curve_name
        self.xfield = xfield
        self.yfield = yfield
        self.press = None
        Line2D.__init__(self, xfield.to_list(), yfield.to_list(), *args, **kwargs)

    def connect_draggable(self, canvas):
        self.canvas = canvas
        self.cidpress = self.canvas.mpl_connect(
            'button_press_event', self.drag_on_press)
        self.cidrelease = self.canvas.mpl_connect(
            'button_release_event', self.drag_on_release)
        self.cidmotion = self.canvas.mpl_connect(
            'motion_notify_event', self.drag_on_motion)
        
    def drag_on_press(self, event):
        print event
        contains,attrd = self.contains(event)
        if not contains: return
        self.press = attrd['ind']

    def drag_on_motion(self, event):
        if self.press is None: return
        ind = self.press
        if len(ind) > 1: ind = ind[0]
        self.xfield[ind] = event.xdata
        self.yfield[ind] = event.ydata
        
        self.set_xdata(self.xfield.to_list())
        self.set_ydata(self.yfield.to_list())
        self.canvas.draw()

    def drag_on_release(self, event):
        self.press = None
        self.canvas.draw()    
