# -*- coding: utf-8 -*-
########################################################################
##  Copyright (C) 2011 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################
from ffnet import ffnet, mlgraph
from scipy import rand

# Generate random training data
input = rand(10000, 10)
target = rand(10000, 1)

# Define net
conec = mlgraph((10,300,1))
net = ffnet(conec)

if __name__=='__main__':
    print "Training in single process:"
    from time import time
    t0 = time()
    net.train_tnc(input, target, nproc = 1, maxfun=50, messages=1) 
    t1 = time()
    single_time = t1-t0

    print

    from multiprocessing import cpu_count
    print "Trainig at all %s cpus:" %cpu_count()
    net.randomweights()
    t0 = time()
    net.train_tnc(input, target, nproc = 'ncpu', maxfun=50, messages=1) 
    t1 = time()
    allcpus_time = t1-t0

    print
    print 'Train time, single process:', single_time
    print 'Train time, all cpus:      ', allcpus_time

