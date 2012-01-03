########################################################################
##  Copyright (C) 2006 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################

"""
--------------------------------------
Main ffnet class and utility functions
--------------------------------------
"""

from _version import version
from scipy import zeros, ones, random, optimize, sqrt, ndarray, array
import networkx as NX
from fortran import _ffnet as netprop
from pikaia import pikaia
import sys

def mlgraph(arch, biases = True):
    """
    Creates standard multilayer network architecture.

    :Parameters:
        arch : tuple
            Tuple of integers - numbers of nodes in subsequent layers.
        biases : bool, optional
            Indicates if bias (node numbered 0) should be added to hidden
            and output neurons. Default is *True*.

    :Returns:
        conec : list
            List of tuples -- network connections.

    :Examples:
        Basic calls:

        >>> from ffnet import mlgraph
        >>> mlgraph((2,2,1))
        [(1, 3), (2, 3), (0, 3), (1, 4), (2, 4), (0, 4), (3, 5), (4, 5), (0, 5)]
        >>> mlgraph((2,2,1), biases = False)
        [(1, 3), (2, 3), (1, 4), (2, 4), (3, 5), (4, 5)]

        Exemplary plot:

        .. plot::
            :include-source:

            from ffnet import mlgraph, ffnet
            import networkx as NX
            import pylab

            conec = mlgraph((3,6,3,2), biases=False)
            net = ffnet(conec)
            NX.draw_graphviz(net.graph, prog='dot')
            pylab.show()
    """
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
    """
    Creates multilayer architecture with independent outputs.

    This function uses `mlgraph` to build independent multilayer
    architectures for each output neuron. Then it merges them into one
    graph with common input nodes.

    :Parameters:
        arch : tuple
            Tuple of length 3. The first element is number of network inputs,
            last one is number of outputs and the middle one is interpreted
            as the hidden layers definition (it can be an *integer* or
            a *list* -- see examples)
        biases : bool, optional
            Indicates if bias (node numbered 0) should be added to hidden
            and output neurons. Default is *True*.

    :Returns:
        conec : list
            List of tuples -- network connections.

    :Raises:
        TypeError
            If *arch* cannot be properly interpreted.

    :Examples:
        The following *arch* definitions are possible:

        >>> from ffnet import imlgraph
        >>> arch = (2, 2, 2)
        >>> imlgraph(arch, biases=False)
            [(1, 3),
            (2, 3),
            (1, 4),
            (2, 4),
            (3, 5),
            (4, 5),
            (1, 6),
            (2, 6),
            (1, 7),
            (2, 7),
            (6, 8),
            (7, 8)]

        In this case two multilayer networks (for two outputs)
        of the architectures (2,2,1), (2,2,1) are merged into one graph.

        >>> arch = (2, [(2,), (2,2)], 2)
        >>> imlgraph(arch, biases=False)
            [(1, 3),
            (2, 3),
            (1, 4),
            (2, 4),
            (3, 5),
            (4, 5),
            (1, 6),
            (2, 6),
            (1, 7),
            (2, 7),
            (6, 8),
            (7, 8),
            (6, 9),
            (7, 9),
            (8, 10),
            (9, 10)]

        I this case networks of the architectures (2,2,1) and (2,2,2,1)
        are merged.

        Exemplary plot:

        .. plot::
            :include-source:

            from ffnet import imlgraph, ffnet
            import networkx as NX
            import pylab

            conec = imlgraph((3, [(3,), (6, 3), (3,)], 3), biases=False)
            net = ffnet(conec)
            NX.draw_graphviz(net.graph, prog='dot')
            pylab.show()
    """
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
    """
    Creates multilayer network full connectivity list.

    Similar to `mlgraph`, but now layers are fully connected with all
    preceding layers.

    :Parameters:
        arch : tuple
            Tuple of integers - numbers of nodes in subsequent layers.
        biases : bool, optional
            Indicates if bias (node numbered 0) should be added to hidden
            and output neurons. Default is *True*.

    :Returns:
        conec : list
            List of tuples -- network connections.

    :Examples:
        Basic calls:

        >>> from ffnet import tmlgraph
        >>> tmlgraph((2,2,1))
            [(0, 3),
            (1, 3),
            (2, 3),
            (0, 4),
            (1, 4),
            (2, 4),
            (0, 5),
            (1, 5),
            (2, 5),
            (3, 5),
            (4, 5)]
        >>> tmlgraph((2,2,1), biases = False)
        [(1, 3), (2, 3), (1, 4), (2, 4), (1, 5), (2, 5), (3, 5), (4, 5)]

        Exemplary plot:

        .. plot::
            :include-source:

            from ffnet import tmlgraph, ffnet
            import networkx as NX
            import pylab

            conec = tmlgraph((3, 8, 3), biases=False)
            net = ffnet(conec)
            NX.draw_graphviz(net.graph, prog='dot')
            pylab.show()
    """
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

