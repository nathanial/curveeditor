import re
import new
from util import lfind, tuplize, read_file

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
    def __init__(self, version_header, well_header, curve_header, parameter_header, data_rows):
        self.version_header = version_header
        self.well_header = well_header
        self.curve_header = curve_header
        self.parameter_header = parameter_header
        self.fields = LasField.from_rows(data_rows, self.curve_header)

        for mnemonic in self.curve_header.mnemonics():
            field = LasField.find_with_mnemonic(mnemonic, self.fields)
            setattr(self, mnemonic + "_field", field)

    def __eq__(self,that):
        if not isinstance(that, LasFile): return False
        return (self.version_header == that.version_header and
                self.well_header == that.well_header and
                self.curve_header == that.curve_header and 
                self.parameter_header == that.parameter_header and
                self.fields == that.fields)

    @staticmethod
    def from_(path):
        from parser import parse
        return parse("las_file", read_file(path))

    def to_las(self):
        return (self.version_header.to_las() +
                self.well_header.to_las() + 
                self.curve_header.to_las() +
                self.parameter_header.to_las() +
                LasField.to_las(self.fields))

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
        return (self.mnemonic + "." + 
                (self.unit or " ") + " " + 
                (self.data or " ") + " : " + 
                (self.description or " "))

class HasDescriptors(object):
    def mnemonics(self):
        return map(lambda d: d.mnemonic.lower(), self.descriptors)

class LasField(object):
    def __init__(self, descriptor, data):
        self.descriptor = descriptor
        self.data = data

    def __getitem__(self, idx):
        return self.get_at(idx)

    def __setitem__(self, idx, val):
        return self.set_at(idx, val)

    def set_at(self, idx, val):
        self.data[idx] = val

    def get_at(self, idx):
        return self.data[idx]

    def data_len(self):
        return len(self.data)

    def __eq__(self, that):
        if not isinstance(that, LasField): return False
        if not self.descriptor == that.descriptor: return False
        return not lfind(tuplize(self.data, that.data), 
                         lambda dd: dd[0] - dd[1] > 0.1)
        
    def __str__(self):
        return str(self.descriptor)
    
    def __repr__(self): return self.__str__()

    def to_list(self):
        return self.data

    @staticmethod
    def from_rows(data_rows, curve_header):
        ds = curve_header.descriptors
        cols = len(ds)
        return [LasField(ds[i],map(lambda r: r[i], data_rows))
                for i in range(0, cols)]

    @staticmethod
    def to_las(fields):
        cols = fields[0].data_len()
        rows = [[field[col] for field in fields] for col in range(0, cols)]
        return "~Ascii\n" + "\n".join(
            map(lambda r: " ".join(map(str, r)), rows))

    @staticmethod
    def find_with_mnemonic(mnemonic, fields):
        return lfind(fields, lambda f: f.descriptor.mnemonic.lower() == mnemonic)

class TransformedLasField(LasField):
    def __init__(self, lasfield, scale_factor):
        self.lasfield = lasfield
        LasField.__init__(self, lasfield.descriptor, lasfield.data)

    def set_at(self, idx, val):
        self.data[idx] = val / (scale_factor * 1.0)
    
    def get_at(self, idx):
        return self.data[idx] * scale_factor

    def to_list(self):
        return [x * scale_factor for x in self.data]



