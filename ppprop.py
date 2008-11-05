import pp
import fortran
from numpy import array, zeros

jobserver = pp.Server()

def normcall2(*args):
    return fortran._ffnet.normcall2(*args)
normcall2_template = pp.Template(jobserver, normcall2, modules=('fortran',))

class PPProp:
    def __init__(self, *args, **kwargs):
        self.server = jobserver #pp.Server(*args, **kwargs)
    
    def _divide(self, inp):
        n = self.server.get_ncpus()
        linp = len(inp)
        sec = linp/n
        idx = [0]
        for i in xrange(1, sec): idx += [i*sec]
        idx += [linp]
        return idx
    
    def normcall2(self, *args):
        n = self.server.get_ncpus()
        inp = args[-1]
        if len(inp) < n: return fortran._ffnet.normcall(*args)
        idx = self._divide(inp)
        
        linp = len(inp)
        nout = len(args[4]) #outno
        cargs = args[:-1]
        if linp < n: 
            return _ffnet.normcall(*args)
        else:
            sec = linp/n
            idx = [0]
            for i in xrange(1, sec): idx += [i*sec]
            idx += [linp]
        # Submit jobs
        jobs = []
        for i in xrange(sec):
            dat = inp[idx[i]:idx[i+1]]
            jobs += [self.server.submit(normcall2, cargs + (dat,), modules=('fortran',))] #(), ('_ffnet',))]
        # Recieve results
        out = zeros((linp, nout))
        for i in xrange(sec):
            out[idx[i]:idx[i+1]] = jobs[i]()
        return out

P = PPProp()
from ffnet import ffnet, mlgraph
net = ffnet(mlgraph((2,2,1)))


inp = array([[1,1],[2,2],[3,3],[4,4],[5,5]])
args = (net.weights, net.conec, net.units, \
                            net.inno, net.outno, net.eni, net.deo, inp)
                            
print P.normcall2(*args)
