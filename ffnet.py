########################################################################
##  Copyright (C) 2006 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################

'''
ffnet - feed-forward neural network for python. 

See ffnet main class description for usage hints or go to
http://ffnet.sourceforge.net for docs and examples.
'''

from version import version
from scipy import array, zeros, ones, random, optimize, sqrt
import networkx as NX
from fortran import _ffnet as netprop
from pikaia import pikaia

def mlgraph(arch, biases = True):
    '''
    Creates standard multilayer network with full connectivity list.
    '''
    nofl = len(arch)
    conec = []
    if nofl: trg = arch[0]
    for l in xrange(1, nofl):
        layer = arch[l]
        player = arch[l-1]
        srclist = range(trg-player+1, trg+1)
        if biases: srclist += [0]
        for i in xrange(layer):
            trg += 1
            for src in srclist:
                conec.append((src, trg))
    return conec

def imlgraph(arch, biases = True):
    '''
    Creates special layered network where outputs are
    independent from each other.
    Exemplary architecture definition:
    arch = (3, [(4,), (), (6, 3)], 3).
    With such an arch, imlgraph builds three independent
    multilayer graphs: 3-4-1, 3-1, 3-6-3-1
    and merges them into one graph with common input nodes.
    
    Simplified version of the above architecture syntax is:
    arch = (3, 3, 3)  #exactly as in the mlgraph
    Three nets: 3-3-1, 3-3-1, 3-3-1 are merged in this case.
    '''
    #Checks of the architecture
    if len(arch) < 3:
        raise TypeError("Wrong architecture definition (at least 3 layers needed).")
    if isinstance(arch[1], int):
        arch = tuple(arch)
        arch = arch[:1] + tuple([[ arch[1:-1] ] * arch[-1]]) + arch[-1:]
    elif isinstance(arch[1], (list, tuple)):
        if len(arch[1]) != arch[2]:
            raise TypeError("Length of arch[1] should be equal to arch[2].")
    else: raise TypeError("Wrong architecture definition.")
    
    #Merging function
    def merge(conec, conec_tmp, nofi):
        from scipy import array, where
        try:
            trans = array(conec).max() - nofi
            tmp = array(conec_tmp)
            tmp = where(tmp > nofi, tmp + trans, tmp)
            conec_tmp = [ tuple(c) for c in tmp ]
            return conec + conec_tmp
        except ValueError:
            return conec_tmp
        
    nofi = arch[0]
    inps = arch[:1]
    outs = (1,)
    conec = []
    for hids in arch[1]:
        arch_tmp = tuple(inps) + tuple(hids) + tuple(outs)
        conec_tmp = mlgraph(arch_tmp, biases=biases)
        conec = merge(conec, conec_tmp, nofi)
    return conec

def tmlgraph(arch, biases = True):
    '''
    Creates multilayer network full connectivity list,
    but now layers have connections with all preceding layers
    (not only the first one)
    '''
    nofl = len(arch)
    conec = []; srclist = []
    if biases: srclist = [0]
    if nofl: trg = arch[0]
    for l in xrange(1, nofl):
        layer = arch[l]
        player = arch[l-1]
        srclist += range(trg-player+1, trg+1)
        for i in xrange(layer):
            trg += 1
            for src in srclist:
                conec.append((src, trg))
    return conec

def linear(a, b, c, d):
    '''
    Returns coefficients of linear map from range (a,b) to (c,d)
    '''
    #if b == a: raise ValueError("Mapping not possible due to equal limits")
    if b == a: 
        c1 = 0.0
        c2 = ( c + d ) / 2.
    else:
        c1 = ( d - c ) / ( b - a )
        c2 = c - a * c1
    return c1, c2

def norms(inarray, lower = 0., upper = 1.):
    '''
    Gets normalization information from an array,for use in ffnet class.
    (lower, upper) is a range of normalisation.
    inarray is 2-dimensional and normalisation parameters are computed
    for each column...
    '''
    limits = []; en = []; de = []
    inarray = array(inarray).transpose()
    for col in inarray:
        maxarr = max(col)
        minarr = min(col)
        limits += [(minarr, maxarr)]
        en += [linear(minarr, maxarr, lower, upper)]
        de += [linear(lower, upper, minarr, maxarr)]
    return array(limits), array(en), array(de)
    
def normarray(inarray, coeff):
    ''' 
    Normalize 2-dimensional array linearly column by column 
    with provided coefficiens.
    '''
    #if coeff is not None:
    inarray = array(inarray).transpose()
    coeff = array(coeff)
    i = inarray.shape[0]
    for ii in xrange(i):
        inarray[ii] = inarray[ii] * coeff[ii,0] + coeff[ii,1]
    return inarray.transpose()
    #else: print "Lack of normalization parameters. Nothing done."

def ffconec(conec):
    """
    Checks if conec is acyclic, sorts it if necessary and returns tuple:
    (conec, inno, hidno, outno) where:
    conec - sorted input connectivity
    inno/hidno/outno  - lists of input/hidden/ouput units
    """
    if len(conec) == 0: raise ValueError("Empty connectivity list")
    graph = NX.DiGraph()
    graph.add_edges_from(conec)
    snodes = NX.topological_sort(graph)
    if not snodes:
        raise TypeError("Network has cycles.")
    else:
        conec = []; inno = []; hidno = []; outno = []
        for node in snodes:
            ins = graph.in_edges(node)
            outs = graph.out_edges(node)
            if not ins and node != 0 :  # biases handling
                inno += [node]
            else:
                conec += ins   #Maybe + [(0,node)] i.e. bias
                if not outs: outno += [node]
                else: 
                    if node != 0: hidno += [node] #bias handling again
    return graph, conec, inno, hidno, outno

