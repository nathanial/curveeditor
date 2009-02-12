class Registry(object):
    def __init__(self):
        self._lasfile = None
        self.lasfile_listeners = []
        self.filename = None

    def get_lasfile(self):
        return self._lasfile

    def set_lasfile(self,lf):
        self._lasfile = lf
        for listener in self.lasfile_listeners:
            listener()

    def get_curve(self,name):
        return getattr(self._lasfile, str(name + "_field"))

    lasfile = property(fget = get_lasfile, fset = set_lasfile)

registry = Registry()
