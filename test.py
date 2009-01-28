from __future__ import with_statement
import parser
from las import Descriptor, VersionHeader, CurveHeader, LasData

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
    "DEPTH .m                  : trend\n"
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
        return parser.parse("descriptor", descriptors_text[n])

    dept = parse_from(0)
    net_gross = parse_from(1)
    facies = parse_from(2)
    porosity = parse_from(3)
    gamma = parse_from(4)
    depth = parse_from(5)
    
    assert dept == Descriptor("DEPT", "m", "DEPTH")
    assert net_gross == Descriptor("NetGross", None, "NetGross")
    assert facies == Descriptor("Facies", None, "Facies")
    assert porosity == Descriptor("Porosity", "m3/m3", "Porosity")
    assert gamma == Descriptor("Gamma", "gAPI", "Gamma")
    assert depth == Descriptor("DEPTH", "m", "trend")

def test_version_header():
    version_header = parser.parse("version_header", version_header_text)
    assert version_header == VersionHeader(2.0, False)
    
def test_curve_header():
    global curve_header
    curve_header = parser.parse("curve_header", curve_header_text)
    assert len(curve_header.descriptors) == 6
    
#    assert curve_header.mnemonics == ["DEPT", "NetGross", "Facies", 
#                                     "Porosity", "Gamma", "DEPTH"]

def test_las_data():
   data = parser.parse("las_data", las_data_text)
   las_datas = LasData.split(data,curve_header)

def test_las_file():
    las_text = ""
    with open("test2.las") as f:
        for line in f:
            las_text += line
    
    las_file = parser.parse("las_file", las_text)

    

test_descriptors()
test_version_header()
test_curve_header()
test_las_data()
test_las_file()

print "success"
