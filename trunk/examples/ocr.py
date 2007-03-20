########################################################################
##  Copyright (C) 2006 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################

### Digits recognition example for ffnet ###

# The training set is contained in the file data/ocr.dat.
# The file contains 68 total patterns (first 58 are used for training 
# and last 10 are used for the test set). Data columns 1 through 64 
# contain the input node bitmap data and 64 through 74 contain the
# training targets (10 targets for 10 digits). 
# Layered network architecture is used: (64, 10, 10, 10)

from ffnet import ffnet, mlgraph

# Generate standard layered network architecture
conec = mlgraph((64,10,10,10))
# Create network
net = ffnet(conec)

# Read training data
file = open("data/ocr.dat", 'r')
from scipy.io import read_array
input_cols = tuple(range(0, 64)); target_cols = tuple(range(64, 74))
input, target = read_array(file, columns=[input_cols, target_cols])

# Train network
#train with scipy tnc optimizer
print "TRAINING NETWORK..."
##net.train_genetic(input, target, individuals=20, generations=500, lower=-1., upper=1.)
net.train_tnc(input[:58], target[:58], maxfun = 2000, messages=1)

# Test network
print
print "TESTING NETWORK..."
output, regression = net.test(input[58:], target[58:], iprint = 2)

#Make a plot of a chosen digit along with the network guess
try:
    from pylab import *
    from random import randint
    
    digitpat = randint(58, 67) #Choose testing pattern to plot
    
    subplot(211)
    imshow(input[digitpat].reshape(8,8), interpolation = 'nearest')
    
    subplot(212)
    N = 10  # number of digits / network outputs
    ind = arange(N)   # the x locations for the groups
    width = 0.35       # the width of the bars
    bar(ind, net(input[digitpat]), width, color='b') #make a plot
    xticks(ind+width/2., ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'))
    xlim(-width,N-width)
    axhline(linewidth=1, color='black')
    title("Trained network (64-10-10-10) guesses a digit above...")
    xlabel("Digit")
    ylabel("Network outputs")
   
    show()
except ImportError: 
    print "Cannot make plots. For plotting install matplotlib..."
    
print \
"""
Note:
Normalization of input/output data is handled automatically in ffnet.
Just use your raw data both at trainig and recalling phase. 
"""