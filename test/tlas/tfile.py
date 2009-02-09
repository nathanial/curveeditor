from test.test_util import test
from las.file import *
from las.headers import *
from util import subdivide
from util import partial
import parser
from test import data

tests = []
test = partial(test, tests)
lpath = "test.las"

@test
def header_get_attributes():
    ch = data.curve_header
    assert ch.depth.unit == "m"
    assert ch.porosity.unit == "m3/m3"
    assert ch.porosity.description == "Gamma"
    assert ch.netgross.description == "NetGross"
    assert ch.depth.description == "trend"

@test
def header_attributes():
    wh = data.well_header
    assert wh.strt.data == "1499.8790000"
    assert wh.strt.unit == "m"
    assert wh.comp.description == "COMPANY"        

@test
def descriptor_to_las():
    d = Descriptor("DEPT", "m", None, "DEPTH")
    nd = parser.parse("descriptor", d.to_las())
    assert d == nd
    
@test
def data_to_las():
    ch = data.curve_header
    cols = len(ch.descriptors)
    data_rows = subdivide(parser.parse("data_rows", data.text['las_data']), cols)
    fields = LasField.from_rows(data_rows, ch)

    ndata_rows = subdivide(parser.parse("data_rows", LasField.to_las(fields)), cols)
    nfields = LasField.from_rows(ndata_rows, data.curve_header)
    assert fields == nfields

@test
def lasfile_to_las():
    ol = LasFile.from_(lpath)
    nl = parser.parse("las_file", ol.to_las())
    assert ol == nl
    
@test
def write_lasfile():
    lf =  LasFile.from_(lpath)
    lf.depth_field[0] = "yack"
    assert "yack" in lf.to_las()
    
if __name__ == "__main__":
    for test in tests:
        test()
