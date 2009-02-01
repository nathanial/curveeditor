import re
from file import HasDescriptors

class VersionHeader(object):
    def __init__(self, version, wrap): 
        self.version = version
        if isinstance(wrap, str):
            if wrap.strip() == "NO":
                self.wrap = False
            elif wrap.strip() == "YES":
                self.wrap = True
            else:
                raise "Unknown value for wrap = %s " % wrap
        else:
            self.wrap = wrap
            
    def __str__(self):
        return "version = %s, wrap = %s" % (self.version, self.wrap)

    def __repr__(self):
        return self.__str__()

    def __eq__(self,that):
        if not isinstance(that, VersionHeader): return False
        return (self.version == that.version and
                self.wrap == that.wrap)

class HeaderWithDescriptors(HasDescriptors):
    def __str__(self):
        return "%s(descriptors = %s)" % (self.__class__.__name__, self.descriptors)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, that):
        if not isinstance(that, self.__class__): return False
        return (self.descriptors == that.descriptors)

class CurveHeader(HeaderWithDescriptors):
    def __init__(self, descriptors):
        self.descriptors = descriptors

class WellHeader(HeaderWithDescriptors): 
    def __init__(self, descriptors):
        self.descriptors = descriptors

class ParameterHeader(HeaderWithDescriptors):
    def __init__(self, descriptors):
        self.descriptors = descriptors

