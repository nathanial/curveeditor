import re
import new

class LasFile(object):
    def __init__(self, version_header, well_header, curve_header, parameter_header, las_data):
        self.version_header = version_header
        self.well_header = well_header
        self.curve_header = curve_header
        self.parameter_header = parameter_header
        self.las_data = las_data

    def __getattr__(self, attr):
        if attr in self.__dict__: 
            return self.__dict__[attr]
        else:
            m = re.match("([a-z]+)(_list)?", attr)
            desc, dtype = m.groups()
            print self.curve_header.descriptor_mnemonics()
            if desc in self.curve_header.descriptor_mnemonics() and dtype == "_list":
                acc = []
                for data in self.las_data:
                    acc.append(getattr(data,desc))
                return acc
            else:
                raise AttributeError

class DefaultProperty(property):
    def __init__(self, default_value):
        super(DefaultProperty, self).__init__(fget = self.get, fset = self.set)
        self.val = default_value
        
    def get(self, obj):
        return self.val

    def set(self, obj, nval):
        if isinstance(nval, str) and nval.strip() == "":
            self.val = None
        else:
            self.val = nval
        
class Descriptor(object):
    mnemonic = DefaultProperty(None)
    unit = DefaultProperty(None)
    data = DefaultProperty(None)
    description = DefaultProperty(None)

    def __init__(self, mnemonic, unit = None, data = None, description = None):
        self.mnemonic = mnemonic
        self.unit = unit
        self.data = data
        self.description = description

    def __str__(self):
        return "mnemonic = %s, unit = %s, data = %s, description = %s" % (
            self.mnemonic, self.unit, self.data, self.description)

    def __repr__(self): return self.__str__()

    def __eq__(self, that):
        if not isinstance(that, Descriptor): return False
        return (self.mnemonic == that.mnemonic and
                self.unit == that.unit and
                self.data == that.data and
                self.description == that.description)


class LasData(object): 
       
    def __init__(self, data, curve_header):
        self.data = data
        self.curve_header = curve_header

    def __repr__(self): 
        return self.__str__()
    
    def __str__(self):
        return str(self.data)

    def __getattr__(self,attr):
        if attr in self.__dict__: 
            return self.__dict__[attr]
        elif attr in self.curve_header.descriptor_mnemonics():
            return self.data_for(attr)
        else:
            raise AttributeError

    def data_for(self, desc):
        idx = self.curve_header.descriptor_mnemonics().index(desc)
        return self.data[idx]

    @staticmethod
    def split(data,curve_header):
        row_len = len(curve_header.descriptors)
        rows = LasData.split_into_rows(data, row_len)
        return map(lambda r: LasData(r, curve_header), rows)

    @staticmethod
    def split_into_rows(data, row_len):
        cursor = 0
        rows = []
        while cursor < len(data):
            rows.append(data[cursor:(cursor + row_len)])
            cursor += row_len
        return rows        
        
        
class HasDescriptors(object):
    def descriptor_mnemonics(self):
        return map(lambda d: d.mnemonic.lower(), self.descriptors)
