from test.test_util import test
from util import partial
import parser
from test import data

tests = []
test = partial(test, tests)

@test 
def test_to_las():
    ch = data.curve_header
    nch = parser.parse("curve_header", ch.to_las())
    assert ch == nch

if __name__ == "__main__":
    for test in tests:
        test()
