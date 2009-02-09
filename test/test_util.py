def test(tests, method):
    mname = method.__name__
    def f():
        method()
        print "tested %s" % mname
    tests.append(f)
    return f    