def bconec(conec, inno):
    """
    Returns list of adjoint graph (for backprop) edges positions
    in conec. Conec is assumed to be acyclic.
    """
    bgraph = NX.DiGraph()
    bgraph.add_edges_from(conec)
    bgraph = bgraph.reverse()
    bgraph.delete_nodes_from(inno)
    try: bgraph.delete_node(0) #handling biases
    except: pass
    bsnodes = NX.topological_sort(bgraph)
    bconecno = []
    for bnode in bsnodes:
        for bedge in bgraph.in_edges(bnode):
            edge = (bedge[1], bedge[0])
            idx = conec.index(edge) + 1
            bconecno.append(idx)
    return bgraph, bconecno
    
def dconec(conec, inno):
    """
    Return list of edges positions (in conec) of graphs for
    derivative calculation, all packed in one list (dconecno). Additionaly
    beginings of each graph in this list is returned (dconecmk)
    """
    dgraphs = []; dconecno = []; dconecmk = [0]
    for idx, i in enumerate(inno):
        dgraph = NX.DiGraph()
        dgraph.add_edges_from(conec)
        dgraph.delete_nodes_from(inno[0:idx])
        dgraph.delete_nodes_from(inno[idx+1:])
        try: dgraph.delete_node(0)  #handling biases
        except: pass
        dsnodes = NX.topological_sort(dgraph)
        for dnode in dsnodes:
            for dedge in dgraph.in_edges(dnode):
                idx = conec.index(dedge) + 1
                dconecno.append(idx)
        dgraphs.append(dgraph)
        dconecmk.append(len(dconecno))
    return dgraphs, dconecno, dconecmk

