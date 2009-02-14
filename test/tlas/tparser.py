from test.test_util import test
from las.file import *
from las.headers import *
from util import partial, forall, subdivide
from my_parser import Parser
from test import data

tests = []
test = partial(test, tests)

@test
def test_descriptors():
    def parse(name):
        parser = Parser(data.text['descriptors'][name])
        return parser.descriptor()

    dept = parse('dept')
    net_gross = parse('netgross')
    facies = parse('facies')
    porosity = parse('porosity')
    gamma = parse('gamma')
    depth = parse('depth')
    start = parse('strt')
    stop = parse('stop')
    date = parse('date')

    assert dept == Descriptor(mnemonic="DEPT",unit="m",description="DEPTH")
    assert net_gross == Descriptor(mnemonic="NetGross", description="NetGross")
    assert facies == Descriptor(mnemonic="Facies", description="Facies")
    assert porosity == Descriptor(mnemonic="Porosity", unit="m3/m3", description="Porosity")
    assert gamma == Descriptor(mnemonic="Gamma", unit="gAPI", description="Gamma")
    assert depth == Descriptor(mnemonic="DEPTH", unit="m", description="trend")
    assert start == Descriptor(mnemonic="STRT", unit="m", data=1499.8790000)
    assert stop == Descriptor(mnemonic="STOP", unit="m", data=2416.3790000)

    assert date == Descriptor(mnemonic="DATE",
                              data="Monday, January 26 2009 14:04:02",
                              description="DATE")
@test
def test_version_header():
    parser = Parser(data.text['version_header'])
    version_header = parser.version_header()
    assert version_header == VersionHeader(2.0, False)
    
@test
def test_well_header():
    parser = Parser(data.text['well_header'])
    well_header = parser.well_header()
    assert well_header.date.data == "Monday, January 26 2009 14:04:02"
    assert well_header.date.description == "DATE"

@test
def test_curve_header():
    parser = Parser(data.text['curve_header'])
    curve_header = parser.curve_header()
    mnemonics = curve_header.mnemonics()
    assert len(curve_header.descriptors) == 6
    assert forall(["dept", "netgross", "facies", "porosity", "gamma", "depth"],
                  lambda m: m in mnemonics)


@test
def test_las_data():
    parser = Parser(data.text['las_data'])
    cols = len(data.curve_header.descriptors)
    curves = parser.las_data(data.curve_header)
    assert len(curves) == cols
    for curve in curves:
        assert len(curve.to_list()) == 9


    
if __name__ == "__main__":
    for test in tests:
        test()