def _dependency(G, source):
    """
    Returns subgraph of G connecting source with all sinks.
    """
    H = G.copy()
    node_removal = 1
    while node_removal:
        node_removal = 0
        for node in H.nodes():
            if not H.in_degree(node) and node != source:
                H.remove_node(node)
                node_removal = 1
    return H

def _linear(a, b, c, d):
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

def _norms(inarray, lower = 0., upper = 1.):
    '''
    Gets normalization information from an array, for use in ffnet class.

    (lower, upper) is a range of normalization.
    inarray is 2-dimensional, normalization parameters are computed
    for each column...
    '''
    limits = []; en = []; de = []
    inarray = array(inarray).transpose()
    for col in inarray:
        maxarr = max(col)
        minarr = min(col)
        limits += [(minarr, maxarr)]
        en += [_linear(minarr, maxarr, lower, upper)]
        de += [_linear(lower, upper, minarr, maxarr)]
    return array(limits), array(en), array(de)

def _normarray(inarray, coeff):
    '''
    Normalize 2-dimensional array linearly column by column.

    coeff -- linear map coefficiens.
    '''
    #if coeff is not None:
    inarray = array(inarray).transpose()
    coeff = array(coeff)
    i = inarray.shape[0]
    for ii in xrange(i):
        inarray[ii] = inarray[ii] * coeff[ii,0] + coeff[ii,1]
    return inarray.transpose()
    #else: print "Lack of normalization parameters. Nothing done."

def _ffconec(conec):
    """
    Generates forward propagation informations from conec.

    Checks if conec is acyclic, sorts it if necessary and returns tuple:
    (graph, conec, inno, hidno, outno) where:
    graph - NX.DiGraph()
    conec - topologically sorted conec
    inno/hidno/outno  - lists of input/hidden/ouput units
    """
    if len(conec) == 0: raise ValueError("Empty connectivity list")
    graph = NX.DiGraph()
    graph.add_edges_from(conec)
    snodes = NX.topological_sort(graph) # raises NetworkXUnfeasible if cycles are found
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

def _bconec(conec, inno):
    """
    Generates back propagation informations from conec.

    Returns positions of edges of reversed graph in conec (for backprop).
    Conec is assumed to be acyclic.
    """
    bgraph = NX.DiGraph()
    bgraph.add_edges_from(conec)
    bgraph = bgraph.reverse()
    bgraph.remove_nodes_from(inno)
    try: bgraph.remove_node(0) #handling biases
    except: pass
    bsnodes = NX.topological_sort(bgraph)
    bconecno = []
    for bnode in bsnodes:
        for bedge in bgraph.in_edges(bnode):
            edge = (bedge[1], bedge[0])
            idx = conec.index(edge) + 1
            bconecno.append(idx)
    return bgraph, bconecno

