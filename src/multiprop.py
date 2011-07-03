from multiprocessing import Pool, cpu_count
from numpy import split

from fortran import _ffnet as netprop
def prop(*args): return netprop.func(*args)
def grad(*args): return netprop.grad(*args)


nproc = cpu_count()
pool = Pool()

def splitdata(inp, trg):
    N = len(inp)
    n = N / nproc
    i = (nproc - N % nproc) * n
    idx = range(n, i, n) + range(i, N, n+1)
    return zip(split(inp, idx), split(trg, idx))

def func(*args):
    args0 = args[:-1]
    data = args[-1]
    res = []
    for d in data:
        res.append(pool.apply_async(prop, args0 + d))
    f = sum([r.get() for r in res])
    return f
    
def fprime(*args):
    args0 = args[:-1]
    data = args[-1]
    res = []
    for d in data:
        res.append(pool.apply_async(grad, args0 + d))
    f = sum([r.get() for r in res])
    return f