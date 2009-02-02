import re
import new

def preprocess_str(obj):
    if isinstance(obj, str):
        obj = obj.strip()
        if obj == "":
            return None
        else:
            return obj
    else:
        return obj

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
            if desc in self.curve_header.descriptor_mnemonics() and dtype == "_list":
                acc = []
                for data in self.las_data:
                    acc.append(getattr(data,desc))
                return acc
            else:
                raise AttributeError

    def to_las(self):
        return (self.version_header.to_las() +
                self.well_header.to_las() + 
                self.curve_header.to_las() +
                self.parameter_header.to_las() +
                self.las_data.to_las())

class Descriptor(object):
    def __init__(self, mnemonic, unit = None, data = None, description = None):
        self.mnemonic = preprocess_str(mnemonic)
        self.unit = preprocess_str(unit)
        self.data = preprocess_str(data)
        self.description = preprocess_str(description)

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

    def to_las(self):
        return " ".join([self.mnemonic, self.unit, self.data, self.description]) + "\n"


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

    def to_las(self):
        rows = LasData.split_into_rows(self.data, len(self.curve_header.descriptors))
        data_string = "\n".join(map(lambda r: " ".join(r)))
        return ("~Ascii\n" + data_string)
                
        
        
class HasDescriptors(object):
    def descriptor_mnemonics(self):
        return map(lambda d: d.mnemonic.lower(), self.descriptors)