def _dconec(conec, inno):
    """
    Generates derivative propagation informations from conec.

    Return positions of edges (in conec) of graphs for
    derivative calculation, all packed in one list (dconecno). Additionaly
    beginings of each graph in this list is returned (dconecmk)
    """
    dgraphs = []; dconecno = []; dconecmk = [0]
    for idx, i in enumerate(inno):
        dgraph = NX.DiGraph()
        dgraph.add_edges_from(conec)
        dgraph = _dependency(dgraph, i)
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
    Feed-forward neural network main class.

    :Parameters:
        conec : list of tuples
            List of network connections
        lazy_derivative : bool
            If *True* all data necessary for derivatives calculation
            (see `ffnet.derivative` method) are generated only on demand.

    :Returns:
        net
             Feed forward network object

    :Raises:
        TypeError
           If *conec* is not directed acyclic graph

    :Instance attributes:
        conec : array
            Topologically sorted network connections
        weights : array
            Weights in order of topologically sorted connections
        renormalize : bool
            If *True* normalization ranges will be recreated from
            training data at next training call.

            Default is *True*

    :Examples:
        >>> from ffnet import mlgraph, ffnet
        >>> conec = mlgraph((2,2,1))
        >>> net = ffnet(conec)

    :See also:
        `mlgraph`, `tmlgraph`, `imlgraph`

    """
    def __init__(self, conec, lazy_derivative = True):
        graph, conec, inno, hidno, outno = _ffconec(conec)
        self.graph = graph
        self.conec = array(conec)
        self.inno = array(inno)
        self.hidno = array(hidno)
        self.outno = array(outno)

        bgraph, bconecno = _bconec(conec, self.inno)
        self.bgraph = bgraph
        self.bconecno = array(bconecno)

        # Ommit creating data for derivatives here (which is expensive for large nets)
        if lazy_derivative:
            self.dgraphs = None
            self.dconecno = None
            self.dconecmk = None
        else:
            self._set_dconec()

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
        ## Something more sophisticated is needed here?
        return self.call(inp)

    def _set_dconec(self):
        conec = [tuple(c) for c in self.conec] # maybe rather some changes in _dconec?
        dgraphs, dconecno, dconecmk = _dconec(conec, self.inno)
        self.dgraphs = dgraphs
        self.dconecno = array(dconecno)
        self.dconecmk = array(dconecmk)

    def call(self, inp):
        """
        Calculates network answer to given input.

        :Parameters:
            inp : array
                2D array of input patterns (or 1D for single pattern)

        :Returns:
            ans : array
                1D or 2D array of calculated network outputs

        :Raises:
            TypeError
                If *inp* is invalid
        """
        if not isinstance(inp, ndarray): inp = array(inp, 'd')
        if inp.ndim == 1:
            output = netprop.normcall(self.weights, self.conec, self.units, \
                            self.inno, self.outno, self.eni, self.deo, inp)
            return output
        if inp.ndim == 2:
            output = netprop.normcall2(self.weights, self.conec, self.units, \
                            self.inno, self.outno, self.eni, self.deo, inp)
            return output
        raise TypeError("Input is not valid")

    def derivative(self, inp):
        """
        Returns partial derivatives of the network's output vs its input.

        For each input pattern an array of the form::

            | o1/i1, o1/i2, ..., o1/in |
            | o2/i1, o2/i2, ..., o2/in |
            | ...                      |
            | om/i1, om/i2, ..., om/in |

        is returned.

        :Parameters:
            inp : array
                2D array of input patterns (or 1D for single pattern)

        :Returns:
            ans : array
                1D or 2D array of calculated network outputs

        :Examples:
            >>> from ffnet import mlgraph, ffnet
            >>> conec = mlgraph((3,3,2))
            >>> net = ffnet(conec); net.weights[:] = 1.
            >>> net.derivative([0., 0., 0.])
            array([[ 0.02233658,  0.02233658,  0.02233658],
                   [ 0.02233658,  0.02233658,  0.02233658]])
        """
        if self.dconecno is None:  #create dconecno (only od demand)
            self._set_dconec()

        if not isinstance(inp, ndarray): inp = array(inp, 'd')
        if inp.ndim == 1:
            deriv = netprop.normdiff(self.weights, self.conec, self.dconecno, self.dconecmk, \
                            self.units, self.inno, self.outno, self.eni, self.ded, inp)
            return deriv
        if inp.ndim == 2:
            deriv = netprop.normdiff2(self.weights, self.conec, self.dconecno, self.dconecmk, \
                            self.units, self.inno, self.outno, self.eni, self.ded, inp)
            return deriv
        raise TypeError("Input is not valid")

    def sqerror(self, input, target):
        """
        Calculates sum of squared errors at network output.

        Error is calculated for **normalized** input and target arrays.

        :Parameters:
            input : 2-D array
                Array of input patterns
            target : 2-D array
                Array of network targets

        :Returns:
            err : float
                0.5*(sum of squared errors at network outputs)

        .. note::
            This function might be slow in frequent use, because data
            normalization is performed at each call. Usually there's no need
            to use this function, unless you need to adopt your own training
            strategy.
        """
        input, target = self._setnorm(input, target)
        err  = netprop.sqerror(self.weights, self.conec, self.units, \
                               self.inno, self.outno, input, target)
        return err

    def sqgrad(self, input, target):
        """
        Returns gradient of network error vs. network weights.

        Error is calculated for **normalized** input and target arrays.

        :Parameters:
            input : 2-D array
                Array of input patterns
            target : 2-D array
                Array of network targets

        :Returns:
            grad : 1-D array
                Array of the same length as *net.weights* containing
                gradient values.

        .. note::
            This function might be slow in frequent use, because data
            normalization is performed at each call. Usually there's no need
            to use this function, unless you need to adopt your own training
            strategy.
        """
        input, target = self._setnorm(input, target)
        g  = netprop.grad(self.weights, self.conec, self.bconecno, self.units, \
                          self.inno, self.outno, input, target)
        return g

    def randomweights(self):
        """
        Randomize network weights due to Bottou proposition.

        If *n* is a number of node's incoming connections, weights of these
        connections are chosen randomly from range
        *(-2.38/sqrt(n), -2.38/sqrt(n))*

        """
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
        """
        Tests input and target data.
        """
        # Test conversion
        try:
            if not isinstance(input, ndarray): input = array(input, 'd')
            #input = array(input, 'd')
        except: raise ValueError("Input cannot be converted to numpy array")
        try:
            if not isinstance(target, ndarray): target = array(target, 'd')
            #target = array(target, 'd')
        except: raise ValueError("Target cannot be converted to numpy array")

        #if input.dtype.char != 'd': input = array(input, 'd')

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
        """
        Retrieves normalization info from training data and normalizes data.

        This method sets self.renormalize attribute to control normalization.
        """
        numi = len(self.inno); numo = len(self.outno)
        if input is None and target is None:
            self.inlimits  = array( [[0.15, 0.85]]*numi ) #informative only
            self.outlimits = array( [[0.15, 0.85]]*numo ) #informative only
            self.eni = self.dei = array( [[1., 0.]] * numi )
            self.eno = self.deo = array( [[1., 0.]] * numo )
            self.ded = ones((numo, numi), 'd')
            self.renormalize = True  # this is set by __init__
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
            if self.renormalize:
                self.inlimits, self.eni, self.dei = _norms(input, lower=0.15, upper=0.85)
                self.outlimits, self.eno, self.deo = _norms(target, lower=0.15, upper=0.85)
                self.ded = zeros((numo,numi), 'd')
                for o in xrange(numo):
                    for i in xrange(numi):
                        self.ded[o,i] = self.eni[i,0] * self.deo[o,0]
                self.renormalize = False

            return _normarray(input, self.eni), _normarray(target, self.eno)

    def train_momentum(self, input, target, eta = 0.2, momentum = 0.8, \
                        maxiter = 10000, disp = 0):
        """
        Simple backpropagation training with momentum.

        :Parameters:
            input : 2-D array
                Array of input patterns
            target : 2-D array
                Array of network targets
            eta : float, optional
                Learning rate
            momentum : float, optional
                Momentum coefficient
            maxiter : integer, optional
                Maximum number of iterations
            disp : bool
                If True convergence method is displayed
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

        :Parameters:
            input : 2-D array
                Array of input patterns
            target : 2-D array
                Array of network targets
            a : float, optional
                Training step increasing parameter
            b : float, optional
                Training step decreasing parameter
            mimin : float, optional
                Minimum training step
            mimax : float, optional
                Maximum training step
            xmi : array (or float), optional
                Array containing initial training steps for weights.
                If *xmi* is a scalar then its value is set for all weights
            maxiter : integer, optional
                Maximum number of iterations
            disp : bool
                If True convergence method is displayed. Default is *False*

        :Returns:
            xmi : array
                Computed array of training steps to be used in eventual further
                training calls.
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

        :Parameters:
            input : 2-D array
                Array of input patterns
            target : 2-D array
                Array of network targets
            lower : float, optional
                Lower bound of weights values (default is -25.)
            upper : float, optional
                Upper bound of weights values (default is 25.)
            individuals : integer, optional
                Number of individuals in a population (default is 20)
            generations : integer, optional
                Number of generations over which solution is
                to evolve (default is 500)
            verbosity : {0, 1, 2}, optional
                Printed output 0/1/2=None/Minimal/Verbose (default is 0)

        .. seealso::
            See description of `pikaia.pikaia` optimization function for other
            parameters.
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
        Train network with conjugate gradient algorithm.

        :Parameters:
            input : 2-D array
                Array of input patterns
            target : 2-D array
                Array of network targets
            maxiter : integer, optional
                Maximum number of iterations (default is 10000)
            disp : bool
                If True convergence method is displayed (default)

        .. seealso::
            `scipy.optimize.fmin_cg` optimizer is used in this method. Look
            at its documentation for possible other useful parameters.
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
        Train network with constrained version of BFGS algorithm.

        :Parameters:
            input : 2-D array
                Array of input patterns
            target : 2-D array
                Array of network targets
            maxfun : int
                Maximum number of function evaluations (default is 15000)
            bounds : list, optional
                *(min, max)* pairs for each connection weight, defining
                the bounds on that weight. Use None for one of *min* or
                *max* when there is no bound in that direction.
                By default all bounds ar set to (-100, 100)
            disp : int, optional
                If 0, then no output (default). If positive number then
                convergence messages are dispalyed.

        .. seealso::
            `scipy.optimize.fmin_l_bfgs_b` optimizer is used in this method. Look
            at its documentation for possible other useful parameters.
        """
        if sys.platform.startswith('aix'): return

        input, target = self._setnorm(input, target)
        if 'bounds' not in kwargs: kwargs['bounds'] = ((-100., 100.),)*len(self.conec)
        func = netprop.func
        fprime = netprop.grad
        extra_args = (self.conec, self.bconecno, self.units, \
                           self.inno, self.outno, input, target)
        self.weights = optimize.fmin_l_bfgs_b(func, self.weights, fprime=fprime, \
                                              args=extra_args, **kwargs)[0]
        self.trained = 'bfgs'

    def train_tnc(self, input, target, nproc = 1, **kwargs):
        """
        :Parameters:
            input : 2-D array
                Array of input patterns
            target : 2-D array
                Array of network targets
            nproc : int or 'ncpu', optional
                Number of processes spawned for training. If nproc='ncpu'
                nproc will be set to number of avilable processors
            maxfun : int
                Maximum number of function evaluation. If None, maxfun is
                set to max(100, 10*len(weights)). Defaults to None.
            bounds : list, optional
                *(min, max)* pairs for each connection weight, defining
                the bounds on that weight. Use None for one of *min* or
                *max* when there is no bound in that direction.
                By default all bounds ar set to (-100, 100)
            messages : int, optional
                If 0, then no output (default). If positive number then
                convergence messages are dispalyed.

        .. note::
            On Windows using *ncpu > 1* might be memory hungry, because
            each process have to load its own instance of network and
            training data. This is not the case on Linux platforms.

        .. seealso::
            `scipy.optimize.fmin_tnc` optimizer is used in this method. Look
            at its documentation for possible other useful parameters.
        """
        input, target = self._setnorm(input, target)
        if 'messages' not in kwargs: kwargs['messages'] = 0
        if 'bounds' not in kwargs: kwargs['bounds'] = ((-100., 100.),)*len(self.conec)

        # multiprocessing version if nproc > 1
        if (isinstance(nproc, int) and nproc > 1) or nproc in (None, 'ncpu'):
            if nproc == 'ncpu': nproc = None
            self._train_tnc_mp(input, target, nproc = nproc, **kwargs)
            return

        # single process version
        func = netprop.func
        fprime = netprop.grad
        extra_args = (self.conec, self.bconecno, self.units, \
                           self.inno, self.outno, input, target)
        res = optimize.fmin_tnc(func, self.weights, fprime=fprime, \
                                         args=extra_args, **kwargs)
        self.weights = array( res[0] )
        self.trained = 'tnc'

    def _train_tnc_mp(self, input, target, nproc = None, **kwargs):
        """
        Parallel training with TNC algorithm

        Standard multiprocessing package is used here.
        """
        #register training data at mpprop module level
        # this have to be done *BEFORE* creating pool
        import _mpprop as mpprop
        try: key = max(mpprop.nets) + 1
        except ValueError: key = 0  # uniqe identifier for this training
        mpprop.nets[key] = self
        mpprop.inputs[key] = input
        mpprop.targets[key] = target

        # create processing pool
        from multiprocessing import Pool, cpu_count
        if nproc is None: nproc = cpu_count()
        if sys.platform.startswith('win'):
            # we have to initialize processes in pool on Windows, because
            # each process reimports mpprop thus the registering
            # made above is not enough
            # WARNING: this might be slow and memory hungry
            # (no shared memory, all is serialized and copied)
            initargs = [key, self, input, target]
            pool = Pool(nproc, initializer = mpprop.initializer, initargs=initargs)
        else:
            pool = Pool(nproc)
        # generate splitters for training data
        splitters = mpprop.splitdata(len(input), nproc)

        # train
        func = mpprop.mpfunc
        fprime = mpprop.mpgrad

        #if 'messages' not in kwargs: kwargs['messages'] = 0
        #if 'bounds' not in kwargs: kwargs['bounds'] = ((-100., 100.),)*len(self.conec)
        res = optimize.fmin_tnc(func, self.weights, fprime = fprime, \
                                args = (pool, splitters, key), **kwargs)
        self.weights = res[0]

        # remove references from mpprop
        del mpprop.nets[key]
        del mpprop.inputs[key]
        del mpprop.targets[key]
        pool.terminate()
        del pool

    def test(self, input, target, iprint = 1, filename = None):
        """
        Calculates output and parameters of regression.

        :Parameters:
            input : 2-D array
                Array of input patterns
            target : 2-D array
                Array of network targets
            iprint : {0, 1, 2}, optional
                Verbosity level: 0 -- print nothing, 1 -- print regression
                parameters for each output node (default), 2 -- print
                additionaly general network info and all targets vs. outputs
            filename : str
                Path to the file where printed messages are redirected
                Default is None

        :Returns:
            out : tuple
                *(output, regress)* tuple where: *output* is an array of network
                answers on input patterns and *regress* contains regression
                parameters for each output node. These parameters are: *slope,
                intercept, r-value, p-value, stderr-of-slope, stderr-of-estimate*.

        :Examples:
            >>> from ffnet import mlgraph, ffnet
            >>> from numpy.random import rand
            >>> conec = mlgraph((3,3,2))
            >>> net = ffnet(conec)
            >>> input = rand(50,3); target = rand(50,2)
            >>> output, regress = net.test(input, target)
            Testing results for 50 testing cases:
            OUTPUT 1 (node nr 8):
            Regression line parameters:
            slope         = -0.000649
            intercept     =  0.741282
            r-value       = -0.021853
            p-value       =  0.880267
            slope stderr  =  0.004287
            estim. stderr =  0.009146
            .
            OUTPUT 2 (node nr 7):
            Regression line parameters:
            slope         =  0.005536
            intercept     =  0.198818
            r-value       =  0.285037
            p-value       =  0.044816
            slope stderr  =  0.002687
            estim. stderr =  0.005853

            Exemplary plot:

            .. plot::
                :include-source:

                from ffnet import mlgraph, ffnet
                from numpy.random import rand
                from numpy import linspace
                import pylab

                # Create and train net on random data
                conec = mlgraph((3,10,2))
                net = ffnet(conec)
                input = rand(50,3); target = rand(50,2)
                net.train_tnc(input, target, maxfun = 400)
                output, regress = net.test(input, target, iprint = 0)

                # Plot results for first output
                pylab.plot(target.T[0], output.T[0], 'o',
                                        label='targets vs. outputs')
                slope = regress[0][0]; intercept = regress[0][1]
                x = linspace(0,1)
                y = slope * x + intercept
                pylab.plot(x, y, linewidth = 2, label = 'regression line')
                pylab.legend()
                pylab.show()
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
        output = self(input) #array([self(inp) for inp in input])
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
            x = target[o]; y = output[o]
            r = linregress(x, y)
            # linregress calculates stderr of the slope instead of the estimate, even
            # though the docs say something else. we calculate the thing here manually
            sstd = r[-1]
            estd = sstd * sqrt( ( ( x-x.mean() )**2 ).sum() )
            r += (estd,)
            if iprint:
                print "Regression line parameters:"
                print "slope         = % f" % r[0]
                print "intercept     = % f" % r[1]
                print "r-value       = % f" % r[2]
                print "p-value       = % f" % r[3]
                print "slope stderr  = % f" % r[4]
                print "estim. stderr = % f" % r[5]
            regress.append(r)
            if iprint: print
        # Close file and restore stdout
        if filename:
            file.close()
            sys.stdout = saveout

        return output.transpose(), regress