class ffnet:
    """
    Feed-forward neural network implementation.
    
    NETWORK CREATION:
    Base creation of the network consist in delivering list of connections:
        coneclist = [[1, 3], [2, 3], [0, 3] 
                     [1, 4], [2, 4], [0, 4] 
                     [3, 5], [4, 5], [0, 5]]
        n = ffnet(coneclist)
    0 in coneclist is a special unit representing bias. If there is
    no connection from 0, bias is not considered in the node.
    Only feed-forward directed graphs are allowed. Class makes check
    for cycles in the provided graph and raises TypeError if any.
    All nodes (exept input ones) have sigmoid activation function.

    Generation of coneclist is left to the user. There are however
    functions: mlgraph and tmlgraph provided to generate coneclist for layered network.
    See description of these functions.
    More architectures may be provided in the future.
    
    Weights are automatically initialized at the network creation. They can
    be reinitialized later with 'randomweights' method.
    
    TRAINING NETWORK:
    There are several training methods included, currently:
    train_genetic, train_cg, train_bfgs, train_tnc.
    The simplest usage is, for example:
        n.train_tnc(input, target)
    where 'input' and 'target' is raw data to be learned. Class performs data
    normalization by itself and records encoding/decoding information to be used
    during network recalling.
    Class makes basic checks of consistency of data.
    
    For information about training prameters see appropriate method description.
    
    RECALLING NETWORK:
    Usage of the trained network is an simple as function call:
        ans = n(inp)
    or, alternatively:
        ans = n.call(inp)
    where 'inp' - list of network inputs and 'ans' - array of network outputs
    There is also possibility to retrieve partial derivatives of output vs. input
    at given input point:
        deriv = n.derivative(inp)
    Output 'deriv' is an array of the form:
        | o1/i1, o1/i2, ..., o1/in |
        | o2/i1, o2/i2, ..., o2/in |
        | ...                      |
        | om/i1, om/i2, ..., om/in |
    
    LOADING/SAVING NETWORK
    There are provided two helper functions with this class: savenet and loadnet.
    Usage:
        savenet(n, "filename")
        n = loadnet("filename")
    These functions use internally cPickle module.
    
    PLOTS
    If you have matplotlib installed, the network architecture can be drawn with:
        import networkx, pylab
        networkx.draw_circular(n.graph)
        pylab.show()
    This is a very basic solution, network is drawn with circular layout.
    """
    def __init__(self, conec):
        #~ if 'biases' in kwargs: biases = kwargs['biases']
        #~ else: biases = True
            
        #~ if 'conec'  in kwargs: conec = kwargs['conec']
        #~ elif 'mlp'  in kwargs: conec = mlgraph(kwargs['mlp'], biases = biases)
        #~ elif 'tmlp' in kwargs: conec = tmlgraph(kwargs['tmlp', biases = biases])
        #~ else: raise TypeError("Wrong network definition")
    
        graph, conec, inno, hidno, outno = ffconec(conec)
        bgraph, bconecno = bconec(conec, inno)
        dgraphs, dconecno, dconecmk = dconec(conec, inno)
        self.graph = graph
        self.bgraph = bgraph
        self.dgraphs = dgraphs
        self.conec = array(conec)
        self.inno = array(inno)
        self.hidno = array(hidno)
        self.outno = array(outno)
        self.bconecno = array(bconecno)
        self.dconecno = array(dconecno)
        self.dconecmk = array(dconecmk)
        #max(graph) below needed if graph lacks some numbers
        self.units = zeros(max(graph), 'd')
        # initialize weights
        self.randomweights()
        # set initial normalization parameters
        self._setnorm()
        
    def __repr__(self):
        info = "Feed-forward neural network: \n" + \
               "inputs:  %4i \n" %(len(self.inno)) + \
               "hiddens: %4i \n" %(len(self.hidno)) + \
               "outputs: %4i \n" %(len(self.outno)) + \
               "connections and biases: %4i" %(len(self.conec)) 
        return info
    
    def __call__(self, inp):
        output = netprop.normcall(self.weights, self.conec, self.units, \
                                  self.inno, self.outno, self.eni, self.deo, inp)
        return output.tolist()
    
    def call(self, inp):
        """Returns network answer to input sequence
        """
        return self.__call__(inp)

    def derivative(self, inp):
        """Returns partial derivatives of the network's 
           output vs. its input at given input point
           in the following array:
               | o1/i1, o1/i2, ..., o1/in |
               | o2/i1, o2/i2, ..., o2/in |
               | ...                      |
               | om/i1, om/i2, ..., om/in |
        """

        deriv = netprop.normdiff(self.weights, self.conec, self.dconecno, self.dconecmk, \
                                 self.units, self.inno, self.outno, self.eni, self.ded, inp)
        return deriv.tolist()
        
    def sqerror(self, input, target):
        """
        Returns 0.5*(sum of squared errors at output)
        for input and target arrays being first normalized.
        Might be slow in frequent use, because data normalization is
        performed at ach call.
        (_setnorm should be called before sqerror - will be changed)
        """
        input, target = self._testdata(input, target)
        input = normarray(input, self.eni) #Normalization data might be uninitialized here!
        target = normarray(target, self.eno)
        err  = netprop.sqerror(self.weights, self.conec, self.units, \
                               self.inno, self.outno, input, target)
        return err
    
    def sqgrad(self, input, target):
        """
        Returns gradient of sqerror vs. network weights.
        Input and target arrays are first normalized.
        Might be slow in frequent use, because data normalization is
        performed at each call.
        (_setnorm should be called before sqgrad - will be changed)
        """
        input, target = self._testdata(input, target) 
        input = normarray(input, self.eni) #Normalization data might be uninitialized here!
        target = normarray(target, self.eno)
        g  = netprop.grad(self.weights, self.conec, self.bconecno, self.units, \
                          self.inno, self.outno, input, target)
        return g
    
    def randomweights(self):
        """Randomize weights due to Bottou proposition"""
        nofw = len(self.conec)
        weights = zeros(nofw, 'd')
        for w in xrange(nofw):
            trg = self.conec[w,1]
            n = len(self.graph.predecessors(trg))
            bound = 2.38 / sqrt(n)
            weights[w] = random.uniform(-bound, bound)
        self.weights = weights
        self.trained = False

    def _testdata(self, input, target):
        """Tests input and target data"""
        # Test conversion
        try: input = array(input, 'd')
        except: raise ValueEror("Input cannot be converted to numpy array")
        try: target = array(target, 'd')
        except: raise ValueEror("Target cannot be converted to numpy array")
        
        #Convert 1-d arrays to 2-d (this allows to put 1-d arrays
        #for training if we have one input and/or one output
        if len(self.inno) == 1 and len(input.shape) == 1:
            input = input.reshape( (input.shape[0], 1) )
        if len(self.outno) == 1 and len(target.shape) == 1:
            target = target.reshape( (target.shape[0], 1) )        

        #Test some sizes
        numip = input.shape[0]; numop = target.shape[0]
        if numip != numop:
            raise ValueError \
            ("Data not aligned: input patterns %i, target patterns: %i" %(numip, numop))
        numi = len(self.inno); numiv = input.shape[1]
        if numiv != numi:
            raise ValueError \
            ("Inconsistent input data, input units: %i, input values: %i" %(numi, numiv))
        numo = len(self.outno); numov = target.shape[1]
        if numov != numo:
            raise ValueError \
            ("Inconsistent target data, target units: %i, target values: %i" %(numo, numov))
        
        return input, target

    def _setnorm(self, input = None, target = None):
        """Retrieves normalization info from training data and normalizes data"""
        numi = len(self.inno); numo = len(self.outno)
        if input is None and target is None:
            self.inlimits  = array( [[0.15, 0.85]]*numi ) #informative only
            self.outlimits = array( [[0.15, 0.85]]*numo ) #informative only
            self.eni = self.dei = array( [[1., 0.]] * numi )
            self.eno = self.deo = array( [[1., 0.]] * numo )
            self.ded = ones((numo, numi), 'd')
        else:
            input, target = self._testdata(input, target)
            
            # Warn if any input or target node takes a one single value
            # I'm still not sure where to put this check....
            for i, col in enumerate(input.transpose()):
                if max(col) == min(col):
                    print "Warning: %ith input node takes always a single value of %f." %(i+1, max(col))

            for i, col in enumerate(target.transpose()):
                if max(col) == min(col):
                    print "Warning: %ith target node takes always a single value of %f." %(i+1, max(col))
            
            #limits are informative only, eni,dei/eno,deo are input/output coding-decoding
            self.inlimits, self.eni, self.dei = norms(input, lower=0.15, upper=0.85)
            self.outlimits, self.eno, self.deo = norms(target, lower=0.15, upper=0.85)
            self.ded = zeros((numo,numi), 'd')
            for o in xrange(numo):
                for i in xrange(numi):
                    self.ded[o,i] = self.eni[i,0] * self.deo[o,0]
            return normarray(input, self.eni), normarray(target, self.eno)

    def train_momentum(self, input, target, eta = 0.2, momentum = 0.8, \
                        maxiter = 10000, disp = 0):
        """
        Simple backpropagation training with momentum.
    
        Allowed parameters:
        eta             - descent scaling parameter (default is 0.2)
        momentum        - momentum coefficient (default is 0.8)
        maxiter         - the maximum number of iterations (default is 10000)
        disp            - print convergence message if non-zero (default is 0)
        """
        input, target = self._setnorm(input, target)
        if disp:
            err  = netprop.sqerror(self.weights, self.conec, self.units, \
                                   self.inno, self.outno, input, target)
            print "Initial error --> 0.5*(sum of squared errors at output): %.15f" %err
        self.weights = netprop.momentum(self.weights, self.conec, self.bconecno, \
                                        self.units, self.inno, self.outno, input, \
                                        target, eta, momentum, maxiter)
        if disp:
            err  = netprop.sqerror(self.weights, self.conec, self.units, \
                                   self.inno, self.outno, input, target)
            print "Final error   --> 0.5*(sum of squared errors at output): %.15f" %err

    def train_rprop(self, input, target, \
                    a = 1.2, b = 0.5, mimin = 0.000001, mimax = 50., \
                    xmi = 0.1, maxiter = 10000, disp = 0):
        """
        Rprop training algorithm.
        
        Allowed parameters:
        a               - training step increasing parameter (default is 1.2)
        b               - training step decreasing parameter (default is 0.5)
        mimin           - minimum training step (default is 0.000001)
        mimax           - maximum training step (default is 50.)
        xmi             - vector indicating initial training step for weights,
                          if 'xmi' is a scalar then its value is set for all
                          weights (default is 0.1)
        maxiter         - the maximum number of iterations (default is 10000)
        disp            - print convergence message if non-zero (default is 0)
        
        Method updates network weights and returns 'xmi' vector 
        (after 'maxiter' iterations).
        """
        input, target = self._setnorm(input, target)
        if type(xmi).__name__ in ['float', 'int']:
            xmi = [ xmi ]*len(self.conec)
        
        if disp:
            err  = netprop.sqerror(self.weights, self.conec, self.units, \
                                   self.inno, self.outno, input, target)
            print "Initial error --> 0.5*(sum of squared errors at output): %.15f" %err
        self.weights, xmi = netprop.rprop(self.weights, self.conec, self.bconecno, \
                                          self.units, self.inno, self.outno, input, \
                                          target, a, b, mimin, mimax, xmi, maxiter)
        if disp:
            err  = netprop.sqerror(self.weights, self.conec, self.units, \
                                   self.inno, self.outno, input, target)
            print "Final error   --> 0.5*(sum of squared errors at output): %.15f" %err
        return xmi

    def train_genetic(self, input, target, **kwargs):
        """
        Global weights optimization with genetic algorithm.
    
        Allowed parameters:
        lower        - lower bound of weights values (default is -25.)
        upper        - upper bound of weights values (default is 25.)
        individuals  - number of individuals in a population (default
                       is 20)
        generations  - number of generations over which solution is
                       to evolve (default is 500)
        crossover    - crossover probability; must be  <= 1.0 (default
                       is 0.85). If crossover takes place, either one
                       or two splicing points are used, with equal
                       probabilities
        mutation     - 1/2/3/4/5 (default is 2)
                       1=one-point mutation, fixed rate
                       2=one-point, adjustable rate based on fitness
                       3=one-point, adjustable rate based on distance
                       4=one-point+creep, fixed rate
                       5=one-point+creep, adjustable rate based on fitness
                       6=one-point+creep, adjustable rate based on distance
        initrate     - initial mutation rate; should be small (default
                       is 0.005) (Note: the mutation rate is the proba-
                       bility that any one gene locus will mutate in
                       any one generation.)
        minrate      - minimum mutation rate; must be >= 0.0 (default
                       is 0.0005)
        maxrate      - maximum mutation rate; must be <= 1.0 (default
                       is 0.25)
        fitnessdiff  - relative fitness differential; range from 0
                       (none) to 1 (maximum).  (default is 1.)
        reproduction - reproduction plan; 1/2/3=Full generational
                       replacement/Steady-state-replace-random/Steady-
                       state-replace-worst (default is 3)
        elitism      - elitism flag; 0/1=off/on (default is 0)
                       (Applies only to reproduction plans 1 and 2)
        verbosity    - printed output 0/1/2=None/Minimal/Verbose
                       (default is 0)
    
        Note: this optimization routine is a python port of fortran pikaia code.
    
        For more info see pikaia homepage and documentation:
        http://www.hao.ucar.edu/Public/models/pikaia/pikaia.html
        """
        input, target = self._setnorm(input, target)
        lower = -25.
        upper =  25.
        if 'lower' in kwargs: lower = kwargs['lower']; del kwargs['lower']
        if 'upper' in kwargs: upper = kwargs['upper']; del kwargs['upper']
        if lower >= upper: raise ValueError("Wrong weights range: (%f, %f)" %(lower, upper))
        if 'individuals' not in kwargs: kwargs['individuals'] = 20
        func = netprop.pikaiaff
        n = len(self.weights)
        extra_args = (self.conec, self.units, self.inno,
                      self.outno, input, target, lower, upper)
        self.weights = pikaia(func, n, extra_args, **kwargs)
        self.weights = netprop.vmapa(self.weights, 0., 1., lower, upper)
        self.trained = 'genetic'
    
    def train_cg(self, input, target, **kwargs):
        """
        Train network with conjugate gradient algorithm using the
        nonlinear conjugate gradient algorithm of Polak and Ribiere.
        See Wright, and Nocedal 'Numerical Optimization', 1999, pg. 120-122.

        Allowed parameters:
        gtol         - stop when norm of gradient is less than gtol
                       (default is 1e-5)
        norm         - order of vector norm to use (default is infinity)
        maxiter      - the maximum number of iterations (default is 10000)
        disp         - print convergence message at the end of training
                       if non-zero (default is 1)
    
        Note: this procedure does not produce any output during training.
        Note: optimization routine used here is part of scipy.optimize.
        """
        if 'maxiter' not in kwargs: kwargs['maxiter'] = 10000
        input, target = self._setnorm(input, target)
        func = netprop.func
        fprime = netprop.grad
        extra_args = (self.conec, self.bconecno, self.units, \
                           self.inno, self.outno, input, target)
        self.weights = optimize.fmin_cg(func, self.weights, fprime=fprime, \
                                        args=extra_args, **kwargs)
        self.trained = 'cg'

    def train_bfgs(self, input, target, **kwargs):
        """
        Train network with constrained version of quasi-Newton method
        of Broyden, Fletcher, Goldfarb, and Shanno (BFGS). Algorithm is
        called L_BFGS_B.
    
        Allowed parameters:
        bounds  -- a list of (min, max) pairs for each weight, defining
                   the bounds on that parameter. Use None for one of min or max
                   when there is no bound in that direction. At default all weights
                   are bounded to (-100, 100)
        m       -- the maximum number of variable metric corrections
                   used to define the limited memory matrix. (the limited memory BFGS
                   method does not store the full hessian but uses this many terms in an
                   approximation to it). Default is 10.
        factr   -- The iteration stops when
                   (f^k - f^{k+1})/max{|f^k|,|f^{k+1}|,1} <= factr*epsmch
                   where f is current cost function value and
                   epsmch is the machine precision, which is automatically
                   generated by the code. Typical values for factr: 1e12 for
                   low accuracy; 1e7 for moderate accuracy; 10.0 for extremely
                   high accuracy. Default is 1e7.
        pgtol   -- The iteration will stop when
                   max{|proj g_i | i = 1, ..., n} <= pgtol
                   where pg_i is the ith component of the projected gradient.
                   Default is 1e-5.
        iprint  -- controls the frequency of output. <0 means no output.
                   Default is -1.
        maxfun  -- maximum number of cost function evaluations. Default is 15000.
    
        Note: optimization routine used here is part of scipy.optimize.
        Note: there exist copyright notice for original optimization code:

        License of L-BFGS-B (Fortran code)
        ==================================
        The version included here (in fortran code) is 2.1 (released in 1997). It was
        written by Ciyou Zhu, Richard Byrd, and Jorge Nocedal <nocedal@ece.nwu.edu>. It
        carries the following condition for use:

        This software is freely available, but we expect that all publications
        describing  work using this software , or all commercial products using it,
        quote at least one of the references given below.

        References
        * R. H. Byrd, P. Lu and J. Nocedal. A Limited Memory Algorithm for Bound
          Constrained Optimization, (1995), SIAM Journal on Scientific and
          Statistical Computing , 16, 5, pp. 1190-1208.
        * C. Zhu, R. H. Byrd and J. Nocedal. L-BFGS-B: Algorithm 778: L-BFGS-B,
           FORTRAN routines for large scale bound constrained optimization (1997),
           ACM Transactions on Mathematical Software, Vol 23, Num. 4, pp. 550 - 560.
        """
        input, target = self._setnorm(input, target)
        if 'bounds' not in kwargs: kwargs['bounds'] = ((-100., 100.),)*len(self.conec)
        func = netprop.func
        fprime = netprop.grad
        extra_args = (self.conec, self.bconecno, self.units, \
                           self.inno, self.outno, input, target)
        self.weights = optimize.fmin_l_bfgs_b(func, self.weights, fprime=fprime, \
                                              args=extra_args, **kwargs)[0]
        self.trained = 'bfgs'

    def train_tnc(self, input, target, **kwargs):
        """
        Train network with a TNC algorithm.
        TNC is a C implementation of TNBC, a truncated newton
        optimization package originally developed by Stephen G. Nash in Fortran.
    
        Allowed parameters:
        bounds    : a list of (min, max) pairs for each weight, defining
                    the bounds on that parameter. Use None for one of min or max
                    when there is no bound in that direction. At default all weights
                    are bounded to (-100, 100)
        scale      : scaling factors to apply to each weight (a list of floats)
                    if None, the factors are up-low for interval bounded weights
                    and 1+|weight| for the others.
                    defaults to None
        messages  : bit mask used to select messages display during minimization
                    0: 'No messages',
                    1: 'One line per iteration',
                    2: 'Informational messages',
                    4: 'Version info',
                    8: 'Exit reasons',
                    15: 'All messages'
                    defaults to 0.
        maxCGit   : max. number of hessian*vector evaluation per main iteration
                    if maxCGit == 0, the direction chosen is -gradient
                    if maxCGit < 0, maxCGit is set to max(1,min(50,n/2))
                    defaults to -1
        maxfun    : max. number of function evaluation
                    if None, maxnfeval is set to max(1000, 100*len(x0))
                    defaults to None
        eta       : severity of the line search. if < 0 or > 1, set to 0.25
                    defaults to -1
        stepmx    : maximum step for the line search. may be increased during call
                    if too small, will be set to 10.0
                    defaults to 0
        accuracy  : relative precision for finite difference calculations
                    if <= machine_precision, set to sqrt(machine_precision)
                    defaults to 0
        fmin      : minimum cost function value estimate
                    defaults to 0
        ftol      : precision goal for the value of f in the stopping criterion
                    relative to the machine precision and the value of f.
                    if ftol < 0.0, ftol is set to 0.0
                    defaults to 0
        rescale   : Scaling factor (in log10) used to trigger rescaling
                    if 0, rescale at each iteration
                    if a large value, never rescale
                    if < 0, rescale is set to 1.3.
                    default to -1
    
        Note: optimization routine used here is part of scipy.optimize.
        """
        input, target = self._setnorm(input, target)
        if 'messages' not in kwargs: kwargs['messages'] = 0
        if 'bounds' not in kwargs: kwargs['bounds'] = ((-100., 100.),)*len(self.conec)
        func = netprop.func
        fprime = netprop.grad
        extra_args = (self.conec, self.bconecno, self.units, \
                           self.inno, self.outno, input, target)
        self.weights = optimize.fmin_tnc(func, self.weights.tolist(), fprime=fprime, \
                                         args=extra_args, **kwargs)[-1]
        self.weights = array(self.weights)
        self.trained = 'tnc'
        
    def test(self, input, target, iprint = 1, filename = None):
        """
        Calculates output and parameters of regression line of targets vs. outputs.
        Returns: (output, regress)
        where regress contains regression line parameters for each output node. These
        parameters are (slope, intercept, r, two-tailed prob, stderr-of-the-estimate).
        
        Optional parameters:
        iprint   - verbosity level:
                   0 - print nothing
                   1 - print regression parameters for each output node
                   2 - print additionaly general network info and all targets vs. outputs
                       (default is 1)
        filename - string with path to the file; if given, output is redirected 
                   to this file (default is None)
        """
        # Check if we dump stdout to the file
        if filename:
            import sys
            file = open(filename, 'w')
            saveout = sys.stdout
            sys.stdout = file
        # Print network info
        if iprint == 2:
            print self
            print
        # Test data and get output
        input, target = self._testdata(input, target)
        nump = len(input)
        output = array([self(inp) for inp in input])
        # Calculate regression info
        from scipy.stats import linregress
        numo = len(self.outno)
        target = target.transpose()
        output = output.transpose()
        regress = []
        if iprint: print "Testing results for %i testing cases:" % nump
        for o in xrange(numo):
            if iprint:
                print "OUTPUT %i (node nr %i):" %(o+1, self.outno[o])
            if iprint == 2:    
                print "Targets vs. outputs:"
                for p in xrange(nump):
                    print "%4i % 13.6f % 13.6f" %(p+1, target[o,p], output[o,p])
            r = linregress(target[o], output[o])
            if iprint:
                print "Regression line parameters:"
                print "slope       = % f" % r[0] 
                print "intercept   = % f" % r[1]
                print "correlation = % f" % r[2]
                print "tailprob    = % f" % r[3]
                print "stderr      = % f" % r[4]
            regress.append(r)
            if iprint: print
        # Close file and restore stdout
        if filename: 
            file.close()
            sys.stdout = saveout
            
        return output.transpose().tolist(), regress

