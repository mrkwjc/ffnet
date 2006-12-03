from scipy import array, zeros, ones, random, optimize, sqrt
import networkx as NX
import _ffnet as netprop
from pikaia import pikaia


def mlgraph(arch, biases = True):
    '''
    Creates standard multilayer network full connectivity list.
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
    if b == a: raise ValueError("Mapping not possible due to equal limits")
    c1 = ( d - c ) / ( b - a )
    c2 = c - a*c1
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
    snodes = NX.paths.topological_sort(graph)
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
    bsnodes = NX.paths.topological_sort(bgraph)
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
        dsnodes = NX.paths.topological_sort(dgraph)
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
        coneclist = [[1, 3], [2, 3], [0, 3] \
                     [1, 4], [2, 4], [0, 4] \
                     [3, 5], [4, 5], [0, 5]]
        n = ffnet(conec = coneclist)
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
    There are some training methods included, currently:
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
        """ Returns network answer to input sequence """
        return self.__call__(inp)

    def derivative(self, inp):
        """ Returns partial derivatives of output vs. input at given input point
            in the following array:
                | o1/i1, o1/i2, ..., o1/in |
                | o2/i1, o2/i2, ..., o2/in |
                | ...                      |
                | om/i1, om/i2, ..., om/in |
        """
        deriv = netprop.normdiff(self.weights, self.conec, self.dconecno, self.dconecmk, \
                                 self.units, self.inno, self.outno, self.eni, self.ded, inp)
        return deriv.tolist()

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
        try: input = array(input, 'd')
        except: raise ValueEror("Input cannot be converted to numpy array")
        try: target = array(target, 'd')
        except: raise ValueEror("Target cannot be converted to numpy array")
        
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
        if input == target == None:
            #self.inlimits  = array( [[0.15, 0.85]]*numi ) #informative only
            #self.outlimits = array( [[0.15, 0.85]]*numo ) #informative only
            self.eni = self.dei = array( [[1., 0.]] * numi )
            self.eno = self.deo = array( [[1., 0.]] * numo )
            self.ded = ones(shape = (numo, numi))
        else:
            input, target = self._testdata(input, target)
            #limits are informative only, eni,dei/eno,deo - input/output coding-decoding
            self.inlimits, self.eni, self.dei = norms(input, lower=0.15, upper=0.85)
            self.outlimits, self.eno, self.deo = norms(target, lower=0.15, upper=0.85)
            self.ded = zeros((numo,numi), 'd')
            for o in xrange(numo):
                for i in xrange(numi):
                    self.ded[o,i] = self.eni[i,0] * self.deo[o,0]
            return normarray(input, self.eni), normarray(target, self.eno)

    def train_momentum(self, input, target, eta = 0.2, momentum = 0.8, \
                        maxiter = 1000, disp = 1):
        """
        Simple backpropagation training with momentum.
    
        Allowed parameters:
        eta             - descent scaling parameter (default is 0.2)
        momentum         - momentum coefficient (default is 0.8)
        maxiter         - the maximum number of iterations (default is 1000)
        disp            - print convergence message if non-zero (default is 1)
        """
        input, target = self._setnorm(input, target)
        if disp:
            err  = netprop.sqerror(self.weights, self.conec, self.units, \
                                   self.inno, self.outno, input, target)
            print "Initial error --> 0.5*(sum of squared errors at output): %f" %err
        self.weights = netprop.momentum(self.weights, self.conec, self.bconecno, \
                                        self.units, self.inno, self.outno, input, \
                                        target, eta, momentum, maxiter)
        if disp:
            err  = netprop.sqerror(self.weights, self.conec, self.units, \
                                   self.inno, self.outno, input, target)
            print "Final error   --> 0.5*(sum of squared errors at output): %f" %err

    def train_genetic(self, input, target, **kwargs):
        """
        Global weights optimization with genetic algorithm.
    
        Allowed parameters:
        lower         - lower bound of weights values (default is -25.)
        upper         - upper bound of weights values (default is 25.)
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
    
        For more info see pikaia homepage and documentation4:
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
        maxiter         - the maximum number of iterations (default is None)
        disp         - print convergence message at the end of training
                       if non-zero (default is 1)
    
        Note: this procedure does not produce any output during training.
        Note: optimization routine used here is part of scipy.optimize.
        """
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
                   when there is no bound in that direction. There are no bounds
                   at default.
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
                    when there is no bound in that direction. There are no bounds
                    at default.
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
        #if iprint: print "RESULTS FOR %i TESTING CASES" % nump
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
    import cPickle
    file = open(filename, 'w')
    cPickle.dump(net, file)
    file.close()
    
def loadnet(filename):
    import cPickle
    file = open(filename, 'r')
    net = cPickle.load(file)
    return net

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
        self.assertRaises(ValueError, linear, 1.0, 1.0, 2.0, 3.0)
    def testEqualOutRanges(self):
        self.assertEqual(linear(1.0, 2.0, 2.0, 2.0), (0.0, 2.0))
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
        
    def testTrainGenetic(self):
        print "Test of genetic algorithm optimization"
        self.tnet.train_genetic(self.input, self.target, lower = -50., upper = 50., \
                                individuals = 20, generations = 1000)
        self.tnet.test(self.input, self.target)
    
    def testTrainMomentum(self): 
        print "Test of backpropagation momentum algorithm"
        self.tnet.train_momentum(self.input, self.target, maxiter=10000)
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
        self.tnet.train_tnc(self.input, self.target, maxfun = 1000)
        self.tnet.test(self.input, self.target)

if __name__ == '__main__':
    unittest.main()

