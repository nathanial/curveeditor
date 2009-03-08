from __future__ import with_statement
def lfind(ls, pred):
    for i in range(0, len(ls)):
        if pred(ls[i]): return ls[i]

def lindex(ls, pred):
    for i in range(0, len(ls)):
        if pred(ls[i]): return i
        
def interleave(*args):
    for idx in range(0, max(len(arg) for arg in args)):
        for arg in args:
            try:
                yield arg[idx]
            except IndexError:
                continue

def tuplize(*args):
    return [[arg[idx] for arg in args] for idx in range(0, max(len(arg) for arg in args))]

def times(num, fn):
    for i in range(0,num):
        fn(i)

def each(ls, fn):
    for l in ls:
        fn(l)

def subdivide(ls, increment):
    acc = []
    cursor = 0
    while cursor < len(ls):
        acc.append(ls[cursor:(cursor+increment)])
        cursor += increment
    return acc

def forall(ls, pred):
    return not lfind(ls, lambda e: not pred(e))

def ident(x): return x

def assertAll(*conditions):
    assert forall(conditions, ident)

def read_file(path):
    text = ""
    with open(path) as f:
        for line in f:
            text += line
    return text

def partial(fn, *args):
    def p(*rest):
        total = args + rest
        return fn(*total)
    return p

def fixed_point(data, fn):
    return data == fn(data)
    
def float_eq(a,b):
    return a - b < 0.001

def swap(ls, old, new):
    index = ls.index(old)
    ls[index] = new        
def cmp_min(x,y):
    if x > y:
        return 1
    elif x == y:
        return 0
    else:
        return -1
        
def cmp_max(x,y):
    return -1 * cmp_min(x,y)

def save_plot(plot):
    from gui.plots import PlotCanvas
    plot_canvas = PlotCanvas(ymin=plot.ymin(),
                             ymax=plot.ymax(),
                             yinc=(plot.ymax() - plot.ymin()))
    plot_canvas.add_plot(plot)
    filename = "tmp/" + plot.name() + ".png"
    plot_canvas.fig.savefig(filename)
    plot_canvas.remove_plot(plot)
    return filename

def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)
