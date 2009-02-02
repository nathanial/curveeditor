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

    def wrap_string(self):
        if self.wrap: return "YES"
        else: return "NO"
            
    def __str__(self):
        return "version = %s, wrap = %s" % (self.version, self.wrap)

    def __repr__(self):
        return self.__str__()

    def __eq__(self,that):
        if not isinstance(that, VersionHeader): return False
        return (self.version == that.version and
                self.wrap == that.wrap)

    def to_las(self):
        return ("~Version information\n" +
                "VERS. %s\n" % self.version + 
                "WRAP. %s\n" % self.wrap_string())
        

class HeaderWithDescriptors(HasDescriptors):
    def __str__(self):
        return "%s(descriptors = %s)" % (self.__class__.__name__, self.descriptors)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, that):
        if not isinstance(that, self.__class__): return False
        return (self.descriptors == that.descriptors)

    def __getattr__(self, attr):
        if attr in self.__dict__: 
            return self.__dict__[attr]
        else:
            if attr in self.descriptor_mnemonics():
                idx = self.descriptor_mnemonics().index(attr)
                descriptor = self.descriptors[idx]
                return descriptor
            else:
                print "attr %s not found in %s " % (attr, self.descriptor_mnemonics())
                raise AttributeError

    def to_las(self):
        return (self.identifier_string + "\n" + 
                map(lambda x: x.to_las(), self.descriptors))

def descriptor_header(name, identifier):
    class Anon(HeaderWithDescriptors):
        def __init__(self, descriptors):
            self.identifier = identifier
            self.descriptors = descriptors
    Anon.__name__ = name
    return Anon

CurveHeader = descriptor_header("CurveHeader","~Curve")
WellHeader = descriptor_header("WellHeader","~Well")
ParameterHeader = descriptor_header("ParameterHeader","~Parameter")