def savenet(net, filename):
    """
    Saves network to a file using cPickle module.
    """
    import cPickle
    file = open(filename, 'w')
    cPickle.dump(net, file)
    file.close()
    return
    
def loadnet(filename):
    """
    Loads network pickled previously with 'savenet'. 
    """    
    import cPickle
    file = open(filename, 'r')
    net = cPickle.load(file)
    return net

def exportnet(net, filename, name = 'ffnet', lang = 'fortran'):
    """
    Exports network to a compiled language source code.
    Currently only fortran is supported.

    There are two routines exported. First one, for recalling the network,
    is named as indicated with keyword argument 'name'. The second one,
    for calculating partial derivatives, have the same name with 'd'
    prefix. 'ffnet' and 'dffnet' are exported at default.
    
    NOTE: You need 'ffnet.f' file distributed with ffnet
          sources to get the exported routines to work.
    """
    from tools import py2f
    f = open( filename, 'w' )
    f.write( py2f.fheader( net, version = version ) )
    f.write( py2f.fcomment() )
    f.write( py2f.ffnetrecall(net, name) )
    f.write( py2f.fcomment() )
    f.write( py2f.ffnetdiff(net, 'd' + name) )
    f.close()
    return
    
# TESTS
import unittest

class Testmlgraph(unittest.TestCase):
    def testEmpty(self):
        arch = ()
        conec = mlgraph(arch)
        self.assertEqual(conec, [])
    def testOneLayer(self):
        arch = (5,)
        conec = mlgraph(arch)
        self.assertEqual(conec, [])
    def testTwoLayers(self):
        arch = (1,1)
        conec = mlgraph(arch)
        self.assertEqual(conec, [(1,2), (0,2)])
    def testThreeLayers(self):
        arch = (2,2,1)
        conec = mlgraph(arch)
        conec0 = [(1, 3), (2, 3), (0, 3), \
                  (1, 4), (2, 4), (0, 4), \
                  (3, 5), (4, 5), (0, 5)]
        self.assertEqual(conec, conec0)
    def testNoBiases(self):
        arch = (2,2,1)
        conec = mlgraph(arch, biases = False)
        conec0 = [(1, 3), (2, 3), \
                  (1, 4), (2, 4), \
                  (3, 5), (4, 5)]
        self.assertEqual(conec, conec0)

