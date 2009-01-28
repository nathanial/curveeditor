class LasFile(object):
    def __init__(self, version_header, curve_header, las_data):
        self.version_header = version_header
        self.curve_header = curve_header
        self.las_data = las_data


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

    def __repr__(self): return self.__str__()

    def __eq__(self,that):
        return (self.version == that.version and
                self.wrap == that.wrap)

class CurveHeader(object):
    def __init__(self, descriptors):
        self.descriptors = descriptors

    def __str__(self):
        return "descriptors = %s" % self.descriptors

    def __repr__(self): return self.__str__()

    def __eq__(self,that):
        return (self.descriptors == that.descriptors)

class Descriptor(object):
    def __init__(self, mnemonic, unit, description):
        self.mnemonic = mnemonic
        if isinstance(unit,str) and unit.strip() == "":
            self.unit = None
        else:
            self.unit = unit
        self.description = description

    def __str__(self):
        return "mnemonic = %s, unit = %s, description = %s" % (
            self.mnemonic, self.unit, self.description)

    def __repr__(self): return self.__str__()

    def __eq__(self, that):
        return (self.mnemonic == that.mnemonic and
                self.unit == that.unit and
                self.description == that.description)
    

class LasData(object): 
       
    def __init__(self, data, descriptors):
        self.data = data
        self.descriptors = descriptors

    @staticmethod
    def split(data,descriptors):
        row_len = len(descriptors)
        rows = LasData.split_into_rows(data, row_len)
        return map(lambda r: LasData(r, descriptors), rows)

    @staticmethod
    def split_into_rows(data, row_len):
        cursor = 0
        rows = []
        while cursor < len(data):
            rows.append(data[cursor:(cursor + row_len)])
            cursor += row_len
        return rows

    def __repr__(self): return self.__str__()
    
    def __str__(self):
        return str(self.data)

        
        
        
