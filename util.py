
def lfind(ls, pred):
    for i in range(0, len(ls)):
        if pred(ls[i]): return ls[i]

def interleave(*args):
    for idx in range(0, max(len(arg) for arg in args)):
        for arg in args:
            try:
                yield arg[idx]
            except IndexError:
                continue

def tuplize(*args):
    return [[arg[idx] for arg in args] for idx in range(0, max(len(arg) for arg in args))]

def each(ls, fn):
    for i in range(0, len(ls)):
        fn(i)

def times(num, fn):
    for i in range(0,num):
        fn(i)
