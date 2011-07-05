# -*- coding: utf-8 -*-
########################################################################
##  Copyright (C) 2011 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################
from ffnet import ffnet_multi, mlgraph
from scipy import rand

# Generate random training data
input = rand(10000, 10)
target = rand(10000, 1)

# Define net
conec = mlgraph((10,300,1))
net = ffnet_multi(conec)

from time import time
t0 = time()
net.train_tnc_multi(input, target, nproc = None, maxfun=100, messages=1) 
t1 = time()
print t1-t0