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
        self.fields = LasField.rows_to_fields(data_rows, self.curve_header)

        for mnemonic in self.curve_header.descriptor_mnemonics():
            field = LasField.find_with_mnemonic(mnemonic, self.fields)
            setattr(self,mnemonic + "_field", field)

    def __eq__(self,that):
        if not isinstance(that, LasFile): return False
        return (self.version_header == that.version_header and
                self.well_header == that.well_header and
                self.curve_header == that.curve_header and 
                self.parameter_header == that.parameter_header and
                self.fields == that.fields)

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

class LasField(object):
    def __init__(self, descriptor, data):
        self.descriptor = descriptor
        self.data = data

    def set_at(self, idx, val):
        self.data[idx] = val

    def get_at(self, idx):
        return self.data[idx]

    def data_length(self):
        return len(self.data)

    def __eq__(self, that):
        if not isinstance(that, LasField): return False
        if not self.descriptor == that.descriptor: return False

        for idx in range(0, len(self.data)):
            if not ((self.data[idx] - that.data[idx]) < 0.1):
                return False
        return True

    def __str__(self):
        return str(self.descriptor)
    
    def __repr__(self): return self.__str__()

    def to_list(self):
        return self.data

    @staticmethod
    def rows_to_fields(data_rows, curve_header):
        fields = []
        idx = 0
        for descriptor in curve_header.descriptors:
            field = LasField(descriptor, map(lambda row: row[idx], data_rows))
            fields.append(field)
            idx += 1
        return fields

    @staticmethod
    def to_las(fields):
        row_len = fields[0].data_length()
        rows = []
        for idx in range(0, row_len):
            row = []
            for field in fields:
                row.append(field.get_at(idx))
            rows.append(row)
            
        return "~Ascii\n" + "\n".join(
            map(lambda r: " ".join(map(str, r)), rows))

    @staticmethod
    def find_with_mnemonic(mnemonic, fields):
        for idx in range(0, len(fields)):
            if fields[idx].descriptor.mnemonic.lower() == mnemonic:
                return fields[idx]
        return None
                
                
        
class HasDescriptors(object):
    def descriptor_mnemonics(self):
        return map(lambda d: d.mnemonic.lower(), self.descriptors)
