from scipy import array, zeros, random, optimize, sqrt
import networkx as NX
import _ffnet as netprop
from pikaia import pikaia


def mlgraph(arch, biases = True):
	'''
	Creates standard multilayer network full connectivity list.
	'''
	nofl = len(arch)
	conec = []; trg = arch[0]
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
	conec = []; trg = arch[0]; srclist = []
	if biases: srclist = [0]
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
	Gets normalization information from an array,
	for use in ffnet class.
	(lower, upper) is a range of normalisation.
	If inarray is 2-dimensional then each column
	is treated sepearately.
	'''
	limits = []; en = []; de = []
	inarray = array(inarray).transpose()
	for col in inarray:
		maxarr = max(col)
		minarr = min(col)
		limits += [(minarr, maxarr)]
		en += [linear(minarr, maxarr, lower, upper)]
		de += [linear(lower, upper, minarr, maxarr)]
	return limits, array(en), array(de)
	
def normarray(inarray, coeff = None):
	''' Normalize array linearly column by column with provided coefficiens '''
	if coeff is not None:
		inarray = array(inarray).transpose()
		i = inarray.shape[0]
		for ii in xrange(i):
			inarray[ii] = inarray[ii] * coeff[ii,0] + coeff[ii,1]
		return inarray.transpose()
	else: print "Lack of normalization parameters. Nothing done."

def ffconec(conec):
	"""
	Checks if conec is acyclic, sorts it if necessary and returns tuple:
	(conec, inno, hidno, outno) where:
		conec - sorted input connectivity
		inno/hidno/outno  - lists of input/hidden/ouput units
	"""
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
				else: hidno += [node]
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
	dgraphs = []; dconecno = []; dconecmk = [1]
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
	
	There is support for some standard feed-forward architectures:
	- multilayer perceptron:
		n = ffnet(mlp = (2,2,1))
		note: this produces network with connectivity as in the above 'coneclist'
	- total multilayer perceptron:
		n = ffnet(tmlp = (2,1,1))
		note: produced connectivity: [[1, 3], [2, 3], [0, 3], \
									  [1, 4], [2, 4], [3, 4], [0, 4]]
									  
	Weights are automatically initialized at the network creation. They can
	be reinitialized later with 'randomweights' method.
	
	TRAINING NETWORK:
	There are some training methods included, currently:
	train_genetic, train_cg, train_bfgs, train_tnc.
	The simplest usage is, for example:
		n.train_tnc(input, target)
	where 'input' and 'target' are RAW data to be learned. Class performs data 
	normalization by itself and records encoding/decoding information to be used
	during network recalling.
	Class makes basic checks of data.
	
	For information about training prameters see appropriate method description.
	
	RECALLING NETWORK:
	Usage of the trained network is very simple:
		ans = n(inp)
	or
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
	def __init__(self, **kwargs):
		if 'conec'  in kwargs: conec = kwargs['conec']
		elif 'mlp'  in kwargs: conec = mlgraph(kwargs['mlp'])
		elif 'tmlp' in kwargs: conec = tmlgraph(kwargs['tmlp'])
		else: raise TypeError("Wrong network definition")
			
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
		self.randomweights()

	def __call__(self, inp):
		return self.call(inp)
	
	def call(self, inp):
		""" Returns network answer to input sequence """
		output = netprop.prop9(self.weights, self.conec, self.units, \
							   self.inno, self.outno, self.eni, self.deo, inp)
		return output

	def derivative(self, inp):
		""" Returns partial derivatives of output vs. input at given input point 
			in the following array:
				| o1/i1, o1/i2, ..., o1/in |
				| o2/i1, o2/i2, ..., o2/in |
				| ...                      |
				| om/i1, om/i2, ..., om/in |
		"""
		deriv = netprop.prop10(self.weights, self.conec, self.dconecno, self.dconecmk, \
							   self.units, self.inno, self.outno, self.eni, self.ded, inp)
		return deriv

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
		numip = input.shape[0]; numop = target.shape[0]
		if numip != numop:
			raise ValueError \
			("Training data not aligned: input patterns %i, target patterns: %i" %(numip, numop))
		numi = len(self.inno); numiv = input.shape[1]
		if numiv != numi: 
			raise ValueError \
			("Inconsistent input data, input units: %i, input values: %i" %(numi, numiv))
		numo = len(self.outno); numov = target.shape[1]
		if numov != numo: 
			raise ValueError \
			("Inconsistent target data, target units: %i, target values: %i" %(numo, numov))

	def _setnorm(self, input, target):
		"""Retrieves normalization info from training data and normalizes data"""
		input = array(input); target = array(target)
		self._testdata(input, target)
		self.inlimits, self.eni, self.dei = norms(input, lower=0.15, upper=0.85)
		self.outlimits, self.eno, self.deo = norms(target, lower=0.15, upper=0.85)
		numi = len(self.inno); numo = len(self.outno)
		self.ded = zeros((numo,numi), 'd')
		for o in xrange(numo): 
			for i in xrange(numi):
				self.ded[o,i] = self.eni[i,0] * self.deo[o,0]
		return normarray(input, self.eni), normarray(target, self.eno)

	def train_genetic(self, input, target, **kwargs):
		""" 
		Global weights optimization with genetic algorithm.
		
		Allowed parameters:
		lower		 - lower bound of weights values (default is -25.)
		upper		 - upper bound of weights values (default is 25.)
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
		func = netprop.prop5
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
		gtol		 - stop when norm of gradient is less than gtol
					   (default is 1e-5)
		norm		 - order of vector norm to use (default is infinity)
		maxiter		 - the maximum number of iterations (default is None)
		disp		 - print convergence message at the end of training
					   if non-zero (default is 1)
					   
		Note: this procedure does not produce any output during training.
		Note: optimization routine used here is part of scipy.optimize.
		"""
		input, target = self._setnorm(input, target)
		func = netprop.prop7
		fprime = netprop.prop6
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
		func = netprop.prop7
		fprime = netprop.prop6
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
		scale	  : scaling factors to apply to each weight (a list of floats)
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
		func = netprop.prop7
		fprime = netprop.prop6
		extra_args = (self.conec, self.bconecno, self.units, \
						   self.inno, self.outno, input, target)
		self.weights = optimize.fmin_tnc(func, self.weights.tolist(), fprime=fprime, \
										 args=extra_args, **kwargs)[-1]
		self.weights = array(self.weights)
		self.trained = 'tnc'

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

conec = [[1, 3], [2, 3], \
	     [1, 4], [2, 4], \
	     [3, 5], [4, 5]]
conec = mlgraph((2,2,1))
conec = tmlgraph((2,1,1))
#~ conec = [[1, 3], [2, 3], \
		 #~ [1, 4], [2, 4], [3, 4]]
#print conec
#~ conec = [[1, 3], [2, 3], \
	     #~ [1, 4], [2, 4], [3, 4]]
n = ffnet(conec=conec)
#n.genetic.im_func.__doc__ += pikaia.__doc__
#~ print n.conec
#~ print n.inno
#~ print n.outno
#~ print n.bconec
#~ print n.bconecno
#~ print n.units
#~ print n.weights
input = [[0.,0.], [0.,1.], [1.,0.], [1.,1.]]
target  = [[1.], [0.], [0.], [1.]]
from _ffnet import vmapa
target = vmapa(target, 0., 1., 0.15, 0.85)

#n.powell(input, target, maxiter=100)
#n.bfgs(input, target)
#n.anneal(input, target, lower = -1., upper = 1., learn_rate=0.001)
#n.genetic(input, target, lower = -5., upper = 5., individuals = 20, generations = 100)
#n.ncg(input, target, epsilon=0.0001)
#n.l_bfgs_b(input, target, iprint=1)
conec = mlgraph((2,4,2))
print conec
n = ffnet(mlp=(2,4,2))
print n.conec
print n.dconecno
from scipy import sin, pi, cos
pat = 20
#input = [[k*2*pi/pat] for k in xrange(1,pat+1)]+[[0.]]
#target = [[0.4*sin(x[0])+0.5] for x in input]

input = [[2*pi+k*2*pi/pat, k*2*pi/pat] for k in xrange(1,pat+1)]+[[2*pi,0.]]
target = [[2*sin(x[0]),5*cos(x[1])] for x in input]

#target = vmapa(target, -1., 1., 0.15, 0.85)
print n.weights
#n.genetic(input, target, lower = -20., upper = 20., individuals = 20, generations = 2000)

n.train_tnc(input, target, maxfun=5000)
#n.bfgs(input, target, iprint=1, bounds=n._getbounds())
#n.train_cg(input, target, maxiter=10000, disp=1)
print n.weights
print n.units
#n.genetic(input, target, lower = -5., upper = 5., individuals = 20, generations = 1000)
#print n.deriv([pi/6])

savenet(n, "lala")
n = loadnet("lala")


import pylab
inp = input[:-1]
inp1 = [x[0] for x in input[:-1]]
inp2 = [x[1] for x in input[:-1]]
res1 = [n(x)[0] for x in inp]
res2 = [n(x)[1] for x in inp]
#print target
#print res1
dres1 = [n.derivative(x)[0][0] for x in inp]
dres2 = [n.derivative(x)[1][0] for x in inp]
#from flagshyp import partial_derivative as pd
#res3 = [pd(n, [x], dx=0.001)[0] for x in inp]

pylab.plot(inp1, res1)
pylab.plot(inp1, dres1)
pylab.plot(inp2, res2)
pylab.plot(inp2, dres2)
#pylab.plot(inp, res3)
pylab.show()
#pylab.close()
#n.draw(biasnode=True)


#~ bounds=n._getbounds()
#~ def _getbounds(self):
	#~ """Sets bounds of weights"""
	#~ nofw = len(self.conec)
	#~ bounds = []
	#~ for w in xrange(nofw):
		#~ trg = self.conec[w,1]
		#~ n = len(self.graph.predecessors(trg))
		#~ b = 100./n
		#~ w = self.weights[w]
		#~ if 0.8*b > w: upp = b
		#~ else: upp = 1.2*w
		#~ if -0.8*b < w: low = -b
		#~ else: low = 1.2*w
		#~ bounds += [(low, upp)]
	#~ return bounds
	
	
#~ def drawnet(self, biasnode = False):
	#~ "Draws network in circular layout"
	#~ try: import pylab
	#~ except:
		#~ print "Install matplotlib first"
		#~ return
	#~ pylab.close()
	#~ pgraph = self.graph.copy()
	#~ if not biasnode: pgraph.delete_node(0)
	#~ NX.draw_circular(pgraph)
	#~ pylab.show()
	#~ return


#~ print n.weights
#~ for inp in input:
    #~ print inp, n(inp)

#~ from nn import ffnet, loadnet, savenet
#~ # network initialization possibilities
#~ n = ffnet(conec = conec)
#~ n = ffnet(file = "conecfile") #reads connections
#~ n = ffnet(mlp = arch)
#~ n = ffnet(tmlp = arch)

#~ n.train_genetic(input, target)
#~ ans = n(inp)
#~ deriv = n.derivative(inp)

#~ loadnet("filename")
#~ savenet(n, "filename")

# nn module functions: loadnet, savenet
# nn module classes: ffnet

# ffnet attributes: inlimits, outlimits, trained, conec, weights, units
# ffnet methods: call, derivative, train_*, plot


	#~ def __getattr__(self, name):
		#~ if name == 'genetic_data':
			#~ return (self.conec, self.units, self.inno, self.outno)
		#~ elif name == 'bprop_data':
			#~ return (self.conec, self.bconecno, self.units, self.inno, self.outno)
		#~ elif name == 'call_data':
			#~ return (self.weights, self.conec, self.units, \
					#~ self.inno, self.outno, self.eni, self.deo)
		#~ elif name == 'deriv_data':
			#~ return (self.weights, self.conec, self.dconecno, self.dconecmk, \
					#~ self.units, self.inno, self.outno, self.eni, self.ded)
					