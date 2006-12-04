########################################################################
##  Copyright (C) 2006 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################

### XOR problem example for ffnet ###

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

print "Note:"
print "You can use ffnet network as a python function."
print "For example calling net([1, 1]) gives %s:" % net([1, 1])
