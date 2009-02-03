from las.headers import *
from las.file import *
import parser
import helpers


curve_header = CurveHeader([
        Descriptor(mnemonic="DEPT", unit="m", description="DEPTH"),
        Descriptor(mnemonic="NetGross", description="NetGross"),
        Descriptor(mnemonic="Facies", description="Facies"),
        Descriptor(mnemonic="Porosity", unit="m3/m3", description="Gamma"),
        Descriptor(mnemonic="Gamma", unit="gAPI", description="Gamma"),
        Descriptor(mnemonic="DEPTH", unit="m", description="trend")])

well_header = WellHeader([
        Descriptor(mnemonic="STRT", unit="m", data="1499.8790000"),
        Descriptor(mnemonic="STOP", unit="m", data="2416.3790000"),
        Descriptor(mnemonic="COMP", description="COMPANY"),
        Descriptor(mnemonic="DATE", data="Monday, January 26 2009 14:04:02 : DATE")])


class TestHeaders(object):

    def test_get_attributes(self):
        ch = curve_header
        assert ch.depth.unit == "m"
        assert ch.porosity.unit == "m3/m3"
        assert ch.porosity.description == "Gamma"
        assert ch.netgross.description == "NetGross"
        assert ch.depth.description == "trend"
        print "tested get_attributes"

    def test_attributes(self):
        wh = well_header
        assert wh.strt.data == "1499.8790000"
        assert wh.strt.unit == "m"
        assert wh.comp.description == "COMPANY"        
        print "tested attributes"
        
    def run_tests(self):
        self.test_get_attributes()
        self.test_attributes()

class TestWriteLas(object):
    def test_header_to_las(self):
        ch = curve_header
        nch = parser.parse("curve_header", curve_header.to_las()) 
        assert curve_header == nch
        print "tested header_to_las"

    def test_descriptor_to_las(self):
        d = Descriptor("DEPT", "m",None,"DEPTH")
        nd = parser.parse("descriptor", d.to_las())
        assert d == nd
        print "tested descriptor_to_las"

    def test_data_to_las(self):
        data_rows = parser.divide_into_rows(parser.parse("data_rows", """
~Ascii
 1499.8790000 0.0000000000  -999.250000  -999.250000  -999.250000 1499.8790283
 1500.1290000 0.0000000000  -999.250000  -999.250000  -999.250000 1500.1290283
 1500.6290000 0.0000000000  -999.250000  -999.250000  -999.250000 1500.6290283
 1501.1290000 0.0000000000 0.0000000000 0.2706460059  -999.250000 1501.1290283
 1501.6290000 0.0000000000 0.0000000000 0.2674280107 78.869453430 1501.6290283
 1502.1290000 0.0000000000 0.0000000000 0.2560760081 78.008300781 1502.1290283
 1502.6290000 0.0000000000 0.0000000000 0.2421260029 75.581558228 1502.6290283 
"""), len(curve_header.descriptors))
        fields = LasField.rows_to_fields(data_rows,curve_header)
        ndata_rows = parser.divide_into_rows(parser.parse("data_rows", LasField.to_las(fields)), len(curve_header.descriptors))
        nfields = LasField.rows_to_fields(ndata_rows, curve_header)
        assert fields == nfields
        print "tested data_to_las"

    def test_las_file_to_las(self):
        ol = helpers.read_lasfile("test.las")
        nl = parser.parse("las_file", ol.to_las())

        assert ol == nl
        print "tested las_file_to_las"

    def test_writing(self):
        lf = helpers.read_lasfile("test.las")
        lf.depth_field.set_at(0,"yack")
        assert "yack" in lf.to_las()
        print "tested writing"
        
    def run_tests(self):
        self.test_descriptor_to_las()
        self.test_header_to_las()
        self.test_data_to_las()
        self.test_las_file_to_las()
        self.test_writing()
        

if __name__ == "__main__":
    TestHeaders().run_tests()
    TestWriteLas().run_tests()
        