class Testimlgraph(unittest.TestCase):
    def testEmpty(self):
        arch = ()
        self.assertRaises(TypeError, imlgraph, arch)
    def testOneLayer(self):
        arch = (5,)
        self.assertRaises(TypeError, imlgraph, arch)
    def testTwoLayers(self):
        arch = (1,1)
        self.assertRaises(TypeError, imlgraph, arch)
    def testThreeLayers(self):
        arch = (2,2,2)
        conec = imlgraph(arch)
        conec0 = [(1, 3), (2, 3), (0, 3), \
                  (1, 4), (2, 4), (0, 4), \
                  (3, 5), (4, 5), (0, 5), \
                  (1, 6), (2, 6), (0, 6), \
                  (1, 7), (2, 7), (0, 7), \
                  (6, 8), (7, 8), (0, 8)]
        self.assertEqual(conec, conec0)
    def testNoBiases(self):
        arch = (2,[(2,), (2,)],2)
        conec = imlgraph(arch, biases = False)
        conec0 = [(1, 3), (2, 3), \
                  (1, 4), (2, 4), \
                  (3, 5), (4, 5), \
                  (1, 6), (2, 6), \
                  (1, 7), (2, 7), \
                  (6, 8), (7, 8),]
        self.assertEqual(conec, conec0)


