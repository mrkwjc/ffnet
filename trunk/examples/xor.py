from ffnet import ffnet, mlgraph

# Generate standard layered network architecture
conec = mlgraph((2,2,1))
# Create network
net = ffnet(conec)

# Define training data
input = [[0.,0.], [0.,1.], [1.,0.], [1.,1.]]
target  = [[1.], [0.], [0.], [1.]]

# Train network
#first find good starting point with genetic algorithm (not necessary, but helpful)
net.train_genetic(input, target, individuals=20, generations=500)
#then train with scipy tnc optimizer
net.train_tnc(input, target, maxfun = 1000)

# Test network
net.test(input, target, iprint = 2)

# Save/load network
from ffnet import savenet, loadnet
print "Network is saved..."
savenet(net, "xor.net")
print "Network is reloaded..."
net = loadnet("xor.net")
print "Network is tested again..."
net.test(input, target, iprint = 2)

# Use network as a function...
print "Note:"
print "You can use the network as a python function."
print "For example calling net([1, 1]) gives %s:" % net([1, 1])
print "Ladies and gentelments, it just works!"

#initial_weights = [ 1.06887228,  1.08273479, -1.11452322, -0.0479572 , -0.80835213,
#                   -0.69700962, -0.53619104, -0.90239253, -0.04677224]
#~ conec = [[1, 3], [2, 3], \
         #~ [1, 4], [2, 4], \
         #~ [3, 5], [4, 5]]
#~ conec = mlgraph((2,2,1))
#~ conec = tmlgraph((2,1,1))
#~ conec = [[1, 3], [2, 3], \
         #~ [1, 4], [2, 4], [3, 4]]
#print conec
#~ conec = [[1, 3], [2, 3], \
         #~ [1, 4], [2, 4], [3, 4]]
#~ n = ffnet(conec=conec)
#n.genetic.im_func.__doc__ += pikaia.__doc__
#~ print n.conec
#~ print n.inno
#~ print n.outno
#~ print n.bconec
#~ print n.bconecno
#~ print n.units
#~ print n.weights
#~ input = [[0.,0.], [0.,1.], [1.,0.], [1.,1.]]
#~ target  = [[1.], [0.], [0.], [1.]]

#~ target = netprop.vmapa(target, 0., 1., 0.15, 0.85)

#~ #n.powell(input, target, maxiter=100)
#~ #n.bfgs(input, target)
#~ #n.anneal(input, target, lower = -1., upper = 1., learn_rate=0.001)
#~ #n.genetic(input, target, lower = -5., upper = 5., individuals = 20, generations = 100)
#~ #n.ncg(input, target, epsilon=0.0001)
#~ #n.l_bfgs_b(input, target, iprint=1)
#~ conec = mlgraph((2,4,2))
#~ print conec
#~ n = ffnet(mlp=(2,4,2))
#~ print n.conec
#~ print n.dconecno
#~ from scipy import sin, pi, cos
#~ pat = 20
#~ #input = [[k*2*pi/pat] for k in xrange(1,pat+1)]+[[0.]]
#~ #target = [[0.4*sin(x[0])+0.5] for x in input]

#~ input = [[2*pi+k*2*pi/pat, k*2*pi/pat] for k in xrange(1,pat+1)]+[[2*pi,0.]]
#~ target = [[2*sin(x[0]),5*cos(x[1])] for x in input]

#~ #target = vmapa(target, -1., 1., 0.15, 0.85)
#~ print n.weights
#~ #n.genetic(input, target, lower = -20., upper = 20., individuals = 20, generations = 2000)

#~ #n.train_tnc(input, target, maxfun=5000)
#~ n.train_momentum(input, target, maxiter=10000)
#~ #n.bfgs(input, target, iprint=1, bounds=n._getbounds())
#~ #n.train_cg(input, target, maxiter=10000, disp=1)
#~ print n.weights
#~ print n.units
#~ #n.genetic(input, target, lower = -5., upper = 5., individuals = 20, generations = 1000)
#~ #print n.deriv([pi/6])

#~ savenet(n, "lala")
#~ n = loadnet("lala")


#~ import pylab
#~ inp = input[:-1]
#~ inp1 = [x[0] for x in input[:-1]]
#~ inp2 = [x[1] for x in input[:-1]]
#~ res1 = [n(x)[0] for x in inp]
#~ res2 = [n(x)[1] for x in inp]
#~ #print target
#~ #print res1
#~ dres1 = [n.derivative(x)[0][0] for x in inp]
#~ dres2 = [n.derivative(x)[1][0] for x in inp]
#~ #from flagshyp import partial_derivative as pd
#~ #res3 = [pd(n, [x], dx=0.001)[0] for x in inp]

#~ pylab.plot(inp1, res1)
#~ pylab.plot(inp1, dres1)
#~ pylab.plot(inp2, res2)
#~ pylab.plot(inp2, dres2)
#~ #pylab.plot(inp, res3)
#~ pylab.show()
#~ #pylab.close()
#~ #n.draw(biasnode=True)


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
