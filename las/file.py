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
    def __init__(self, version_header, well_header, curve_header, parameter_header, data_rows):
        self.version_header = version_header
        self.well_header = well_header
        self.curve_header = curve_header
        self.parameter_header = parameter_header
        self.data_rows = data_rows

        for mnemonic in self.curve_header.descriptor_mnemonics():
            setattr(self,mnemonic + "_list", self.acc_data_for(mnemonic))

    def __eq__(self,that):
        if not isinstance(that, LasFile): return False
        return (self.version_header == that.version_header and
                self.well_header == that.well_header and
                self.curve_header == that.curve_header and 
                self.parameter_header == that.parameter_header and
                self.data_rows == that.data_rows)

    def acc_data_for(self, desc):
        acc = []
        for data_row in self.data_rows:
            acc.append(getattr(data_row, desc))
        return acc

    def clean_dirty_data(self):
        for mnemonic in self.curve_header.descriptor_mnemonics():
            dirty_data = getattr(self, mnemonic + "_list")
            idx = 0
            for data_row in self.data_rows:
                setattr(data_row,mnemonic,dirty_data[idx])
                idx += 1

    def to_las(self):
        self.clean_dirty_data()
        return (self.version_header.to_las() +
                self.well_header.to_las() + 
                self.curve_header.to_las() +
                self.parameter_header.to_las() +
                "~Ascii\n" + 
                "\n".join(map(lambda dr: dr.to_las(), self.data_rows)))

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


class LasData(object):        
    def __init__(self, data, curve_header):
        self.data = data
        self.curve_header = curve_header
        for mnemonic in self.curve_header.descriptor_mnemonics():
            setattr(self, mnemonic, self.data_for(mnemonic))

    def __repr__(self): 
        return self.__str__()
    
    def __str__(self):
        return str(self.data)

    def __eq__(self,that):
        if not isinstance(that, LasData): return False
        return self.data == that.data

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

    def clean_dirty_data(self):
        idx = 0
        for mnemonic in self.curve_header.descriptor_mnemonics():
            self.data[idx] = getattr(self, mnemonic)
            idx += 1

    def to_las(self):
        self.clean_dirty_data()
        return " ".join(map(lambda x: str(x), self.data))
        
        
class HasDescriptors(object):
    def descriptor_mnemonics(self):
        return map(lambda d: d.mnemonic.lower(), self.descriptors)
