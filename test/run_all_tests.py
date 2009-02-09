from test.tlas import tfile, theaders, tparser
from util import each

def run_tests(suite):
    for test in suite.tests:
        test()

each([tfile,theaders,tparser], run_tests)
