from test.test_util import test
from util import partial
from yacc_parser import LasLexer
from test import data

tests = []
test = partial(test, tests)

@test 
def test_descriptor_lexing():
    def lex_from(n):
        lexer = LasLexer()
        lexer.input(data.text['descriptors'][n])
        tokens = [tok for tok in lexer]
        types = map(lambda t: t.type, tokens)
        values = map(lambda t: t.value, tokens)
        return tokens, types, values

    tokens, types, values = lex_from(0)
    assert types == ["WORD", "DOT", "WORD", "COLON", "WORD"]
    assert values == ["DEPT", ".", "m", ":", "DEPTH"]

    tokens,types,values = lex_from(1)
    assert types == ["WORD", "DOT", "COLON", "WORD"]
    assert values == ["NetGross", ".", ":", "NetGross"]

    tokens,types,values = lex_from(7)
    assert types == ["WORD", "DOT", "WORD", "NUMBER", "COLON"]
    assert values == ["STOP", ".", "m", 2416.3790000, ":"]

    tokens,types,values = lex_from(3)
    assert types == ["WORD", "DOT", "WORD", "COLON", "WORD"]
    assert values == ["Porosity", ".", "m3/m3", ":", "Porosity"]

@test
def test_version_header():
    lexer = LasLexer()
    lexer.input(data.text['version_header'])
    tokens = [tok for tok in lexer]
    assert tokens[0].type == "VERSION_START"
    assert tokens[2].value == "VERS"
    assert tokens[4].value == 2.0
    assert tokens[6].value == "WRAP"
    assert tokens[8].value == "NO"
    
@test
def test_well_header():
    lexer = LasLexer()
    lexer.input(data.text['well_header'])
    tokens [tok for tok in lexer]


@test
def test_curve_header():
    lexer = LasLexer()
    lexer.input(data.text['curve_header'])
    tokens = [tok for tok in lexer]
    assert tokens[0].type == "CURVE_START"
    for tok in tokens: print tok
    print

@test
def test_las_data():
    lexer = LasLexer()
    lexer.input(data.text['las_data'])
    for tok in lexer:
        print tok
    print



if __name__ == "__main__":
    for test in tests:
        test()
