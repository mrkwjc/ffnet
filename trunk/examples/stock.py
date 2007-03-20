########################################################################
##  Copyright (C) 2006 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################

### stock problem example for ffnet ###
##
## Data and description for this example is borrowed from:
## http://www.scientific-consultants.com/nnbd.html
##
## 
## The data to train the network consists of Black-Scholes option prices 
## for volatility levels running from 20 percent to 200 percent, 
## for time remaining running from 5 to 15 days, and for strike price 
## running from 70 dollars to 130 dollars. The stock price was set to 
## 100 dollars and the interest rate to 0 percent when generating 
## the data.
##
## The data is "difficult" in that, for a neural network to 
## practically emulate Black-Scholes, a very tight fit is required.
## The R-squared should be at least 0.999999 or better, and the largest
## absolute error must be less than 0.05 dollars (the price increment 
## for most options) or, better yet, less than 0.01 dollars.
##
##
## So let's try.
## Attention: training phase might be long as a big network is trained.

from ffnet import ffnet, mlgraph
from scipy.io import read_array
from numpy import array

# Generate standard layered network architecture
conec = mlgraph((3,22,12,1))
# Create network
net = ffnet(conec)

# Read training data
print "READING DATA..."
file = open('data/black-scholes.dat', 'r')
patterns = len( file.readlines() ); file.seek(0)
lins = tuple( range( 1, patterns) )
inpcols = (1, 2, 3); trgcols = (4,); cols = [ inpcols, trgcols ]
input, target = read_array(file, columns=cols, lines=lins)

print "TRAINING NETWORK..."
import sys; sys.stdout.flush() #Just to ensure dislpaing the above messages here
net.train_tnc(input, target, maxfun = 5000, messages=1)

# Test network
print
print "TESTING NETWORK..."
output, regression = net.test(input, target, iprint = 0)
Rsquared = regression[0][2]
maxerr = abs( array(output).reshape( len(output) ) - array(target) ).max()
print "R-squared:           %s  (should be >= 0.999999)" %str(Rsquared)
print "max. absolute error: %s  (should be <= 0.05)" %str(maxerr)
print
print "Is ffnet ready for stock?"

# Make plot if matplotlib is avialble
try:
    from pylab import *
    plot( target, 'b--' )
    plot( output, 'k-' )
    legend(('target', 'output'))
    xlabel('pattern'); ylabel('price')
    title('Outputs vs. target of trained network.')
    grid(True)
    show()
except ImportError: 
    print "Cannot make plots. For plotting install matplotlib..."
 