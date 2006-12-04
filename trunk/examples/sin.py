########################################################################
##  Copyright (C) 2006 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################

### Sine training example for ffnet ###

from ffnet import ffnet, mlgraph
from math import pi, sin, cos

# Let's create layered network connectivity by hand (architecture (1,4,1))
# Tip: draw network on a sheet of paper and number its nodes first. :)
# Remember that biases of nodes are handled as the connections 
# from special node numbered 0.
# Order of node numbering has no meaning. Order of links in conec is meaningless too,
# but the tuples indicating connections have to be from source to target. 

conec = [(1, 2), (1, 3), (1, 4), (1, 5), (2, 6), (3, 6), (4, 6), (5, 6), \
         (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)]

# Note1: Adding connection from 0 to 1 will cause it not to be input node any more
# therefore it is not allowed!
# Note2: The same connectivity can be obtained using mlgraph function provided with ffnet.

# Create network
net = ffnet(conec)

# Generate training data (sine values for x from 0 to 2*pi)
patterns = 16
input = [ [0.] ] + [ [k*2*pi/patterns] for k in xrange(1, patterns + 1) ]
target = [[sin(x[0])] for x in input]

# Train network
#first find good starting point with genetic algorithm (not necessary, but helpful)
net.train_genetic(input, target, individuals=20, generations=500)
#then train with scipy tnc optimizer
net.train_tnc(input, target, maxfun = 10000)

# Test network
net.test(input, target, iprint = 2)

# Make some plots
try:
    from pylab import *
    points = 128
    xaxis = [ 0. ] + [ k*2*pi/points for k in xrange(1, points + 1) ]
    sine = [ sin(x) for x in xaxis ]
    cosine = [ cos(x) for x in xaxis ]
    netsine = [ net([x]) for x in xaxis]
    netcosine = [ net.derivative([x]) for x in xaxis ]
    
    subplot(211)
    plot(xaxis, sine, 'b--', xaxis, netsine, 'k-')
    legend(('sine', 'network output'))
    grid(True)
    title('Outputs of trained network.')
    
    subplot(212)
    plot(xaxis, cosine, 'b--', xaxis, netcosine, 'k-')
    legend(('cosine', 'network derivative'))
    grid(True)
    show()
except: 
    print "Cannot make plots. For plotting install matplotlib..."

print \
"""
Note:
You have access to partial derivatives of the network
outputs vs. its inputs. For example, calling
net.derivative([3.14]) for a sine network just trained 
we obtain %s (cosine at 3.14 is -1).
""" % net.derivative([3.14])
 