class Testtmlgraph(unittest.TestCase):
    def testEmpty(self):
        arch = ()
        conec = tmlgraph(arch)
        self.assertEqual(conec, [])
    def testOneLayer(self):
        arch = (5,)
        conec = tmlgraph(arch)
        self.assertEqual(conec, [])
    def testTwoLayers(self):
        arch = (1,1)
        conec = tmlgraph(arch)
        self.assertEqual(conec, [(0,2), (1,2)])
    def testThreeLayers(self):
        arch = (2,1,1)
        conec = tmlgraph(arch)
        conec0 = [(0, 3), (1, 3), (2, 3), \
                  (0, 4), (1, 4), (2, 4), (3, 4)]
        self.assertEqual(conec, conec0)
    def testNoBiases(self):
        arch = (2,1,1)
        conec = tmlgraph(arch, biases = False)
        conec0 = [(1, 3), (2, 3), \
                  (1, 4), (2, 4), (3, 4)]
        self.assertEqual(conec, conec0)

class Testlinear(unittest.TestCase):
    def testEqualInRanges(self):
        #self.assertRaises(ValueError, linear, 1.0, 1.0, 2.0, 3.0)
        self.assertEqual(linear(1.0, 1.0, 2.0, 3.0), (0, 2.5))
    def testEqualOutRanges(self):
        self.assertEqual(linear(2.0, 3.0, 1.0, 1.0), (0.0, 1.0))
    def testNormalCase(self):
        self.assertEqual(linear(0.0, 1.0, 0.0, 2.0), (2.0, 0.0))

