def test(tests, method):
    mname = method.__name__
    def f():
        print "start testing %s" % mname
        method()
        print "finished testing %s" % mname
    tests.append(f)
    return f    

