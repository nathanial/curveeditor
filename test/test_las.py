from las.headers import *
from las.file import *

curve_header = CurveHeader([
        Descriptor(mnemonic="DEPT", unit="m", description="DEPTH"),
        Descriptor(mnemonic="NetGross", description="NetGross"),
        Descriptor(mnemonic="Facies", description="Facies"),
        Descriptor(mnemonic="Porosity", unit="m3/m3", description="Gamma"),
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
    def __init__(self):
        pass


if __name__ == "__main__":
    TestHeaders().run_tests()
        
        

        
        
        
        
            
