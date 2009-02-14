from test.test_util import test
from util import partial
from yacc_parser import LasLexer
from test import data

tests = []
test = partial(test, tests)

@test 
def test_descriptor_lexing():
    def lex(name):
        lexer = LasLexer()
        lexer.input(data.text['descriptors'][name])
        tokens = [tok for tok in lexer]
        types = map(lambda t: t.type, tokens)
        values = map(lambda t: t.value, tokens)
        return tokens, types, values

    tokens, types, values = lex('dept')
    print types
    print values
    assert types == ["WORD", "UNIT", "COLON", "WORD"]
    assert values == ["DEPT", "m", ":", "DEPTH"]

    tokens,types,values = lex('netgross')
    assert types == ["WORD", "DOT", "COLON", "WORD"]
    assert values == ["NetGross", ".", ":", "NetGross"]

    tokens,types,values = lex('stop')
    assert types == ["WORD", "UNIT", "NUMBER", "COLON"]
    assert values == ["STOP", "m", "2416.3790000", ":"]

    tokens,types,values = lex('porosity')
    assert types == ["WORD", "UNIT", "COLON", "WORD"]
    assert values == ["Porosity", "m3/m3", ":", "Porosity"]

    tokens,types,values = lex('date')
    assert types == ["WORD", "DOT", "DATA", "COLON", "WORD"]
    assert values == ["DATE", ".", "Monday, January 26 2009 14:04:02", ":", "DATE"]

    

@test
def test_version_header():
    lexer = LasLexer()
    lexer.input(data.text['version_header'])
    tokens = [tok for tok in lexer]
    assert tokens[0].type == "VERSION_START"
    assert tokens[2].value == "VERS"
    assert tokens[4].value == "2.0"
    assert tokens[6].value == "WRAP"
    assert tokens[8].value == "NO"
    
@test
def test_well_header():
    lexer = LasLexer()
    lexer.input(data.text['well_header'])
    tokens = [tok for tok in lexer]
    assert tokens[0].type == "WELL_START"

@test
def test_curve_header():
    lexer = LasLexer()
    lexer.input(data.text['curve_header'])
    tokens = [tok for tok in lexer]
        
    assert tokens[0].type == "CURVE_START"

@test
def test_las_data():
    lexer = LasLexer()
    lexer.input(data.text['las_data'])
    tokens = [tok for tok in lexer]
    assert tokens[0].type == "DATA_START"

if __name__ == "__main__":
    for test in tests:
        test()
