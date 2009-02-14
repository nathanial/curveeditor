from test.test_util import test
from util import partial
from my_parser import Parser
from test import data

tests = []
test = partial(test, tests)

@test 
def test_to_las():
    ch = data.curve_header
    parser = Parser(ch.to_las())
    nch = parser.curve_header()
    assert ch == nch

if __name__ == "__main__":
    for test in tests:
        test()
