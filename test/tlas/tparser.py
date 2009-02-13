from test.test_util import test
from las.file import *
from las.headers import *
from util import partial, forall, subdivide
from yacc_parser import parser, LasLexer
from test import data

tests = []
test = partial(test, tests)

@test
def test_descriptors():
    def parse_from(n):
        return parser.parse(data.text['descriptors'][n])
    pf = parse_from
    
    dept, net_gross, facies = pf(0), pf(1), pf(2)
    porosity, gamma, depth = pf(3), pf(4), pf(5)
    start, stop = pf(6), pf(7)

    assert dept == Descriptor(mnemonic="DEPT",unit="m",description="DEPTH")
    assert net_gross == Descriptor(mnemonic="NetGross", description="NetGross")
    assert facies == Descriptor(mnemonic="Facies", description="Facies")
    assert porosity == Descriptor(mnemonic="Porosity", unit="m3/m3", description="Porosity")
    assert gamma == Descriptor(mnemonic="Gamma", unit="gAPI", description="Gamma")
    assert depth == Descriptor(mnemonic="DEPTH", unit="m", description="trend")
    assert start == Descriptor(mnemonic="STRT", unit="m", data="1499.8790000")
    assert stop == Descriptor(mnemonic="STOP", unit="m", data="2416.3790000")

@test
def test_version_header():
    version_header = parser.parse(data.text['version_header'])
    assert version_header == VersionHeader(2.0, False)
    
@test
def test_well_header():
    well_header = parser.parse(data.text['well_header'])
    assert well_header.date.data == "Monday, January 26 2009 14:04:02"
    assert well_header.date.description == "DATE"

@test
def test_curve_header():
    curve_header = parser.parse(data.text['curve_header'])
    mnemonics = curve_header.mnemonics()
    assert len(curve_header.descriptors) == 6
    assert forall(["dept", "netgross", "facies", "porosity", "gamma", "depth"],
                  lambda m: m in mnemonics)


@test
def test_las_data():
    cols = len(data.curve_header.descriptors)
    rows = subdivide(parser.parse(data.text['las_data']), cols)
    curves = LasCurve.from_rows(rows,data.curve_header)
    
if __name__ == "__main__":
    for test in tests:
        test()
