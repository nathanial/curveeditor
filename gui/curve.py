from las.file import LasField, transform
from matplotlib.lines import Line2D

class Curve(Line2D):
    def __init__(self,curve_name, canvas, xfield = None, yfield = None, *args, **kwargs):
        self.curve_name = curve_name
        self.canvas = canvas
        self.xfield = xfield
        self.yfield = yfield
        self._args = args
        self._kwargs = kwargs
        self.press = None
        self.draggable = False
        Line2D.__init__(self, xfield.to_list(), yfield.to_list(), *args, **kwargs)

    def connect_draggable(self):
        self.cidpress = self.canvas.mpl_connect(
            'button_press_event', self.drag_on_press)
        self.cidrelease = self.canvas.mpl_connect(
            'button_release_event', self.drag_on_release)
        self.cidmotion = self.canvas.mpl_connect(
            'motion_notify_event', self.drag_on_motion)
        self.draggable = True
        
    def drag_on_press(self, event):
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

    def disconnect_draggable(self):
        self.canvas.mpl_disconnect(self.cidpress)
        self.canvas.mpl_disconnect(self.cidrelease)
        self.canvas.mpl_disconnect(self.cidmotion)
        self.draggable = False

    def transform(self,xscale = 1.0, yscale = 1.0, xoffset = 0, yoffset = 0):
        return TransformedCurve(
            self.curve_name,
            self.canvas,
            self.xfield, xscale, xoffset,
            self.yfield, yscale, yoffset,
            *self._args, **self._kwargs)
                     
    def yrange(self):
        return self.ymax() - self.ymin()

    def ymin(self):
        return min(self.yfield.to_list())

    def ymax(self):
        return max(self.yfield.to_list())

    def xrange(self):
        return self.xmax() - self.xmin()

    def xmax(self):
        return max(self.xfield.to_list())
    
    def xmin(self):
        return min(self.xfield.to_list())

class TransformedCurve(Curve):
    def __init__(self, curve_name, canvas, 
                 xfield, xscale, xoffset, 
                 yfield, yscale, yoffset, 
                 *args, **kwargs):
        self.original_xfield = xfield
        self.original_yfield = yfield
        Curve.__init__(self, curve_name, canvas,
                       transform(xfield, xscale, xoffset),
                       transform(yfield, yscale, yoffset),
                       *args, **kwargs)

    def transform(self, xscale = 1.0, yscale = 1.0, xoffset = 0, yoffset = 0):
        return TransformedCurve(
            self.curve_name, 
            self.canvas,
            self.original_xfield, xscale, xoffset,
            self.original_yfield, yscale, yoffset,
            *self._args, **self._kwargs)

    def original(self):
        return Curve(self.curve_name,
                     self.canvas,
                     self.original_xfield, 
                     self.original_yfield,
                     *self._args, **self._kwargs)
