from las import VersionHeader, CurveHeader, Descriptor, LasFile, LasData


# Begin -- grammar generated by Yapps
import sys, re
from yapps import runtime

class LASParserScanner(runtime.Scanner):
    patterns = [
        ('"\\n"', re.compile('\n')),
        ('"~A"', re.compile('~A')),
        ('"\\."', re.compile('\\.')),
        ('"~C"', re.compile('~C')),
        ('"WRAP."', re.compile('WRAP.')),
        ('":"', re.compile(':')),
        ('"VERS."', re.compile('VERS.')),
        ('" "', re.compile(' ')),
        ('"~V"', re.compile('~V')),
        (' ', re.compile(' ')),
        ('MNEMONIC', re.compile('\\w+')),
        ('UNIT', re.compile('(\\w|[/])*')),
        ('DESCRIPTION', re.compile('\\w*')),
        ('STRING', re.compile('\\w*')),
        ('NUM', re.compile('-?[0-9]+')),
        ('FLOAT', re.compile('-?[0-9]+[.][0-9]+')),
        ('EMPTY', re.compile('')),
    ]
    def __init__(self, str,*args,**kw):
        runtime.Scanner.__init__(self,None,{' ':None,},str,*args,**kw)

class LASParser(runtime.Parser):
    Context = runtime.Context
    def las_file(self, _parent=None):
        _context = self.Context(_parent, self._scanner, 'las_file', [])
        version_header = self.version_header(_context)
        curve_header = self.curve_header(_context)
        las_data = self.las_data(_context)
        return LasFile(version_header, curve_header, LasData.split(las_data, curve_header))

    def version_header(self, _parent=None):
        _context = self.Context(_parent, self._scanner, 'version_header', [])
        while self._peek('"~V"', '"\\n"', '"VERS."', '"WRAP."', '"~C"', '"~A"', 'MNEMONIC', 'EMPTY', 'NUM', 'FLOAT', context=_context) == '"\\n"':
            end_line = self.end_line(_context)
        self._scan('"~V"', context=_context)
        STRING = self._scan('STRING', context=_context)
        while self._peek('" "', '"\\n"', context=_context) == '" "':
            self._scan('" "', context=_context)
            STRING = self._scan('STRING', context=_context)
        end_line = self.end_line(_context)
        self._scan('"VERS."', context=_context)
        number = self.number(_context)
        self._scan('":"', context=_context)
        vers = number
        end_line = self.end_line(_context)
        self._scan('"WRAP."', context=_context)
        STRING = self._scan('STRING', context=_context)
        self._scan('":"', context=_context)
        wrap = STRING
        end_line = self.end_line(_context)
        return VersionHeader(vers,wrap)

    def curve_header(self, _parent=None):
        _context = self.Context(_parent, self._scanner, 'curve_header', [])
        while self._peek('"~C"', '"VERS."', '"WRAP."', '"\\n"', '"~V"', '"~A"', 'MNEMONIC', 'EMPTY', 'NUM', 'FLOAT', context=_context) == '"\\n"':
            end_line = self.end_line(_context)
        self._scan('"~C"', context=_context)
        STRING = self._scan('STRING', context=_context)
        end_line = self.end_line(_context)
        descriptors = []
        while self._peek('"VERS."', '"WRAP."', 'MNEMONIC', '"~V"', '"\\n"', '"~C"', '"~A"', 'EMPTY', 'NUM', 'FLOAT', context=_context) == 'MNEMONIC':
            descriptor = self.descriptor(_context)
            descriptors.append(descriptor)
            end_line = self.end_line(_context)
        return CurveHeader(descriptors)

    def descriptor(self, _parent=None):
        _context = self.Context(_parent, self._scanner, 'descriptor', [])
        MNEMONIC = self._scan('MNEMONIC', context=_context)
        self._scan('"\\."', context=_context)
        UNIT = self._scan('UNIT', context=_context)
        self._scan('":"', context=_context)
        DESCRIPTION = self._scan('DESCRIPTION', context=_context)
        return Descriptor(MNEMONIC, UNIT, DESCRIPTION)

    def las_data(self, _parent=None):
        _context = self.Context(_parent, self._scanner, 'las_data', [])
        while self._peek('"~A"', '"VERS."', '"WRAP."', '"\\n"', '"~V"', '"~C"', 'MNEMONIC', 'EMPTY', 'NUM', 'FLOAT', context=_context) == '"\\n"':
            end_line = self.end_line(_context)
        self._scan('"~A"', context=_context)
        STRING = self._scan('STRING', context=_context)
        end_line = self.end_line(_context)
        data = []
        while self._peek('EMPTY', '"VERS."', '"WRAP."', '"~V"', '"\\n"', '"~C"', '"~A"', 'NUM', 'FLOAT', 'MNEMONIC', context=_context) in ['NUM', 'FLOAT']:
            row = self.row(_context)
            data.extend(row)
            if self._peek('"\\n"', '"VERS."', '"WRAP."', '"~V"', '"~C"', '"~A"', 'EMPTY', 'MNEMONIC', 'NUM', 'FLOAT', context=_context) == '"\\n"':
                end_line = self.end_line(_context)
        EMPTY = self._scan('EMPTY', context=_context)
        return data

    def row(self, _parent=None):
        _context = self.Context(_parent, self._scanner, 'row', [])
        columns = []
        while 1:
            number = self.number(_context)
            columns.append(number)
            if self._peek('NUM', 'FLOAT', '"\\n"', '"VERS."', '"WRAP."', '"~V"', '"~C"', '"~A"', 'EMPTY', 'MNEMONIC', context=_context) not in ['NUM', 'FLOAT']: break
        return columns

    def number(self, _parent=None):
        _context = self.Context(_parent, self._scanner, 'number', [])
        _token = self._peek('NUM', 'FLOAT', context=_context)
        if _token == 'NUM':
            NUM = self._scan('NUM', context=_context)
            return eval(NUM)
        else: # == 'FLOAT'
            FLOAT = self._scan('FLOAT', context=_context)
            return eval(FLOAT)

    def end_line(self, _parent=None):
        _context = self.Context(_parent, self._scanner, 'end_line', [])
        self._scan('"\\n"', context=_context)


def parse(rule, text):
    P = LASParser(LASParserScanner(text))
    return runtime.wrap_error_reporter(P, rule)

if __name__ == '__main__':
    from sys import argv, stdin
    if len(argv) >= 2:
        if len(argv) >= 3:
            f = open(argv[2],'r')
        else:
            f = stdin
        print parse(argv[1], f.read())
    else: print >>sys.stderr, 'Args:  <rule> [<filename>]'
# End -- grammar generated by Yapps