class Testnorms(unittest.TestCase):
    def testEmpty(self):
        inarray = [[], []]
        n = norms(inarray)
        for i in xrange(len(n)):
            self.assertEqual(n[i].tolist(), [])
    def testOneColumn(self):
        inarray = [[0.], [1.], [2.]]
        n = norms(inarray)
        bool1 = n[0].tolist() == [[0., 2.]]
        bool2 = n[1].tolist() == [[0.5, 0.]]
        bool3 = n[2].tolist() == [[2., 0.]]
        self.assert_(bool1 and bool2 and bool3)
    def testNormalCase(self):
        inarray = [[0.,0.], [0.,1.], [1.,0.], [1.,1.]]
        n = norms(inarray, lower=0.15, upper=0.85)
        self.assertEqual(n[0].tolist(), [[0., 1.], [0, 1.]])
        self.assertEqual(n[1].tolist(), [[0.7, 0.15], [0.7, 0.15]])
        self.assertAlmostEqual(n[2][0,0], 1.42857143, 8)
        self.assertAlmostEqual(n[2][0,1], -0.21428571, 8)
        
class Testnormarray(unittest.TestCase):
    def testEmpty(self):
        inarray = [[], []]
        n = normarray(inarray, [])
        for i in xrange(len(n)):
            self.assertEqual(n[i].tolist(), [])
    
    def testOneColumn(self):
        inarray = [[0.], [1.], [1.], [0.]]
        coeff = [[0.7, 0.15]]
        n = normarray(inarray, coeff)
        for i in xrange(4):
            self.assertAlmostEqual(n[i,0], coeff[0][0]*inarray[i][0] + coeff[0][1], 8)
            
class Testffconec(unittest.TestCase):
    def testEmpty(self):
        conec = []
        self.assertRaises(ValueError, ffconec, conec)

    def testWithCycles(self):
        conec = [(1, 3), (2, 3), (0, 3), (3, 1), \
                 (1, 4), (2, 4), (0, 4), (4, 2), \
                 (3, 5), (4, 5), (0, 5), (5, 1) ]
        self.assertRaises(TypeError, ffconec, conec)

    def testNoCycles(self):
        conec = [(1, 3), (2, 3), (0, 3), \
                 (1, 4), (2, 4), (0, 4), \
                 (3, 5), (4, 5), (0, 5) ]
        n = ffconec(conec)
        self.assertEqual(sorted(n[2]), [1, 2])
        self.assertEqual(sorted(n[3]), [3, 4])
        self.assertEqual(sorted(n[4]), [5])
        
class Testbconec(unittest.TestCase):
    def testNoCycles(self):
        conec = [(1, 3), (2, 3), (0, 3), \
                 (1, 4), (2, 4), (0, 4), \
                 (3, 5), (4, 5), (0, 5) ]
        inno = [1,2]
        n = bconec(conec, inno)
        self.assertEqual(n[1], [8,7])
        
class Testdconec(unittest.TestCase):
    def testNoCycles(self):
        conec = [(1, 3), (2, 3), (0, 3), \
                 (1, 4), (2, 4), (0, 4), \
                 (3, 5), (4, 5), (0, 5) ]
        inno = [1,2]
        n = dconec(conec, inno)
        self.assertEqual(n[1], [1, 4, 7, 8, 2, 5, 7, 8])
        self.assertEqual(n[2], [0, 4, 8])
        
