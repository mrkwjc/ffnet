# -*- coding: utf-8 -*-
from ffnet import *
from scipy import optimize

# Global containers to store and share data between processes 
nets = []
inputs = []
targets = []

# Data splitter function
def splitdata(N, nproc):
    n = N / nproc
    i = (nproc - N % nproc) * n
    idx = range(n, i, n) + range(i, N, n+1)
    idx1 = [0] + idx
    idx2 = idx + [N]
    return zip(idx1, idx2)

func = netprop.func
def procfunc(x, splitter, i):
    start, end = splitter
    net = nets[i]
    inp = inputs[i][start:end]
    trg = targets[i][start:end]
    return func(x, net.conec, net.bconecno, net.units, net.inno, net.outno, inp, trg)
def optfunc(x, pool, splitters, i):
    res = []
    for splitter in splitters:
        res += [pool.apply_async(procfunc, (x, splitter, i))]
    return sum([r.get() for r in res])

grad = netprop.grad
def procgrad(x, splitter, i):
    start, end = splitter
    net = nets[i]
    inp = inputs[i][start:end]
    trg = targets[i][start:end]
    return grad(x, net.conec, net.bconecno, net.units, net.inno, net.outno, inp, trg)
def optgrad(x, pool, splitters, i):
    res = []
    for splitter in splitters:
        res += [pool.apply_async(procgrad, (x, splitter, i))]
    return sum([r.get() for r in res])

class ffnet_multi(ffnet, object):
    def __init__(self, *args, **kwargs):
        # Call usual ffnet constructor
        super(ffnet_multi, self).__init__(*args, **kwargs)
        
        # Register net, input, target at topmost level containers
        global nets, inputs, targets
        self.identity = len(nets)
        nets += [self] 
        inputs += [[]]   # empty, will be filled by training routine
        targets += [[]]  # empty, will be filled by training routine
        
    def train_tnc_multi(self, input, target, nproc = None, **kwargs):        
        # register training data at module level
        # this have to be done *BEFORE* creating pool
        i = self.identity
        global inputs, targets
        input, target = self._setnorm(input, target)
        inputs[i] = input; targets[i] = target

        # create processing pool
        from multiprocessing import Pool, cpu_count
        if nproc is None: nproc = cpu_count()
        pool = Pool(nproc)
        
        # generate splitters for training data
        splitters = splitdata(len(input), nproc)
        
        # train
        if 'messages' not in kwargs: kwargs['messages'] = 0
        if 'bounds' not in kwargs: kwargs['bounds'] = ((-100., 100.),)*len(self.conec)
        res = optimize.fmin_tnc(optfunc, self.weights, fprime = optgrad, \
                                args = (pool, splitters, i), **kwargs)
        self.weights = res[0]
