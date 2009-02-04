from __future__ import with_statement
import parser
from las.headers import *
from las.file import *
from util import subdivide, forall

well_header_text = """
~Well
STRT .m      1499.8790000 :
STOP .m      2416.3790000 :
STEP .m     0.00000000 :
NULL .        -999.250000 :
COMP.           : COMPANY
WELL.  A10   : WELL
FLD.            : FIELD
LOC.            : LOCATION
SRVC.           : SERVICE COMPANY
DATE.  Monday, January 26 2009 14:04:02   : DATE
PROV.           : PROVINCE
UWI.      : UNIQUE WELL ID
API.            : API NUMBER
"""

curve_header_text = """
~Curve
DEPT .m                   : DEPTH
NetGross .                : NetGross
Facies .                  : Facies
Porosity .m3/m3           : Porosity
Gamma .gAPI               : Gamma
DEPTH .m                  : trend
"""

descriptors_text = [
    "DEPT .m                   : DEPTH\n",
    "NetGross .                : NetGross\n",
    "Facies .                  : Facies\n",
    "Porosity .m3/m3           : Porosity\n",
    "Gamma .gAPI               : Gamma\n",
    "DEPTH .m                  : trend\n",
    "STRT .m      1499.8790000 :",
    "STOP .m      2416.3790000 :",
    ]

version_header_text = """
~Version information
VERS.   2.0:
WRAP.   NO:
"""

las_data_text = """
~Ascii
 1499.8790000 0.0000000000  -999.250000  -999.250000  -999.250000 1499.8790283
 1500.1290000 0.0000000000  -999.250000  -999.250000  -999.250000 1500.1290283
 1500.6290000 0.0000000000  -999.250000  -999.250000  -999.250000 1500.6290283
 1501.1290000 0.0000000000 0.0000000000 0.2706460059  -999.250000 1501.1290283
 1501.6290000 0.0000000000 0.0000000000 0.2674280107 78.869453430 1501.6290283
 1502.1290000 0.0000000000 0.0000000000 0.2560760081 78.008300781 1502.1290283
 1502.6290000 0.0000000000 0.0000000000 0.2421260029 75.581558228 1502.6290283
 1503.1290000 0.0000000000 0.0000000000 0.2385890037 73.238037109 1503.1290283
 1503.6290000 0.0000000000 0.0000000000 0.2383770049 71.504173279 1503.6290283
"""


def test_descriptors():
    def parse_from(n):
        descriptor = parser.parse("descriptor", descriptors_text[n])
        return descriptor

    dept = parse_from(0)
    net_gross = parse_from(1)
    facies = parse_from(2)
    porosity = parse_from(3)
    gamma = parse_from(4)
    depth = parse_from(5)
    start = parse_from(6)
    stop = parse_from(7)
    
    assert dept == Descriptor(mnemonic="DEPT",unit="m",description="DEPTH")
    assert net_gross == Descriptor(mnemonic="NetGross", description="NetGross")
    assert facies == Descriptor(mnemonic="Facies", description="Facies")
    assert porosity == Descriptor(mnemonic="Porosity", unit="m3/m3", description="Porosity")
    assert gamma == Descriptor(mnemonic="Gamma", unit="gAPI", description="Gamma")
    assert depth == Descriptor(mnemonic="DEPTH", unit="m", description="trend")
    assert start == Descriptor(mnemonic="STRT", unit="m", data="1499.8790000")
    assert stop == Descriptor(mnemonic="STOP", unit="m", data="2416.3790000")

    print "tested descriptors"

def test_version_header():
    version_header = parser.parse("version_header", version_header_text)
    assert version_header == VersionHeader(2.0, False)
    print "tested version_header"

def test_well_header():
    well_header = parser.parse("well_header", well_header_text)
    assert well_header.date.data == "Monday, January 26 2009 14:04:02"
    assert well_header.date.description == "DATE"
    print "tested well_header"
    
def test_curve_header():
    global curve_header
    curve_header = parser.parse("curve_header", curve_header_text)
    assert len(curve_header.descriptors) == 6
    mnemonics = curve_header.mnemonics()
    assert forall(["dept", "netgross", "facies", "porosity", "gamma", "depth"],
                  lambda m: m in mnemonics)
    print "tested curve_header"

def test_las_data():
    cols = len(curve_header.descriptors)
    rows = subdivide(parser.parse("data_rows", las_data_text), cols)
    fields = LasField.rows_to_fields(rows,curve_header)

def test_las_file():
    las_text = ""
    with open("test.las") as f:
        for line in f:
            las_text += line
    
    las_file = parser.parse("las_file", las_text)

    

test_descriptors()
test_version_header()
test_curve_header()
test_las_data()
test_well_header()
test_las_file()

print "success"