class TestFfnetSigmoid(unittest.TestCase):
    def setUp(self):
        self.conec = [(0, 3), (1, 3), (2, 3), \
                      (0, 4), (1, 4), (2, 4), (3, 4)]
        
        self.net = ffnet(self.conec); self.net([1.,1.]) #try if net works
        self.net.weights = array([1.]*7)
        
        self.tnet = ffnet(self.conec)
        self.tnet.weights = array([ 0.65527021, -1.12400619, 0.02066321, \
                                   0.13930684, -0.40153965, 0.11965115, -1.00622429 ])       
        self.input = [[0.,0.], [0.,1.], [1.,0.], [1.,1.]]
        self.target  = [[1.], [0.], [0.], [1.]]
        
    def testCall(self):
        self.assertEqual(self.net([0., 0.]), self.net.call([0., 0.]))
        self.assertAlmostEqual(self.net([0., 0.])[0], 0.8495477739862124, 8)
        
    def testDerivative(self):
        self.assertAlmostEqual(self.net.derivative([0., 0.])[0][0], 0.1529465741023702, 8)
        self.assertAlmostEqual(self.net.derivative([0., 0.])[0][1], 0.1529465741023702, 8)
        
    def testSqerror(self):
        err = self.tnet.sqerror(self.input, self.target)
        out = [ (self.tnet(self.input[i])[0] - self.target[i][0])**2 \
                for i in xrange( len(self.input) ) ]
        pyerr = 0.5 * sum(out)
        self.assertAlmostEqual(err, pyerr, 8)

    def testSqgrad(self):
        self.tnet._setnorm(self.input, self.target) # Possible bug, this shouldn't be here
        g = self.tnet.sqgrad(self.input, self.target)
        w1 = self.tnet.weights - g

        self.tnet.train_momentum(self.input, self.target, eta=1., momentum=0., maxiter=1)
        w2 = self.tnet.weights
        
        for i in xrange(len(w1)):
            self.assertAlmostEqual(w1[i], w2[i], 8)
            

    def testTrainGenetic(self):
        print "Test of genetic algorithm optimization"
        self.tnet.train_genetic(self.input, self.target, lower = -50., upper = 50., \
                                individuals = 20, generations = 1000)
        self.tnet.test(self.input, self.target)
    
    def testTrainMomentum(self): 
        print "Test of backpropagation momentum algorithm"
        self.tnet.train_momentum(self.input, self.target, maxiter=10000)
        self.tnet.test(self.input, self.target)

    def testTrainRprop(self): 
        print "Test of rprop algorithm"
        self.tnet.randomweights()
        xmi = self.tnet.train_rprop(self.input, self.target, \
                                    a=1.2, b=0.5, mimin=0.000001, mimax=50, \
                                    xmi=0.1, maxiter=10000, disp=1)
        self.tnet.test(self.input, self.target)

    def testTrainCg(self):
        print "Test of conjugate gradient algorithm"
        self.tnet.train_cg(self.input, self.target, maxiter=1000, disp=1)
        self.tnet.test(self.input, self.target)
        
    def testTrainBfgs(self):
        print "Test of BFGS algorithm"
        self.tnet.train_bfgs(self.input, self.target, maxfun = 1000)
        self.tnet.test(self.input, self.target)
        
    def testTrainTnc(self):
        print "Test of TNC algorithm"
        self.tnet.train_tnc(array(self.input), array(self.target), maxfun = 1000)
        self.tnet.test(self.input, self.target)
        
    def testTestdata(self):
        net = ffnet( mlgraph((1, 5, 1)) )
        input = [1, 2., 5]
        target = [2, 3, 5.]
        net.train_tnc(input, target, maxfun = 10)
        
class TestSaveLoadExport(unittest.TestCase):
    def setUp(self):
        conec = imlgraph( (5,5,5) )
        self.net = ffnet(conec)
        
    def tearDown(self):
        import os
        try: os.remove('tmpffnet.f')
        except: pass
        try: os.remove('tmpffnet.so')
        except: pass
        try: os.remove('tmpffnet.net')
        except: pass

    def testSaveLoad(self):
        res1 = self.net( [ 1, 2, 3, 4, 5. ] )
        savenet( self.net, 'tmpffnet.net' )
        net = loadnet( 'tmpffnet.net' )
        res2 = net( [ 1, 2, 3, 4, 5. ] )
        for i in xrange(5):
            self.assertAlmostEqual(res1[i], res2[i], 8)
        
    def testExport(self):
        resA = self.net ( [ 1, 2, 3, 4, 5. ] )
        resB = self.net.derivative( [ 1, 2, 3, 4, 5. ] )
        exportnet(self.net, 'tmpffnet.f')
        #import os; os.chdir('/tmp')
        from numpy import f2py
        f = open( 'tmpffnet.f', 'r' ); source = f.read(); f.close()
        f = open( 'fortran/ffnet.f', 'r' ); source += f.read(); f.close()
        import sys
        if sys.platform == 'win32':
            eargs = '--compiler=mingw32'
        else: eargs = ''
        f2py.compile(source, modulename = 'tmpffnet', extra_args = eargs, verbose = 0)
        import tmpffnet
        resA1 = tmpffnet.ffnet( [ 1, 2, 3, 4, 5. ] )
        resB1 = tmpffnet.dffnet( [ 1, 2, 3, 4, 5. ] )
        for i in xrange(5):
            self.assertAlmostEqual(resA[i], resA1[i], 7)
            for j in xrange(5):
                self.assertAlmostEqual(resB[i][j], resB1[i][j], 7)
        

if __name__ == '__main__':
    unittest.main()

