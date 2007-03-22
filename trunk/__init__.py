'''
Feed-forward neural network for python.

Basic usage of the package is outlined below. 
See description of ffnet module and its functions 
(and especially ffnet class) for detailed explanations.

    from ffnet import ffnet, mlgraph, savenet, loadnet, exportnet
    conec = mlgraph( (2,2,1) )
    net = ffnet(conec)
    input = [ [0.,0.], [0.,1.], [1.,0.], [1.,1.] ]
    target  = [ [1.], [0.], [0.], [1.] ]
    net.train_tnc(input, target, maxfun = 1000)
    net.test(input, target, iprint = 2)
    savenet(net, "xor.net")
    exportnet(net, "xor.f")
    net = loadnet("xor.net")
    answer = net( [ 0., 0. ] )
    partial_derivatives = net.derivative( [ 0., 0. ] )

Usage examples with full description can be found in 
examples directory of the source distribution.
'''

from _version import version
import fortran
import tools
from ffnet import ffnet, \
                  mlgraph, \
                  tmlgraph, \
                  imlgraph, \
                  savenet, \
                  loadnet, \
                  exportnet
from pikaia import pikaia
from _tests import runtest as test