def savenet(net, filename):
    """
    Dumps network to a file using cPickle.

    :Parameters:
        net : ffnet
            Intance of the network
        filename : str
            Path to the file where network is dumped
    """
    import cPickle
    file = open(filename, 'w')
    cPickle.dump(net, file)
    file.close()
    return

def loadnet(filename):
    """
    Loads network pickled previously with `savenet`.

    :Parameters:
        filename : str
            Path to the file with saved network
    """
    import cPickle
    file = open(filename, 'r')
    net = cPickle.load(file)
    return net

def _exportfortran(net, filename, name, derivative = True):
    """
    Exports network to Fortran source
    """
    import _py2f as py2f
    f = open( filename, 'w' )
    f.write( py2f.fheader( net, version = version ) )
    f.write( py2f.fcomment() )
    f.write( py2f.ffnetrecall(net, name) )
    if derivative:
        if net.dconecno is None: net._set_dconec() #set on demand
        f.write( py2f.fcomment() )
        f.write( py2f.ffnetdiff(net, 'd' + name) )
    f.close()

def exportnet(net, filename, name = 'ffnet', lang = None, derivative = True):
    """
    Exports network to a compiled language source code.

    :Parameters:
        filename : str
            Path to the file where network is exported
        name : str
            Name of the exported function
        lang : str
            Language to which network is to be exported.
            Currently only Fortran is supported
        derivative : bool
            If *True* a function for derivative calculation is also
            exported. It is named as *name* with prefix 'd'

    .. note::
        You need 'ffnet.f' file distributed with ffnet
        sources to get the exported Fortran routines to work.
    """
    # Determine language if not specified
    if not lang:
        import os.path
        fname, ext = os.path.splitext(filename)
        if ext in ['.f', '.for', '.f90']:
            lang = 'fortran'

    if lang == 'fortran':
        _exportfortran(net, filename, name, derivative = derivative)
    else:
        if lang:
            raise TypeError("Unsupported language " + lang)
        else:
            raise TypeError("Unspecified language")
    return

def readdata(filename, **kwargs):
    """
    Reads arrays from ASCII files.

    .. note::
        This function just calls `numpy.loadtxt` passing
        to it all keyword arguments. Refer to this function
        for possible options.
    """
    from numpy import loadtxt
    data = loadtxt(filename, **kwargs)
    return data

