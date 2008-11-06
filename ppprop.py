import pp
import fortran
from numpy import array, zeros

jobserver = pp.Server(3)

def _normcall2(*args): return fortran._ffnet.normcall2(*args)
tnormcall2 = pp.Template(jobserver, _normcall2, modules=('fortran',))

def _func(*args): 
    return fortran._ffnet.func(*args)
tfunc = pp.Template(jobserver, _func, modules=('fortran',))

def _grad(*args): return fortran._ffnet.grad(*args)
tgrad = pp.Template(jobserver, _grad, modules=('fortran',))


#######################################3
def _divide(inp):
    n = jobserver.get_ncpus()
    linp = len(inp)
    sec = linp/n
    idx = []
    for i in xrange(n):
        ims = i*sec
        if i == sec-1:
            idx += [slice(ims, None)]
        else:
            idx += [slice(ims, ims + sec)]
    return idx
    
def normcall2(*args):
    n = jobserver.get_ncpus()
    inp = args[-1]
    if len(inp) < n: return fortran._ffnet.normcall2(*args)
    idx = _divide(inp)
    # Submit jobs
    cargs = args[:-1] #*args without input
    jobs = []
    for i in idx:
        iargs = cargs + (inp[i],)
        jobs += [ tnormcall2.submit(*iargs) ]
    # Recieve results
    nout = len(args[4]) #outno
    out = zeros((len(inp), nout))
    for k, i in enumerate(idx):
        out[i] = jobs[k]()
    return out

def func(*args):
    n = jobserver.get_ncpus()
    inp = args[-2]; trg = args[-1]
    if len(inp) < n: return fortran._ffnet.func(*args)
    idx = _divide(inp)
    # Submit jobs
    cargs = args[:-2] #*args without input
    jobs = []
    for i in idx:
        iargs = cargs + (inp[i], trg[i])
        jobs += [ tfunc.submit(*iargs) ]
    # Recieve results
    out = 0.
    for job in jobs: out += job()
    return out
        
def grad(*args):
    n = jobserver.get_ncpus()
    inp = args[-2]; trg = args[-1]
    if len(inp) < n: return fortran._ffnet.grad(*args)
    idx = _divide(inp)
    # Submit jobs
    cargs = args[:-2] #*args without input
    jobs = []
    for i in idx:
        iargs = cargs + (inp[i], trg[i])
        jobs += [ tgrad.submit(*iargs) ]
    # Recieve results
    out = 0.
    for job in jobs: out += job()
    return out



#~ from ffnet import ffnet, mlgraph
#~ net = ffnet(mlgraph((2,2,2)))

#~ inp = array([[1,1],[2,2],[3,3],[4,4],[5,5]])
#~ trg = array([[1,1],[2,2],[3,3],[4,4],[5,5]])

#~ args = (net.weights, net.conec, net.units, \
                            #~ net.inno, net.outno, net.eni, net.deo, inp)
#~ args2 = (net.weights, net.conec, net.bconecno, net.units, \
                            #~ net.inno, net.outno, inp, trg)
#~ print normcall2(*args)
#~ print func(*args2)
#~ print grad(*args2)
